# /// script
# dependencies = ["matplotlib", "numpy"]
# ///
"""Plot the openEMS results against the hand calculations.

Run from the repository root after the simulations:

    uv run docs/sim/plot_results.py

Writes docs/img/sim_inductors.png, docs/img/sim_capacitors.png and
docs/sim/results/summary.csv. The free-space values come from
results/dc_inductance.csv, written by dc_inductance.py.
"""
import csv
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "results"
IMG = HERE.parent / "img"

SURFACE, TEXT, TEXT_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
CHIP, STANDALONE, HAND = "#2a78d6", "#eb6834", "#52514e"

# (title, chip model, stand-alone model or None, hand calculation)
INDUCTORS = [
    ("Structure 10, spiral, two turns", "spiral_2turn", "Ind2_D250_N2_W26_TO", 1.30),
    ("Structure 8, spiral, four turns", "spiral_4turn", None, 2.13),
    ("Structure 9, symmetric, two turns", "symmetric", "Ind3_D250_N2_W26_TO", 1.30),
]
CAPACITORS = [
    ("Structure 1, MIM 100 µm × 100 µm", "mim_100x100", 20.0),
    ("Structure 2, MIM 54 µm × 25 µm", "mim_54x25", 2.70),
]


def load(model, column, fmax, fmin=0.1):
    """Values from fmin to fmax (GHz). Below 0.1 GHz the simulated time is too short."""
    with open(RESULTS / (model + ".csv")) as fh:
        rows = [r for r in csv.DictReader(fh) if fmin <= float(r["f_GHz"]) <= fmax]
    return [float(r["f_GHz"]) for r in rows], [float(r[column]) for r in rows]


def style(ax, title, ylabel):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, color=TEXT, fontsize=10, loc="left")
    ax.set_xlabel("Frequency (GHz)", color=TEXT_2, fontsize=9)
    ax.set_ylabel(ylabel, color=TEXT_2, fontsize=9)
    ax.grid(color=GRID, linewidth=0.8)
    ax.tick_params(colors=TEXT_2, labelsize=8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)


def ref_line(ax, value, name, dash):
    ax.axhline(value, color=HAND, linestyle=dash, linewidth=1.2, label=name[0].upper() + name[1:])


def hand_line(ax, value):
    ref_line(ax, value, "hand calculation", (0, (4, 3)))


def summarise():
    """Write results/summary.csv: the values quoted in the READMEs.

    Inductance and resistance are read at 0.2 GHz, where they have settled to
    their low-frequency values. Capacitance is read at 0.3 GHz, on the flat part
    of the curve below the rise caused by the feed stubs. The lowest frequency
    points are not used, because the simulated time is too short to resolve them.
    """
    rows = []
    for csv_path in sorted(RESULTS.glob("*.csv")):
        model = csv_path.stem
        if model in ("summary", "mim_pdk_model") or model.startswith("dc_"):
            continue
        with open(csv_path) as fh:
            data = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(fh)]
        if "L_nH" in data[0]:
            at = min(data, key=lambda r: abs(r["f_GHz"] - 0.2))
            peak = max(data, key=lambda r: r["Q"])
            rows.append({"model": model, "L_nH": "%.3f" % at["L_nH"], "R_ohm": "%.3f" % at["R_ohm"],
                         "Q_peak": "%.1f" % peak["Q"], "f_Q_peak_GHz": "%.1f" % peak["f_GHz"], "C_pF": ""})
        else:
            at = min(data, key=lambda r: abs(r["f_GHz"] - 0.3))
            rows.append({"model": model, "L_nH": "", "R_ohm": "", "Q_peak": "", "f_Q_peak_GHz": "",
                         "C_pF": "%.3f" % at["C_pF"]})
    with open(RESULTS / "summary.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row)


def main():
    summarise()
    with open(RESULTS / "dc_inductance.csv") as fh:
        free_space = {r["model"]: float(r["L_nH_0p5um_grid"]) for r in csv.DictReader(fh) if r["L_nH_0p5um_grid"]}
    fmax = 10
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), facecolor=SURFACE, sharey=True)
    for ax, (title, chip, standalone, hand) in zip(axes, INDUCTORS):
        f, l = load(chip, "L_nH", fmax)
        ax.plot(f, l, color=CHIP, linewidth=2, label="openEMS, cell from the chip layout")
        if standalone:
            f, l = load(standalone, "L_nH", fmax)
            ax.plot(f, l, color=STANDALONE, linewidth=2, linestyle=(0, (8, 2, 2, 2)),
                    label="openEMS, stand-alone GDS file")
        hand_line(ax, hand)
        ref_line(ax, free_space[chip], "free-space DC solver", (0, (1, 2)))
        style(ax, title, "Inductance (nH)" if ax is axes[0] else "")
        ax.set_xlim(0, fmax)
        ax.set_ylim(0, 3.5)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, fontsize=9, labelcolor=TEXT)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(IMG / "sim_inductors.png", dpi=150, facecolor=SURFACE)

    fmax = 2
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.6), facecolor=SURFACE)
    for ax, (title, model, hand) in zip(axes, CAPACITORS):
        f, c = load(model, "C_pF", fmax)
        ax.plot(f, c, color=CHIP, linewidth=2, label="openEMS, clip of the chip layout")
        hand_line(ax, hand)
        style(ax, title, "Capacitance (pF)")
        ax.set_xlim(0, fmax)
        ax.set_ylim(hand * 0.9, hand * 1.15)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False, fontsize=9, labelcolor=TEXT)
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    fig.savefig(IMG / "sim_capacitors.png", dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    main()
