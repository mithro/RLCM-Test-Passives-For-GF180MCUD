# /// script
# requires-python = ">=3.10"
# dependencies = ["klayout==0.30.12", "numpy==2.5.4", "scipy==1.18.1"]
# ///
"""Free-space DC inductance of the RLCM inductors from the current distribution in the layout.

Run from the repository root after docs/sim/make_models.py:

    uv run docs/sim/dc_inductance.py

The DC current distribution comes from the resistor network of
dc_resistance.py. The inductance is the magnetic energy of that current in
free space, L = (mu0 / 4 pi) sum_ij (I_i . I_j) <1 / r_ij>, where the sum runs
over all pairs of grid cells of all five metals and <1 / r> is averaged over
the volume of both cells. The sum is a convolution and is evaluated with FFTs.

This is the quantity the hand calculation estimates: the inductance of the
drawn metal alone, with no substrate, no ground ring current and no enclosure.
The current enters and leaves at the two port markers, so the result is a
partial inductance from terminal to terminal, as for a spiral in a circuit.

The first entry is a check of the method against the closed-form partial self
inductance of a straight rectangular bar.

Writes results/dc_inductance.csv.
"""
import csv
import pathlib

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.signal import fftconvolve

import dc_resistance as dcr

HERE = pathlib.Path(__file__).resolve().parent
MU0 = 4e-7 * np.pi
# Height of the centre of each metal above the substrate (um), and its thickness, from the stack file.
Z_CENTRE = [1.505, 2.655, 3.805, 4.955, 6.72625]
THICKNESS = [m[2] for m in dcr.METALS]
NEAR = 4  # cells within which <1/r> is integrated numerically


def kernel(h, n, dz, ta, tb):
    """<1/r> between two cells of side h (m) and thicknesses ta, tb (m), for offsets up to n cells."""
    k = np.arange(-n, n + 1)
    dx, dy = np.meshgrid(k * h, k * h)
    far = 1.0 / np.sqrt(dx**2 + dy**2 + dz**2 + (h**2 / 6) + (ta**2 + tb**2) / 12)
    # Difference of two uniform positions in a cell. The two cells are sampled
    # with Gauss rules of different order, so that no pair of points coincides in
    # the self term, where 1/r is singular but integrable.
    ga, wa = leggauss(4)
    gb, wb = leggauss(5)
    u = (ga[:, None] - gb[None, :]).ravel() * h / 2
    wu = (wa[:, None] * wb[None, :]).ravel() / 4
    wz = wu
    zz = (ga[:, None] * ta / 2 - gb[None, :] * tb / 2).ravel() + dz
    out = far.copy()
    c = n
    for i in range(-NEAR, NEAR + 1):
        for j in range(-NEAR, NEAR + 1):
            x = i * h + u[:, None, None]
            y = j * h + u[None, :, None]
            r = np.sqrt(x**2 + y**2 + zz[None, None, :] ** 2)
            out[c + j, c + i] = np.einsum("a,b,c,abc->", wu, wu, wz, 1.0 / r)
    return out


def moments(potential, h):
    """Current moments (A m) per cell and layer, x and y, for 1 V between the terminals."""
    mx, my = [], []
    for k, (_, sigma, t) in enumerate(dcr.METALS):
        v = potential[k]
        g = sigma * t * 1e-6  # conductance between neighbouring square cells
        ix = np.nan_to_num(g * (v[:, :-1] - v[:, 1:]))  # current through each x face (A)
        iy = np.nan_to_num(g * (v[:-1, :] - v[1:, :]))
        # Each face current flows along a length h; share it between the two cells.
        cx = np.zeros_like(v); cx[:, :-1] += ix * h / 2; cx[:, 1:] += ix * h / 2
        cy = np.zeros_like(v); cy[:-1, :] += iy * h / 2; cy[1:, :] += iy * h / 2
        mx.append(cx); my.append(cy)
    return mx, my


def inductance(mx, my, h, current):
    ny, nx = mx[0].shape
    n = max(nx, ny)
    energy = 0.0
    for a in range(len(mx)):
        for b in range(len(mx)):
            dz = (Z_CENTRE[a] - Z_CENTRE[b]) * 1e-6
            K = kernel(h, n, dz, THICKNESS[a] * 1e-6, THICKNESS[b] * 1e-6)
            ax = fftconvolve(mx[b], K, mode="same")
            ay = fftconvolve(my[b], K, mode="same")
            energy += np.sum(mx[a] * ax) + np.sum(my[a] * ay)
    return MU0 / (4 * np.pi) * energy / current**2


def bar_check(h_um=1.0):
    """Straight bar on all five metals, 250 um x 26 um, against Rosa's formula for a rectangular bar."""
    length, width = 250e-6, 26e-6
    h = h_um * 1e-6
    nx, ny = int(round(length / h)), int(round(width / h))
    mx = [np.full((ny, nx), 0.0) for _ in dcr.METALS]
    my = [np.zeros((ny, nx)) for _ in dcr.METALS]
    weights = np.array([s * t for _, s, t in dcr.METALS])
    weights /= weights.sum()
    for k in range(len(mx)):
        mx[k][:, :] = weights[k] / ny * h  # 1 A in total, split by conductance, moment I dl per cell
    numeric = inductance(mx, my, h, 1.0)
    thick = (Z_CENTRE[-1] + THICKNESS[-1] / 2 - Z_CENTRE[0] + THICKNESS[0] / 2) * 1e-6
    rosa = MU0 * length / (2 * np.pi) * (np.log(2 * length / (width + thick)) + 0.5 + 0.2235 * (width + thick) / length)
    return numeric, rosa


def main():
    dcr.check_inputs()
    rows = []
    numeric, rosa = bar_check()
    rows.append({"model": "check: straight bar 250 um x 26 um", "L_nH_1um_grid": "%.4f" % (numeric * 1e9),
                 "L_nH_0p5um_grid": "", "reference_nH": "%.4f" % (rosa * 1e9)})
    print(rows[-1])
    for name, (path, cellname, ports, direction) in dcr.MODELS.items():
        values = {}
        for h_um in (1.0, 0.5):
            r, potential, h = dcr.resistance(path, cellname, ports, direction, h_um, fields=True)
            mx, my = moments(potential, h)
            values[h_um] = inductance(mx, my, h, 1.0 / r)
        rows.append({"model": name, "L_nH_1um_grid": "%.4f" % (values[1.0] * 1e9),
                     "L_nH_0p5um_grid": "%.4f" % (values[0.5] * 1e9), "reference_nH": ""})
        print(rows[-1])
    with open(HERE / "results" / "dc_inductance.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
