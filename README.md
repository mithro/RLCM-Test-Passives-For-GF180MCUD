# RLCM: Test Passives for GF180MCUD

RLCM is a test chip of on-chip passives in the open-source
[GF180MCU](https://gf180mcu-pdk.readthedocs.io/) process, taped out on the
[wafer.space](https://wafer.space/) GF180MCU Run 2 shuttle. It was designed by
Ghaith Al Sabagh
([Institute for Communications Engineering and RF-Systems](https://www.jku.at/en/institute-for-communications-engineering-and-rf-systems/),
Johannes Kepler University Linz). The project description on wafer.space reads:

> This TO aims to have a kind of test passives to verify the automated openEMS
> flow used to simulate passives on GF180MCUD.

The die carries two MIM capacitors, two spiral inductors, a symmetric inductor,
two transformers, and the open, joined and thru structures needed to remove
the pads and feed lines from a measurement. Every structure has its own
ground-signal probe launch and nothing on the die needs a supply. Measured
S-parameters of these structures can be compared one to one with an
electromagnetic (EM) simulation of the same GDS, which tells you how far the
simulation setup for this process can be trusted before you rely on it for a
real RF design.

## Status

Silicon is expected back in November 2026. No measurements exist yet.

| Property | Value |
|---|---|
| Shuttle | wafer.space GF180MCU Run 2, shuttle ID G802 |
| Project code | `RLCM` |
| Manufacturing ID | `G802RLCM` |
| Project list entry | "RLCM: Test Passives For GF180MCUD" in [wafer-space/ws-run2](https://github.com/wafer-space/ws-run2) |
| Status on wafer.space | Manufacturable |
| Created | 2026-07-13 |
| Submitted | 2026-07-15 |
| Slot | 0.5&nbsp;×&nbsp;1, half width. Listed on wafer.space as 1.94&nbsp;mm&nbsp;×&nbsp;5.07&nbsp;mm (9.84&nbsp;mm²) |
| Packaging | Chip on board (CoB) |
| Process | GF180MCU, `gf180mcuD` PDK variant (five metal layers) |
| Submitted layout | [`RLCMV4_filled.zip`](RLCMV4_filled.zip), top cell `RLCMV4_filled` |
| Die size in the layout | 1936&nbsp;µm&nbsp;×&nbsp;5122&nbsp;µm |
| License | [CERN-OHL-P v2](LICENSE) |

## The whole chip

![Layout of the whole die with the thirteen items numbered](docs/img/die.png)

*The numbers match the [index](#index-of-structures) below. Only the five
routing metals, the MIM top plate, the pad openings and the EM port markers
are drawn.*

![Every pad opening on the die, coloured by its role](docs/img/pad_map.png)

*All 246 pad openings. The small numbers around the edge are the 72 frame
pads, counted counterclockwise from the lower left. The pad tables are in
[`docs/README.md`](docs/README.md#pads).*

## Index of structures

Size is the bounding box of the layout cell as placed and origin is its
lower left corner, both in the coordinates of the top cell.

| # | Structure | Layout cell | Size (µm) | Origin (µm) | Full details |
|---|---|---|---|---|---|
| [^1] | MIM capacitor, large | `cap_mim` | 101.2&nbsp;×&nbsp;101.2 | 641.4,&nbsp;384.3 | [MIM capacitors](docs/README.md#mim-capacitors) |
| [^2] | MIM capacitor, small | `cap_mim$1` | 55.2&nbsp;×&nbsp;26.2 | 1216.4,&nbsp;384.3 | [MIM capacitors](docs/README.md#mim-capacitors) |
| [^3] | Transformer, one turn per winding | `SymmetricTransformer` | 298&nbsp;×&nbsp;298 | 819,&nbsp;664 | [Transformers](docs/README.md#transformers) |
| [^4] | Three-line thru | three Metal5 rectangles in the top cell | 990&nbsp;×&nbsp;82 | 473,&nbsp;1532 | [De-embedding structures](docs/README.md#de-embedding-structures) |
| [^5] | Transformer, two turns per winding | `SymmetricTransformer$2` | 298&nbsp;×&nbsp;298 | 819,&nbsp;2184 | [Transformers](docs/README.md#transformers) |
| [^6] | Three-port launch, signals joined | `Probes_3P$2$1$2$1` | 447&nbsp;×&nbsp;676 | 26,&nbsp;2755 | [De-embedding structures](docs/README.md#de-embedding-structures) |
| [^7] | Three-port launch, signals open | `Probes_3P$2$2$1$1` | 447&nbsp;×&nbsp;676 | 1463,&nbsp;2755 | [De-embedding structures](docs/README.md#de-embedding-structures) |
| [^8] | Spiral inductor, four turns | `SpiralInductor_2P_282x282$1` | 298&nbsp;×&nbsp;298 | 1284.7,&nbsp;3628 | [Spiral inductors](docs/README.md#spiral-inductors) |
| [^9] | Symmetric inductor with centre tap | `SymmetricInductor_3P_282x282` | 298&nbsp;×&nbsp;298 | 462,&nbsp;4160 | [Symmetric inductor](docs/README.md#symmetric-inductor), [`seperate_GDSs/`](seperate_GDSs/README.md#symmetric-inductor) |
| [^10] | Spiral inductor, two turns | `SpiralInductor_2P_282x282` | 298&nbsp;×&nbsp;298 | 1284.7,&nbsp;4236 | [Spiral inductors](docs/README.md#spiral-inductors), [`seperate_GDSs/`](seperate_GDSs/README.md#spiral-inductor) |
| [^11] | Two-port launch, signals joined | `Probes_2P_DEEMD$1` | 524&nbsp;×&nbsp;338.3 | 430,&nbsp;4757.7 | [De-embedding structures](docs/README.md#de-embedding-structures) |
| [^12] | Two-port launch, signals open | `Probes_2P_DEEMD` | 524&nbsp;×&nbsp;338.3 | 982,&nbsp;4757.7 | [De-embedding structures](docs/README.md#de-embedding-structures) |
| [^13] | Unconnected bond pads | three of `Bondpad_5LM` | 68&nbsp;×&nbsp;369.3 | 26,&nbsp;3515 | [Pads](docs/README.md#pads) |

[^1]: MIM capacitor with a 100 µm × 100 µm top plate, connected in series between the two signal pads of a two-port launch.
[^2]: MIM capacitor with a 54 µm × 25 µm top plate, connected in series between the two signal pads of a two-port launch.
[^3]: Two interleaved single-turn windings on two rings of 26 µm track. Three-port launches on the left and right.
[^4]: Three parallel Metal5 lines, 990 µm long, that join the three signal pads of the left launch straight to those of the right launch.
[^5]: Two interleaved two-turn windings on four rings of 24 µm track. Three-port launches on the left and right.
[^6]: A three-port launch on its own, with the three signal stubs joined by a Metal5 bar.
[^7]: A three-port launch on its own, with the three signal stubs left open.
[^8]: Square spiral, four turns of 26 µm track wound to the centre, on a two-port launch.
[^9]: Square symmetric inductor, two turns of 26 µm track with one crossover and a centre tap, on a three-port launch.
[^10]: Square spiral, two turns of 26 µm track around a 142 µm opening, on a two-port launch.
[^11]: A two-port launch on its own, with the two signal stubs joined.
[^12]: A two-port launch on its own, with the two signal stubs left open.
[^13]: Three frame pads on the left edge that connect to nothing.

Where to find things:

| Location | Contents |
|---|---|
| [`RLCMV4_filled.zip`](RLCMV4_filled.zip) | The submitted layout as one GDS file, with dummy fill and seal ring |
| [`seperate_GDSs/`](seperate_GDSs/README.md) | Stand-alone GDS files of two of the inductors and of the two pad frames |
| [`docs/README.md`](docs/README.md) | Full details of every structure in the submitted layout, and the pad tables |
| [`docs/scripts/expected_values.py`](docs/scripts/expected_values.py) | The hand calculations behind the expected values quoted below |
| [`docs/updating-images.md`](docs/updating-images.md) | How to regenerate the pictures in this documentation |

## Probe launches

Every structure is reached through a probe launch at the die edge. A launch
repeats the same pads on several rows at different pitches, so one structure
can be probed with whichever probe is at hand or wire bonded from the frame
row.

| Launch | Layout cells | Pad order | Used by |
|---|---|---|---|
| Two-port | `Probes_2P`, `Probes_2P_DEEMD` | G S1 S2 G | [^1] [^2] [^8] [^10] [^11] [^12] |
| Three-port | `Probes_3P` | G S1 S2 S3 G | [^3] [^4] [^5] [^6] [^7] [^9] |

| Row | Pitch (µm) | Pads in a two-port launch | Pads in a three-port launch |
|---|---|---|---|
| Frame row, 58 µm from the die edge | 138 on the top and bottom edges, 152 on the left and right edges | G S1 S2 G | G S1 S2 S3 G |
| Second row, 168 µm in | 125 | G S1 S2 G | G S1 S2 S3 G |
| Third row, 278 µm in | 100 in a two-port launch, 125 in a three-port launch | G S1 S2 G | G S1 S3 G |
| Fourth row, 388 µm in | 100 | none | G S1 S2 S3 G |

![Pad rows of a two-port launch](docs/img/launch_2port.png)

![Pad rows of a three-port launch](docs/img/launch_3port.png)

All pad openings are 60 µm × 60 µm. The names G, S1, S2 and S3 are used
only in this documentation, because the layout has no pin labels. S1 is the
signal pad with the lowest x or y coordinate. Full details and the pad tables:
[`docs/README.md`](docs/README.md#probe-launches).

## MIM capacitors

![The two MIM capacitors on their launches](docs/img/mim_capacitors.png)

Two metal-insulator-metal capacitors between Metal4 (bottom plate) and
Metal5 (top plate, through the MIM top plate layer). Each is a series
element: S1 goes to the bottom plate and S2 to the top plate.

| # | Top plate (µm) | Area (µm²) | Expected capacitance |
|---|---|---|---|
| [^1] | 100&nbsp;×&nbsp;100 | 10000 | 20 pF (18 pF to 22 pF) |
| [^2] | 54&nbsp;×&nbsp;25 | 1350 | 2.7 pF (2.43 pF to 2.97 pF) |

| Step | How |
|---|---|
| Probing | Two-port launches on the bottom edge, G S1 S2 G. |
| Measuring | Two-port S-parameters, then remove the launch using the open and joined launches [^12] and [^11], which use the same launch cell. Convert to Y-parameters. The series capacitance is `-Im(Y21) / (2πf)` well below self-resonance. |
| Expected value | Area times the 2.0 fF/µm² (1.8 to 2.2) that the [PDK lists](https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_6_4.html) for its densest MIM option, which is the value the `gf180mcuD` tooling assumes. No EM simulation result is recorded in this repository. |

Full details: [`docs/README.md`](docs/README.md#mim-capacitors).

Further reading:

1. G. Al Sabagh, [EM stack files for GF180MCUD](https://github.com/EngGhaith/The-Silent-Owl-GF180MCU-WB-LNA/tree/main/EM-Flow), with notes on how the MIM layers must be prepared for simulation.
2. GF180MCU PDK documentation, [MIM capacitor electrical specification](https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_6_4.html) and [MIM option B layout rules](https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_10_4_2.html).

## Spiral inductors

| Two turns [^10] | Four turns [^8] |
|---|---|
| ![Two-turn spiral inductor](docs/img/spiral_2turn.png) | ![Four-turn spiral inductor](docs/img/spiral_4turn.png) |

Two square spirals with the same 250 µm outline, 26 µm track and 2 µm
spacing. All five metals are stacked and tied together with via arrays along
the winding. The inner end comes back out underneath the turns on Metal1 and
Metal2.

| # | Turns | Inner opening (µm) | Expected inductance | Expected DC resistance |
|---|---|---|---|---|
| [^10] | 2 | 142 | 1.3 nH | 0.8 Ω |
| [^8] | 4 | 30 | 2.1 nH | 1.2 Ω |

| Step | How |
|---|---|
| Probing | Two-port launches on the right edge, G S1 S2 G. S1 is the inner end of the spiral and S2 the outer end. |
| Measuring | Two-port S-parameters, de-embed, convert to Y-parameters. The usual figures are `L = Im(1/Y11) / (2πf)` and `Q = Im(1/Y11) / Re(1/Y11)` with port 2 grounded, or the same from `-1/Y21` for the series branch. |
| Expected values | The inductance is from the current sheet expression of Mohan et al. and the resistance from the PDK sheet resistances. Both are hand calculations that ignore the substrate, the ground ring and the underpass. Quality factor and self-resonance need the EM simulation, and no simulation result is recorded in this repository. |

Full details: [`docs/README.md`](docs/README.md#spiral-inductors). The
two-turn spiral is also available on its own in
[`seperate_GDSs/`](seperate_GDSs/README.md#spiral-inductor).

Further reading:

1. V. Mühlhaus, [gds2openEMS](https://github.com/VolkerMuehlhaus/gds2openEMS), the GDS to openEMS workflow, with inductor examples.
2. S. S. Mohan, M. del Mar Hershenson, S. P. Boyd and T. H. Lee, "Simple accurate expressions for planar spiral inductances", IEEE J. Solid-State Circuits, vol. 34, no. 10, pp. 1419-1424, 1999. [doi:10.1109/4.792620](https://doi.org/10.1109/4.792620)
3. C. P. Yue and S. S. Wong, "Physical modeling of spiral inductors on silicon", IEEE Trans. Electron Devices, vol. 47, no. 3, pp. 560-568, 2000. [doi:10.1109/16.824729](https://doi.org/10.1109/16.824729)
4. A. M. Niknejad and R. G. Meyer, "Analysis, design, and optimization of spiral inductors and transformers for Si RF ICs", IEEE J. Solid-State Circuits, vol. 33, no. 10, pp. 1470-1481, 1998. [doi:10.1109/4.720393](https://doi.org/10.1109/4.720393)

## Symmetric inductor

![Symmetric inductor with centre tap](docs/img/symmetric_inductor.png)

A square two-turn differential inductor [^9] with the same 250 µm outline,
26 µm track and 2 µm spacing as the spirals. The two turns swap places at
one crossover, where one path stays on Metal3 to Metal5 and the other drops to
Metal1 and Metal2. The centre tap is brought out between the two ends.

| Step | How |
|---|---|
| Probing | Three-port launch on the left edge, G S1 S2 S3 G. S1 and S3 are the two ends and S2 is the centre tap. |
| Measuring | Three-port S-parameters, or a two-port measurement on S1 and S3 using the third pad row, which has no S2 pad. The differential inductance is `Im(Zdiff) / (2πf)` with `Zdiff = Z11 + Z22 - Z12 - Z21` between the two ends. Remove the launch using [^6] and [^7]. |
| Expected value | About 1.3 nH end to end from the same hand calculation as the two-turn spiral, which does not model the crossover or the centre tap. No EM simulation result is recorded in this repository. |

Full details: [`docs/README.md`](docs/README.md#symmetric-inductor). The
inductor is also available on its own in
[`seperate_GDSs/`](seperate_GDSs/README.md#symmetric-inductor).

Further reading:

1. V. Mühlhaus, [gds2openEMS](https://github.com/VolkerMuehlhaus/gds2openEMS), the GDS to openEMS workflow.
2. J. R. Long and M. A. Copeland, "The modeling, characterization, and design of monolithic inductors for silicon RF IC's", IEEE J. Solid-State Circuits, vol. 32, no. 3, pp. 357-369, 1997. [doi:10.1109/4.557634](https://doi.org/10.1109/4.557634)

## Transformers

| One turn per winding [^3] | Two turns per winding [^5] |
|---|---|
| ![Transformer with one turn per winding](docs/img/transformer_1turn.png) | ![Transformer with two turns per winding](docs/img/transformer_2turn.png) |

Two transformers, each made of two interleaved windings with crossovers. Both
sit in the middle of the die between a three-port launch on the left and one
on the right, joined by three Metal5 feed lines on each side.

![Transformer 3 between its two launches](docs/img/transformer_row.png)

| # | Rings | Track (µm) | Left launch | Right launch |
|---|---|---|---|---|
| [^3] | 2 | 26 | S1 and S3: ends of winding A. S2: centre tap of winding B | S1 and S3: ends of winding B. S2: centre tap of winding A |
| [^5] | 4 | 24 | S1 and S3: ends of winding A. S2: centre tap of winding A | S1 and S3: ends of winding B. S2: centre tap of winding B |

| Step | How |
|---|---|
| Probing | Three-port launches on the left and right edges, six signal pads in total. |
| Measuring | A full characterisation is a six-port measurement. With a four-port analyser, measure the four winding ends on the third pad row of each launch, which has no S2 pad, and leave the centre taps open. Remove the launches and feed lines using [^4], [^6] and [^7]. Winding inductances come from `Im(Z)` of each winding, and the coupling factor from `k = Im(Z21) / sqrt(Im(Z11) Im(Z22))` with each winding treated as one differential port. |
| Expected values | Not yet recorded. No closed-form estimate is given here because none of the simple expressions covers interleaved windings. This is the structure where the EM simulation matters most. |

Full details: [`docs/README.md`](docs/README.md#transformers).

Further reading:

1. V. Mühlhaus, [gds2palace](https://github.com/VolkerMuehlhaus/gds2palace_ihp_sg13g2), the GDS to Palace workflow, with multi-port examples.
2. J. R. Long, "Monolithic transformers for silicon RF IC design", IEEE J. Solid-State Circuits, vol. 35, no. 9, pp. 1368-1382, 2000. [doi:10.1109/4.868049](https://doi.org/10.1109/4.868049)
3. A. M. Niknejad and R. G. Meyer, "Analysis, design, and optimization of spiral inductors and transformers for Si RF ICs", IEEE J. Solid-State Circuits, vol. 33, no. 10, pp. 1470-1481, 1998. [doi:10.1109/4.720393](https://doi.org/10.1109/4.720393)

## De-embedding structures

A measurement of any structure above includes its pads and feed lines. These
five structures are the launches on their own, so that their contribution can
be measured and removed.

| # | Launch | Signal pads | Picture |
|---|---|---|---|
| [^11] | Two-port | S1 joined to S2 | below, left |
| [^12] | Two-port | open | below, right |
| [^6] | Three-port | S1, S2 and S3 joined | second picture, left |
| [^7] | Three-port | open | second picture, right |
| [^4] | Three-port, both sides | S1 to S1, S2 to S2 and S3 to S3 through 990 µm lines | third picture |

![Two-port launches with the signals joined and open](docs/img/open_short_2port.png)

![Three-port launches with the signals joined and open](docs/img/open_short_3port.png)

![Three-line thru between two three-port launches](docs/img/thru_3port.png)

| Step | How |
|---|---|
| Probing | Exactly as the structure being de-embedded. |
| Measuring | Measure these with the same calibration and probe placement as the device, then apply an open-short or thru-based method from the reading list. |
| Expected results | The open launches should look like a small shunt capacitance and the joined launches like a small series inductance and resistance between the signal pads. No values are recorded in this repository. |

In [^6] and [^11] the signal pads are joined to each other. The connectivity
extracted from the layout does not show them tied to the ground pads, so they
are not a short to ground in the sense of the classic open-short method. The
intended de-embedding procedure is not recorded in this repository.

Full details: [`docs/README.md`](docs/README.md#de-embedding-structures).

Further reading:

1. M. C. A. M. Koolen, J. A. M. Geelen and M. P. J. G. Versleijen, "An improved de-embedding technique for on-wafer high-frequency characterization", Proc. Bipolar Circuits and Technology Meeting, pp. 188-191, 1991. [doi:10.1109/BIPOL.1991.160985](https://doi.org/10.1109/BIPOL.1991.160985)
2. H. Cho and D. E. Burk, "A three-step method for the de-embedding of high-frequency S-parameter measurements", IEEE Trans. Electron Devices, vol. 38, no. 6, pp. 1371-1375, 1991. [doi:10.1109/16.81628](https://doi.org/10.1109/16.81628)
3. T. E. Kolding, "A four-step method for de-embedding gigahertz on-wafer CMOS measurements", IEEE Trans. Electron Devices, vol. 47, no. 4, pp. 734-740, 2000. [doi:10.1109/16.830987](https://doi.org/10.1109/16.830987)
4. L. F. Tiemeijer and R. J. Havens, "A calibrated lumped-element de-embedding technique for on-wafer RF characterization of high-quality inductors and high-speed transistors", IEEE Trans. Electron Devices, vol. 50, no. 3, pp. 822-829, 2003. [doi:10.1109/TED.2003.811396](https://doi.org/10.1109/TED.2003.811396)
5. H. Ito and K. Masu, "A simple through-only de-embedding method for on-wafer S-parameter measurements up to 110 GHz", IEEE MTT-S Int. Microwave Symp. Digest, pp. 383-386, 2008. [doi:10.1109/MWSYM.2008.4633183](https://doi.org/10.1109/MWSYM.2008.4633183)

## Simulating the structures

The chip exists to check an openEMS simulation flow against silicon. This
repository holds only layout. It has no simulation scripts, no stack file and
no simulated results, and it does not name the flow. The pieces published
elsewhere are:

| Piece | Where |
|---|---|
| GDS to openEMS workflow | [VolkerMuehlhaus/gds2openEMS](https://github.com/VolkerMuehlhaus/gds2openEMS) |
| GDS to Palace workflow | [VolkerMuehlhaus/gds2palace_ihp_sg13g2](https://github.com/VolkerMuehlhaus/gds2palace_ihp_sg13g2) |
| GF180MCUD stack files for both, by the author of this chip | [`EM-Flow/` in EngGhaith/The-Silent-Owl-GF180MCU-WB-LNA](https://github.com/EngGhaith/The-Silent-Owl-GF180MCU-WB-LNA/tree/main/EM-Flow) |
| Stack viewer | [VolkerMuehlhaus/setupEM](https://github.com/VolkerMuehlhaus/setupEM) |

Those workflows take a GDS file, an XML description of the metal and
dielectric stack, and a short Python model script. Ports are drawn in the GDS
as polygons on extra layers, by convention 201 and above, and the model script
maps each layer to a port number. The inductor and transformer cells on this
chip already carry such polygons on layers 201 to 207. They are the red marks
in the pictures and are listed per cell in
[`docs/README.md`](docs/README.md#em-port-markers).

To produce the expected S-parameters for one structure:

1. Unzip [`RLCMV4_filled.zip`](RLCMV4_filled.zip) and cut out the cell you
   want, or start from a file in [`seperate_GDSs/`](seperate_GDSs/README.md).
2. Take [`OPENEMS-GF180MCUD-1P5M-TM11KA-MIMB.xml`](https://github.com/EngGhaith/The-Silent-Owl-GF180MCU-WB-LNA/blob/main/EM-Flow/OPENEMS-GF180MCUD-1P5M-TM11KA-MIMB.xml)
   and read the [README next to it](https://github.com/EngGhaith/The-Silent-Owl-GF180MCU-WB-LNA/blob/main/EM-Flow/README.md),
   in particular the note on MIM vias.
3. Write a gds2openEMS model script that maps the port layers to ports,
   following the gds2openEMS user guide.
4. Run it and compare the resulting Touchstone file with the de-embedded
   measurement.

Steps 3 and 4 have not been done as part of this documentation.

Further reading:

1. G. Al Sabagh, "The Design Journey of mWATTBAT: The Open-Source Radar Chip", master's thesis, Johannes Kepler University Linz, 2026, which has a section on transmission lines in openEMS. [PDF](https://epub.jku.at/download/pdf/13546624.pdf)
2. V. Mühlhaus, "User friendly workflow for RFIC EM simulation using openEMS", talk at the Free Silicon Conference, 2025. [Programme](https://wiki.f-si.org/FSiC2025)
3. T. Liebig, A. Rennings, S. Held and D. Erni, "openEMS: a free and open source equivalent-circuit (EC) FDTD simulation platform supporting cylindrical coordinates suitable for the analysis of traveling wave MRI applications", Int. J. Numerical Modelling, vol. 26, no. 6, pp. 680-696, 2013. [doi:10.1002/jnm.1875](https://doi.org/10.1002/jnm.1875)
4. [openEMS](https://www.openems.de/) and [Palace](https://awslabs.github.io/palace/stable/) project pages.

## License

The wafer.space project page lists this design under the CERN Open Hardware
Licence Version 2, Permissive (`CERN-OHL-P-2.0`). The full text is in
[`LICENSE`](LICENSE).

## Citing this work

No paper describes this chip yet. Until one does, cite the repository and the
shuttle:

```bibtex
@misc{alsabagh2026rlcm,
  author       = {Al Sabagh, Ghaith},
  title        = {{RLCM}: Test Passives for {GF180MCUD}},
  year         = {2026},
  howpublished = {\url{https://github.com/EngGhaith/RLCM-Test-Passives-For-GF180MCUD}},
  note         = {wafer.space GF180MCU Run 2, manufacturing ID G802RLCM}
}
```

Related work by the same author:

- G. Al Sabagh, G. Zachl and H. Pretl, "A 150-GHz 9-dBm EIRP Open-Source FMCW
  Radar Chip in 130-nm BiCMOS", Austrochip Workshop on Microelectronics,
  pp. 13-16, 2025.
  [doi:10.1109/Austrochip67945.2025.11183716](https://doi.org/10.1109/Austrochip67945.2025.11183716)

## Acknowledgements

The credits are written on the die itself, in Metal5 above transformer [^5]:

> DESIGNED BY GHAITH AL SABAGH, NTHFS JKU, MWTH CD LAB
>
> THANK U MIM, THANK U SHO, THANK U VOLKER MUEHLHAUS, THANK U LEO MOSER

| Name on the die | Who or what |
|---|---|
| NTHFS JKU | [Institute for Communications Engineering and RF-Systems](https://www.jku.at/en/institute-for-communications-engineering-and-rf-systems/), Johannes Kepler University Linz |
| MWTH CD LAB | [Christian Doppler Laboratory for Distributed Microwave and Terahertz Systems for Sensors and Data Links](https://www.jku.at/en/news-events/news/detail/news/neues-cd-labor-an-der-jku-hochfrequenzsysteme-fuer-moderne-elektronik/) |
| Volker Muehlhaus | Author of the [gds2openEMS](https://github.com/VolkerMuehlhaus/gds2openEMS) and [gds2palace](https://github.com/VolkerMuehlhaus/gds2palace_ihp_sg13g2) workflows |
| Leo Moser | Not stated in this repository |
| MIM, SHO | Not stated in this repository |

The chip was fabricated through [wafer.space](https://wafer.space/) and uses
its GF180MCU frame, logo and ID cells.
