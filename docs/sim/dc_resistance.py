# /// script
# dependencies = ["klayout", "numpy", "scipy"]
# ///
"""DC resistance of the RLCM inductors from a resistor network built on the layout.

Run from the repository root after docs/sim/make_models.py:

    uv run docs/sim/dc_resistance.py

Each of Metal1 to Metal5 is rasterised on a square grid. Neighbouring cells of
one layer are joined by the sheet resistance, and cells of adjacent layers by
the via resistance wherever a via array covers them. A voltage is applied
between the two terminals at the port markers and the current gives the
resistance. The material values are those of the stack file used for openEMS,
so this is an independent check of the openEMS result with the same physical
model, without the time-domain solution.

R_return_ohm is the resistance of the ground bar between the two port
references. The openEMS ports return the differential current through it, so
the openEMS resistance is to be compared with R_with_return_ohm.

Writes results/dc_resistance.csv.
"""
import csv
import pathlib

import klayout.db as kdb
import numpy as np
import scipy.sparse as sp
import scipy.sparse.csgraph as csgraph
import scipy.sparse.linalg as spla

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

# Stack file OPENEMS-GF180MCUD-1P5M-TM11KA-MIMB.xml: conductivity (S/m) and thickness (um).
METALS = [(34, 20202020.20, 0.55), (36, 20202020.20, 0.55), (42, 20202020.20, 0.55),
          (46, 20202020.20, 0.55), (81, 20964360.58, 1.1925)]
VIAS = [(35, 1972386.58, 0.60), (38, 1972386.58, 0.60), (40, 1972386.58, 0.60), (41, 2958579.88, 0.90)]
MERGE = 1.0  # um, via cuts closer than this form one block, as in gds2openEMS

# model: (GDS file, cell, port layers, port direction)
MODELS = {
    "Ind2_D250_N2_W26_TO": (ROOT / "seperate_GDSs" / "Ind2_D250_N2_W26_TO.gds", "SpiralInductor", (201, 202), "x"),
    "Ind3_D250_N2_W26_TO": (ROOT / "seperate_GDSs" / "Ind3_D250_N2_W26_TO.gds", "SymmetricInductor", (201, 202), "y"),
    "spiral_2turn": (HERE / "build" / "spiral_2turn.gds", "model", (201, 202), "x"),
    "spiral_4turn": (HERE / "build" / "spiral_4turn.gds", "model", (201, 202), "x"),
    "symmetric": (HERE / "build" / "symmetric.gds", "model", (201, 202), "y"),
}


def raster(region, box, h, nx, ny):
    """Fraction of each grid cell covered by the region."""
    origin = kdb.Point(box.left, box.bottom)
    step = kdb.Vector(h, h)
    area = np.array(region.rasterize(origin, step, nx, ny), dtype=float)  # [iy][ix]
    return area / float(h * h)


def resistance(path, cellname, port_layers, direction, h_um, side="terminal", fields=False):
    """Resistance between the Metal5 cells beside the two port markers.

    side="terminal" takes the cells on the winding side, which gives the winding
    resistance. side="reference" takes the cells on the far side of the 1 um gap,
    which gives the resistance of the ground return between the two ports.
    With fields=True, also returns the potential of every metal cell (NaN where
    there is no metal) for 1 V between the electrodes, and the grid pitch in m.
    """
    shift = 0 if side == "terminal" else 1
    ly = kdb.Layout()
    ly.read(str(path))
    cell = ly.cell(cellname)
    h = round(h_um / ly.dbu)
    box = cell.bbox().enlarged(2 * h)
    nx, ny = box.width() // h + 1, box.height() // h + 1
    rec = lambda layer: kdb.Region(cell.begin_shapes_rec(ly.layer(layer, 0))).merged()

    metal = [raster(rec(l), box, h, nx, ny) > 0.5 for l, _, _ in METALS]
    d = round(MERGE / 2 / ly.dbu)
    vias = [raster(rec(l).sized(d).merged().sized(-d), box, h, nx, ny) for l, _, _ in VIAS]

    index = -np.ones((len(METALS), ny, nx), dtype=np.int64)
    count = 0
    for k, mask in enumerate(metal):
        n = int(mask.sum())
        index[k][mask] = np.arange(count, count + n)
        count += n

    rows, cols, vals = [], [], []

    def connect(a, b, g):
        ok = (a >= 0) & (b >= 0)
        rows.append(a[ok]); cols.append(b[ok]); vals.append(np.broadcast_to(g, a.shape)[ok])

    for k, (_, sigma, t) in enumerate(METALS):
        g = sigma * t * 1e-6  # 1 / sheet resistance; square cells
        connect(index[k][:, :-1], index[k][:, 1:], g)
        connect(index[k][:-1, :], index[k][1:, :], g)
    for k, (_, sigma, t) in enumerate(VIAS):
        g = sigma * vias[k] * (h_um * 1e-6) ** 2 / (t * 1e-6)
        connect(index[k], index[k + 1], g)

    r, c, v = np.concatenate(rows), np.concatenate(cols), np.concatenate(vals)
    G = sp.coo_matrix((np.concatenate([v, v]), (np.concatenate([r, c]), np.concatenate([c, r]))), shape=(count, count)).tocsr()

    # Electrodes: the Metal5 cells on one side of each port marker.
    electrodes = []
    for layer in port_layers:
        marker = rec(layer).bbox()
        if direction == "x":
            ix = (marker.left - box.left) // h - 1 if not shift else (marker.right - box.left) // h
            iy0, iy1 = (marker.bottom - box.bottom) // h, (marker.top - box.bottom) // h
            nodes = index[-1][iy0:iy1, ix]
        else:
            iy = (marker.top - box.bottom) // h + 1 if not shift else (marker.bottom - box.bottom) // h - 1
            ix0, ix1 = (marker.left - box.left) // h, (marker.right - box.left) // h
            nodes = index[-1][iy, ix0:ix1]
        electrodes.append(nodes[nodes >= 0])

    # Keep only the network that the first terminal belongs to.
    _, label = csgraph.connected_components(G, directed=False)
    keep = label == label[electrodes[0][0]]
    if not keep[electrodes[1]].all():
        raise SystemExit("%s: the %s electrodes are not connected" % (path.name, side))
    G = G[keep][:, keep]
    new = -np.ones(count, dtype=np.int64)
    new[keep] = np.arange(int(keep.sum()))
    e1, e2 = new[electrodes[0]], new[electrodes[1]]

    L = sp.diags(np.asarray(G.sum(axis=1)).ravel()) - G
    fixed = np.zeros(G.shape[0], dtype=bool)
    fixed[e1] = fixed[e2] = True
    V = np.zeros(G.shape[0])
    V[e1] = 1.0
    free = ~fixed
    rhs = -L[free][:, fixed] @ V[fixed]
    V[free] = spla.spsolve(L[free][:, free].tocsc(), rhs)
    current = (L @ V)[e1].sum()
    if not fields:
        return 1.0 / current
    full = np.full(count, np.nan)
    full[keep] = V
    potential = np.where(index >= 0, full[np.maximum(index, 0)], np.nan)
    return 1.0 / current, potential, h_um * 1e-6


def main():
    rows = []
    for name, (path, cellname, ports, direction) in MODELS.items():
        if not path.exists():
            print("%s: %s not found, skipped" % (name, path))
            continue
        coarse = resistance(path, cellname, ports, direction, 1.0)
        fine = resistance(path, cellname, ports, direction, 0.5)
        ground = resistance(path, cellname, ports, direction, 0.5, side="reference")
        rows.append({"model": name, "R_dc_ohm_1um_grid": "%.4f" % coarse, "R_dc_ohm_0p5um_grid": "%.4f" % fine,
                     "R_return_ohm": "%.4f" % ground, "R_with_return_ohm": "%.4f" % (fine + ground)})
        print(rows[-1])
    with open(HERE / "results" / "dc_resistance.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
