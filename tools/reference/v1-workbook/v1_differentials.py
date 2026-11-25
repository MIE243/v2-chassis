"""The MIE243 v1 differential gear sets as Gear Generator workbooks.

Frame: the drivetrain viewer's CAD frame (origin at the middle of the input shaft, X left, Y up, Z forward, mm).
Each shaft's Axis points from the cone tip into the gear's body, as the viewer's bevel axes do.

The app does not model a differential (spiders orbiting in a turning case), so each diff is built with its case
held still: one side gear is the input, the spiders turn on frame shafts, the other side gear is the output at
1 : 1 the other way. The gears, their cone angles and their places are the real ones; the case, cross pin and
lock collar are the user's to design. The final drive (pinion and ring) is its own workbook for the same reason:
the ring rides on the case.

Run from the Gear Generator repo:  .venv/bin/python <this file> <out folder> <windows output folder>
"""
import os
import sys
from dataclasses import replace

sys.path.insert(0, "src")
from gear_generator.workbook import assess, model, xlsx
from gear_generator.workbook.model import Box, Gear, GearboxSpec, Mesh, Shaft

CENTRE_APEX = ("0", "0", "-151.5")
REAR_AXLE_APEX = ("0", "0", "-252.75")


def g(gid, shaft, teeth, module, face, row, bore="", part="", notes=""):
    return Gear(gid, shaft, "0", "bevel", "", teeth, module, "", face, bore, notes=notes, part_name=part, row=row)


def s(sid, apex, axis, row, role="", speed="", torque="", notes=""):
    return Shaft(sid, "frame", *apex, axis, role, "", speed, torque, notes, row=row)


def diff_pair(name, apex, side_axis, spider_axis, face, part, side_note, row_notes="", module="2.5"):
    """One side gear and one spider of a diff, at their real places. The app's clash check measures a bevel gear's
    face round its cone tip, so two side gears on one axis (or two spiders) are refused as clashing; one pair gives
    every part, cut for its partner, and the rest are copies placed in SolidWorks."""
    shafts = (
        s("Side", apex, side_axis, 2, "input", "100", "0.5", side_note),
        s("Pin", apex, spider_axis, 3, "output", notes="Spider on the cross pin (the case held still in this assembly)"),
    )
    gears = (
        g("Side", "Side", "18", module, face, 2, bore="8", part=part + "_Side"),
        g("Spider", "Pin", "12", module, face, 3, bore="8", part=part + "_Spider"),
    )
    return shafts, gears, (Mesh("Side", "Spider", row=2),)


def centre_diff(out_folder: str) -> GearboxSpec:
    """Centre diff: side gears 18T, two spiders 12T, m2.5, face 9, apex at Z -151.5. Front side gear and the upper spider."""
    shafts, gears, meshes = diff_pair("v1_CentreDiff", CENTRE_APEX, "Z+", "Y+", "9", "v1_CD",
                                      "Front side gear (hollow shaft round the mainshaft); the rear one is the same part, on Z-")
    return GearboxSpec(box=Box(name="v1_CentreDiff", output_folder=out_folder, pressure_angle="20", efficiency="98"),
                       shafts=shafts, gears=gears, meshes=meshes)


def axle_diff(out_folder: str) -> GearboxSpec:
    """Axle diff (same parts front and rear), at the rear axle: side gears 18T, four spiders 12T, m1.75, face 6.
    Left side gear and the upper spider. m1.75 rather than the spec's m2.5 (decided 2026-11-15): at m2.5 the spiders
    hit the final drive's pinion and ring (SolidWorks interference check), with no room for the case wall."""
    shafts, gears, meshes = diff_pair("v1_AxleDiff", REAR_AXLE_APEX, "X+", "Y+", "6", "v1_AX",
                                      "Left side gear (left half shaft); the right one is the same part, on X-",
                                      module="1.75")
    return GearboxSpec(box=Box(name="v1_AxleDiff", output_folder=out_folder, pressure_angle="20", efficiency="98"),
                       shafts=shafts, gears=gears, meshes=meshes)


def final_drive(out_folder: str) -> GearboxSpec:
    """Final drive (same part front and rear), placed at the rear axle: pinion 15T, ring 30T, m2.25, face 12, 2 : 1."""
    shafts = (
        s("Pinion", REAR_AXLE_APEX, "Z+", 2, "input", "100", "0.5", "Pinion shaft from the rear driveshaft, 8 mm"),
        s("Case", REAR_AXLE_APEX, "X-", 3, "output", notes="Ring gear, bolted to the diff case"),
    )
    gears = (
        g("Pinion", "Pinion", "15", "2.25", "12", 2, bore="8", part="v1_FD_Pinion"),
        g("Ring", "Case", "30", "2.25", "12", 3, part="v1_FD_Ring", notes="No bore: mount to the diff case is the user's"),
    )
    return GearboxSpec(box=Box(name="v1_FinalDrive", output_folder=out_folder, pressure_angle="20", efficiency="98"),
                       shafts=shafts, gears=gears, meshes=(Mesh("Pinion", "Ring", row=2),))


if __name__ == "__main__":
    out, win_out = sys.argv[1], sys.argv[2]
    for make in (centre_diff, axle_diff, final_drive):
        sp = make(win_out)
        path = os.path.join(out, sp.box.name + ".xlsx")
        xlsx.write_new(path, model.to_sheets(sp))
        read, problems = model.from_book(xlsx.read(path))
        a = assess.assess(replace(read, source_path=win_out + "\\" + sp.box.name + ".xlsx"), problems, win_out)
        print("=====", sp.box.name, "->", path)
        print("read problems:", [d.message for d in problems])
        print("lay_out_refusal:", repr(a.lay_out_refusal()))
        for d in a.diagnostics:
            print(" ", getattr(d, "severity", "?"), "|", d.message)
        rep = getattr(a, "report", None)
        if rep is not None:
            for name in ("ratio", "speeds", "modes"):
                if hasattr(rep, name):
                    print(" ", name, ":", getattr(rep, name))
