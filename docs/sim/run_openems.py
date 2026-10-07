"""Simulate one RLCM structure with openEMS through the gds2openEMS workflow.

Run inside the rlcm-sim Docker image, from the repository root, after
docs/sim/make_models.py has written the model layouts:

    python3 docs/sim/run_openems.py spiral_2turn
    python3 docs/sim/run_openems.py Ind2_D250_N2_W26_TO mur

The optional second argument selects a boundary variant (see VARIANTS). The
S-parameters are written to docs/sim/results/<model>[_<variant>].s<n>p and the
derived inductance, resistance or capacitance to the matching .csv file.
"""
import csv
import json
import os
import pathlib
import sys
import urllib.request

import numpy as np
from gds2openEMS import gds_reader, simulation_setup, stackup_reader, utilities
from openEMS import openEMS

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"
RESULTS = HERE / "results"

# Stack file by the chip's author, pinned to the commit that was used.
STACK_URL = ("https://raw.githubusercontent.com/EngGhaith/The-Silent-Owl-GF180MCU-WB-LNA/"
             "7deb253d3b96f0daf68dac80536ab2ca4f24b464/EM-Flow/OPENEMS-GF180MCUD-1P5M-TM11KA-MIMB.xml")
STACK = BUILD / "OPENEMS-GF180MCUD-1P5M-TM11KA-MIMB.xml"

# model: (GDS file, cell, [(port layer, direction)], highest frequency, port impedance)
# Every port is an in-plane lumped port on the top metal (TM, GDS layer 81).
# The capacitors use 5 ohm ports: the Z parameters do not depend on the port
# impedance, and the lower impedance shortens the RC time constant, and so the
# simulated time, tenfold.
MODELS = {
    "spiral_2turn": (BUILD / "spiral_2turn.gds", "model", [(201, "x"), (202, "x")], 20e9, 50),
    "spiral_4turn": (BUILD / "spiral_4turn.gds", "model", [(201, "x"), (202, "x")], 20e9, 50),
    "symmetric": (BUILD / "symmetric.gds", "model", [(201, "y"), (202, "y")], 20e9, 50),
    "Ind2_D250_N2_W26_TO": (HERE.parents[1] / "seperate_GDSs" / "Ind2_D250_N2_W26_TO.gds", "SpiralInductor", [(201, "x"), (202, "x")], 20e9, 50),
    "Ind3_D250_N2_W26_TO": (HERE.parents[1] / "seperate_GDSs" / "Ind3_D250_N2_W26_TO.gds", "SymmetricInductor", [(201, "y"), (202, "y")], 20e9, 50),
    "mim_100x100": (BUILD / "mim_100x100.gds", "model", [(201, "x")], 10e9, 5),
    "mim_54x25": (BUILD / "mim_54x25.gds", "model", [(201, "x")], 10e9, 5),
}

NUMFREQ = 401

# Boundary variants, used to check how much the enclosing box changes the result.
# The default encloses the model in perfect conductors 200 um from the layout.
VARIANTS = {
    "": {},
    "far": {"margin": 600},  # side walls three times as far away
    "mur": {"Boundaries": ["MUR"] * 6},  # absorbing boundaries on all six faces
}


def main(model, variant=""):
    gds, cellname, ports, fstop, z0 = MODELS[model]
    name = model + ("_" + variant if variant else "")
    BUILD.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    if not STACK.exists():
        urllib.request.urlretrieve(STACK_URL, STACK)

    settings = {
        "unit": 1e-6,
        "margin": 200,
        "fstart": 0,
        "fstop": fstop,
        "numfreq": NUMFREQ,
        "refined_cellsize": 1.0,
        "Boundaries": ["PEC"] * 6,
        "cells_per_wavelength": 20,
        "energy_limit": -50,
        "preprocess_gds": False,
        "merge_polygon_size": 1.0,
        "no_gui": True,
        "numThreads": int(os.environ.get("OPENEMS_THREADS", "0")),
        **VARIANTS[variant],
    }

    simulation_ports = simulation_setup.all_simulation_ports()
    for number, (layer, direction) in enumerate(ports, start=1):
        simulation_ports.add_port(simulation_setup.simulation_port(
            portnumber=number, voltage=1, port_Z0=z0, source_layernum=layer,
            target_layername="TM", direction=direction))

    materials_list, dielectrics_list, metals_list = stackup_reader.read_substrate(str(STACK))
    layernumbers = metals_list.getlayernumbers()
    layernumbers.extend(simulation_ports.portlayers)
    allpolygons = gds_reader.read_gds(str(gds), layernumbers, purposelist=[0], metals_list=metals_list,
                                      preprocess=settings["preprocess_gds"],
                                      merge_polygon_size=settings["merge_polygon_size"],
                                      cellname=cellname)

    sim_path = str(BUILD / (name + "_data"))
    os.makedirs(sim_path, exist_ok=True)
    settings.update(simulation_ports=simulation_ports, materials_list=materials_list,
                    dielectrics_list=dielectrics_list, metals_list=metals_list,
                    layernumbers=layernumbers, allpolygons=allpolygons,
                    sim_path=sim_path, model_basename=name)

    FDTD = openEMS(EndCriteria=10 ** (settings["energy_limit"] / 10))
    FDTD.SetGaussExcite((settings["fstart"] + fstop) / 2, (fstop - settings["fstart"]) / 2)
    FDTD.SetBoundaryCond(settings["Boundaries"])
    for number in range(1, len(ports) + 1):
        settings["excite_portnumbers"] = [number]
        simulation_setup.setupSimulation(FDTD=FDTD, settings=settings)
        simulation_setup.runSimulation(FDTD=FDTD, settings=settings)

    f = np.linspace(settings["fstart"], fstop, NUMFREQ)
    n = len(ports)
    S = np.array([[utilities.calculate_Sij(i, j, f, sim_path, simulation_ports) for j in range(1, n + 1)]
                  for i in range(1, n + 1)])
    # write_snp takes [S11] for one port and the full matrix for more.
    utilities.write_snp(S[0] if n == 1 else S, f, str(RESULTS / ("%s.s%dp" % (name, n))), z0=z0)

    # Z matrix at every frequency, then the impedance between the two terminals.
    Z = np.empty_like(S)
    for k in range(len(f)):
        Z[:, :, k] = z0 * (np.eye(n) + S[:, :, k]) @ np.linalg.inv(np.eye(n) - S[:, :, k])
    z = Z[0, 0] if n == 1 else Z[0, 0] + Z[1, 1] - Z[0, 1] - Z[1, 0]

    rows = []
    with np.errstate(divide="ignore", invalid="ignore"):
        w = 2 * np.pi * f
        for k in range(1, len(f)):
            row = {"f_GHz": f[k] / 1e9, "R_ohm": z[k].real, "X_ohm": z[k].imag}
            if n == 1:
                row["C_pF"] = -1 / (w[k] * z[k].imag) * 1e12
            else:
                row["L_nH"] = z[k].imag / w[k] * 1e9
                row["Q"] = z[k].imag / z[k].real
            rows.append(row)
    with open(RESULTS / (name + ".csv"), "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: "%.6g" % v for k, v in row.items()})
    print(json.dumps({"model": name, "at_1GHz": min(rows, key=lambda r: abs(r["f_GHz"] - 1))}, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:3])
