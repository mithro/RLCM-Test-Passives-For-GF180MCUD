"""Capacitance of the MIM capacitors from the PDK's ngspice model, at the three MIM corners.

Run inside the rlcm-sim Docker image, from docs/sim, with the gf180mcuD PDK linked as docs/sim/pdk:

    python3 run_mim.py

Writes results/mim_pdk_model.csv.
"""
import csv
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
CORNERS = ["mimcap_typical", "mimcap_ss", "mimcap_ff"]


def main():
    template = (HERE / "tb_mim.spice.in").read_text()
    rows = []
    for corner in CORNERS:
        deck = HERE / "build" / ("tb_mim_%s.spice" % corner)
        deck.parent.mkdir(exist_ok=True)
        deck.write_text(template.replace("CORNER", corner).replace(".lib pdk/", ".lib %s/" % (HERE / "pdk")))
        out = subprocess.run(["ngspice", "-b", str(deck)], capture_output=True, text=True, check=True).stdout
        match = re.search(r"RESULT c1_pF (\S+) c2_pF (\S+)", out)
        if not match:
            raise SystemExit("no result from ngspice for %s:\n%s" % (corner, out))
        c1, c2 = (float(v) * 1e12 for v in match.groups())
        rows.append({"corner": corner, "structure_1_pF": "%.4f" % c1, "structure_2_pF": "%.4f" % c2})
        print(rows[-1])
    with open(HERE / "results" / "mim_pdk_model.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
