"""The MIE243 v1 transfer case (range box + mode sleeve) as a Gear Generator workbook.

Frame: the drivetrain viewer's CAD frame — origin at the middle of the input shaft, X left, Y up, Z forward, mm.
"""
import sys
from dataclasses import replace
sys.path.insert(0, "src")
from gear_generator.workbook import assess, model, xlsx
from gear_generator.workbook.model import Box, Gear, GearboxSpec, Mesh, Mode, Shaft

RANGE = ("17", "1.25")      # range sleeve and its two dogs: teeth, module (pitch dia 21.25)
MODE = ("20", "1.25")       # mode sleeve and the sprocket's dog (pitch dia 25, over the 14 mm hollow shaft)


def g(gid, shaft, at, kind, teeth, module, face, row, slides="", side="", bore="", notes="", part=""):
    return Gear(gid, shaft, at, kind, side, teeth, module, "", face, bore, slides=slides, notes=notes, part_name=part, row=row)


def spec() -> GearboxSpec:
    shafts = (
        Shaft("In", "frame", "0", "0", "0", "Z+", "input", "", "100", "0.5", "Input shaft, 8 mm; ~100 rpm gearmotor through a ~0.5 N·m slip clutch", row=2),
        Shaft("Carrier", "frame", "0", "0", "0", "Z+", "", notes="Planetary carrier", row=3),
        Shaft("Planet", "Carrier", "26.25", "0", "0", "", "", "3", notes="3 planets on a Ø52.5 circle", row=4),
        Shaft("Ring", "frame", "0", "0", "0", "Z+", "fixed", notes="Ring, fixed to the range box", row=5),
        Shaft("Rear", "frame", "0", "0", "0", "Z+", "output", notes="Mainshaft (to the centre diff case)", row=6),
        Shaft("FrontDrv", "frame", "0", "0", "0", "Z+", "output", notes="Drive sprocket hub (chain to the front output, 1 : 1)", row=7),
    )
    gears = (
        g("Sun", "In", "10.5", "spur", "29", "1.25", "10", 2, bore="8"),
        g("Pl", "Planet", "10.5", "spur", "13", "1.25", "10", 3),
        g("Ring", "Ring", "10.5", "spur", "55", "1.25", "10", 4, side="internal"),
        g("InDog", "In", "-32", "dog", *RANGE, "5", 5, bore="8", part="v1_InDog", notes="High range: the sleeve joins the mainshaft to the input shaft"),
        g("LoDog", "Carrier", "-17", "dog", *RANGE, "5", 6, bore="10", part="v1_LoDog", notes="Low range: the sleeve joins the mainshaft to the carrier"),
        g("RangeSlv", "Rear", "-24.5", "sleeve", *RANGE, "10", 7, slides="H=-5, N=0, L=+5"),
        g("FrontDog", "FrontDrv", "-88", "dog", *MODE, "5", 8, bore="14", notes="On the drive sprocket's face (sprocket at Z -92.5)"),
        g("ModeSlv", "Rear", "-80.5", "sleeve", *MODE, "10", 9, slides="2WD=0, 4WD=-5"),
    )
    meshes = (Mesh("Sun", "Pl", row=2), Mesh("Pl", "Ring", row=3))
    sliders = ("RangeSlv", "ModeSlv")
    modes = (
        Mode("2H", (("RangeSlv", "H"), ("ModeSlv", "2WD")), "rear drive, high range", row=2),
        Mode("4H", (("RangeSlv", "H"), ("ModeSlv", "4WD")), "four-wheel drive, high range", row=3),
        Mode("N", (("RangeSlv", "N"), ("ModeSlv", "4WD")), "neutral", row=4),
        Mode("4L", (("RangeSlv", "L"), ("ModeSlv", "4WD")), "four-wheel drive, low range 2.897 : 1", row=5),
    )
    return GearboxSpec(box=Box(name="v1_TransferCase", pressure_angle="20", efficiency="98"), shafts=shafts,
                       gears=gears, meshes=meshes, modes=modes, sliders=sliders)


if __name__ == "__main__":
    out = sys.argv[1]
    xlsx.write_new(out, model.to_sheets(spec()))
    read, problems = model.from_book(xlsx.read(out))
    a = assess.assess(replace(read, source_path="C:\\B\\v1_TransferCase.xlsx"), problems, "C:\\Out\\")
    print("read problems:", [d.message for d in problems])
    print("lay_out_refusal:", repr(a.lay_out_refusal()))
    for d in a.diagnostics if hasattr(a, "diagnostics") else []:
        print(getattr(d, "severity", "?"), "|", d.message)
    print([n for n in dir(a) if not n.startswith("_")])
