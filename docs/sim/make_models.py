# /// script
# dependencies = ["klayout"]
# ///
"""Write the openEMS model layouts for the RLCM capacitors and inductors.

Run from the repository root after unzipping the chip layout into build/:

    unzip -o RLCMV4_filled.zip -d build
    uv run docs/sim/make_models.py

Each model is written to docs/sim/build/<name>.gds with the top cell "model".
Only the drawn layers on datatype 0 that the stack file knows are kept, plus
the port layers 201 and above.

Inductors
    The cell is copied from the chip. As in the stand-alone file
    seperate_GDSs/Ind2_D250_N2_W26_TO.gds, a Metal5 bar is added 1 um in front
    of the terminal ends to close the ground ring, so that each port marker
    spans the 1 um gap between a terminal and ground. On the chip the ring is
    open only where the terminals pass through it, so the bar would close it
    into a loop around the winding. The ring is therefore cut, 6 um wide, on
    the side opposite the terminals, which is where the stand-alone file has
    its cut.

Capacitors
    A clip of the chip around the capacitor and the parallel parts of its two
    feed stubs. One port, on layer 201, spans the 2 um gap between the stubs at
    their lower end. Via4 cuts on the MIM top plate are moved to layer 1041, as
    the stack file's README requires: on layer 41 they would run from Metal4
    to Metal5 and short the capacitor.
"""
import pathlib
import klayout.db as kdb

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHIP = ROOT / "build" / "RLCMV4_filled.gds"
OUT = pathlib.Path(__file__).resolve().parent / "build"

# Metal1, Via1, Metal2, Via2, Metal3, Via3, Metal4, Via4, FuseTop (MIM top plate), Metal5
DRAWN = [34, 35, 36, 38, 42, 40, 46, 41, 75, 81]
METAL5, VIA4, FUSETOP, VIA_MIM = 81, 41, 75, 1041

INDUCTORS = {
    # model name: (chip cell, port layers to keep)
    "spiral_2turn": ("SpiralInductor_2P_282x282", [201, 202]),
    "spiral_4turn": ("SpiralInductor_2P_282x282$1", [201, 202]),
    "symmetric": ("SymmetricInductor_3P_282x282", [201, 202]),
}

CAPACITORS = {
    # model name: (clip box, port box), um in chip coordinates
    "mim_100x100": ((630, 340, 755, 497), (691, 340, 693, 346)),
    "mim_54x25": ((1205, 340, 1283, 422), (1243, 340, 1245, 346)),
}


def um(x1, y1, x2, y2):
    return kdb.Box(round(x1 * 1000), round(y1 * 1000), round(x2 * 1000), round(y2 * 1000))


def new_model():
    layout = kdb.Layout()
    layout.dbu = 0.001
    return layout, layout.create_cell("model")


def write(layout, name):
    OUT.mkdir(exist_ok=True)
    path = OUT / (name + ".gds")
    layout.write(str(path))
    cell = layout.cell("model")
    counts = {layout.get_info(li).layer: sum(1 for _ in cell.each_shape(li)) for li in layout.layer_indexes()}
    print("%s: bbox %s um, shapes per layer %s" % (path.relative_to(ROOT), cell.dbbox(), dict(sorted(counts.items()))))


def ground_bar(ports):
    """Metal5 bar from 1 um beyond the port markers to the cell edge, 3 um wider than the markers on each side."""
    box = ports.bbox()
    if box.width() < box.height():  # markers stacked vertically: terminals point along +x
        return um(box.right / 1000, box.bottom / 1000 - 3, 149, box.top / 1000 + 3)
    return um(box.left / 1000 - 3, -149, box.right / 1000 + 3, box.bottom / 1000)  # terminals point along -y


def ring_cut(ports):
    """6 um cut through the ground ring on the side opposite the terminals."""
    box = ports.bbox()
    if box.width() < box.height():  # terminals point along +x
        return um(-150, -3, -128, 3)
    return um(-3, 128, 3, 150)  # terminals point along -y


def main():
    chip = kdb.Layout()
    chip.read(str(CHIP))
    for name, (cellname, port_layers) in INDUCTORS.items():
        src = chip.cell(cellname)
        layout, model = new_model()
        ports = kdb.Region()
        for layer in port_layers:
            region = kdb.Region(src.begin_shapes_rec(chip.find_layer(layer, 0)))
            model.shapes(layout.layer(layer, 0)).insert(region)
            ports += region
        cut = kdb.Region(ring_cut(ports))
        for layer in DRAWN:
            li = chip.find_layer(layer, 0)
            if li is not None:
                shapes = kdb.Region(src.begin_shapes_rec(li)).merged() - cut
                model.shapes(layout.layer(layer, 0)).insert(shapes)
        model.shapes(layout.layer(METAL5, 0)).insert(ground_bar(ports))
        write(layout, name)

    top = chip.cell("RLCMV4_filled")
    for name, (clip, port) in CAPACITORS.items():
        layout, model = new_model()
        box = um(*clip)
        region = {}
        for layer in DRAWN:
            li = chip.find_layer(layer, 0)
            region[layer] = (kdb.Region(top.begin_shapes_rec_touching(li, box)) & kdb.Region(box)).merged()
        on_plate = region[VIA4].inside(region[FUSETOP])
        region[VIA_MIM] = on_plate
        region[VIA4] = region[VIA4] - on_plate
        for layer, shapes in region.items():
            model.shapes(layout.layer(layer, 0)).insert(shapes)
        model.shapes(layout.layer(201, 0)).insert(um(*port))
        write(layout, name)


if __name__ == "__main__":
    main()
