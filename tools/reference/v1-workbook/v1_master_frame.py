"""The v1 workbooks (transfer case, centre diff, axle diff, final drive) in the frame of the user's
"v1 Chassis Master Geometry.SLDPRT".

That frame is the drivetrain viewer's CAD frame turned 180 degrees about Y: master (x, y, z) = viewer (-x, y, -z).
A turn is a rigid motion, so every At, slide position, speed and torque stays as it was; only each shaft's point
(x and z negated) and Axis (X and Z directions reversed) change.

Run from the Gear Generator repo:
  .venv/bin/python <this file> <out folder> <windows Transfer Case folder> <windows Differentials folder>
"""
import os
import sys
from dataclasses import replace

sys.path.insert(0, "src")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gear_generator.workbook import assess, geometry, model, xlsx  # noqa: E402
import v1_differentials  # noqa: E402
import v1_transfer_case  # noqa: E402

TURN_AXIS = {"Z+": "Z-", "Z-": "Z+", "X+": "X-", "X-": "X+", "Y+": "Y+", "Y-": "Y-", "": "Z-"}


def _neg(text: str) -> str:
    text = text.strip()
    if text in ("", "0"):
        return text
    return text[1:] if text.startswith("-") else "-" + text


def turn(spec):
    """The same gearbox turned 180 degrees about Y. Frame shafts: point (x, z) negated, Axis reversed in X and Z.
    A shaft on a carrier gives its offset in the carrier's plane, which turns with it: x negated, Axis left to the
    carrier (blank) as before."""
    shafts = []
    for s in spec.shafts:
        if s.mount() == "frame":
            shafts.append(replace(s, x=_neg(s.x), z=_neg(s.z), axis=TURN_AXIS[s.axis.strip()]))
        else:
            shafts.append(replace(s, x=_neg(s.x)))
    return replace(spec, shafts=tuple(shafts))


if __name__ == "__main__":
    out, tc_folder, diff_folder = sys.argv[1:4]
    books = [(turn(v1_transfer_case.spec()), tc_folder)]
    books += [(turn(make(diff_folder)), diff_folder) for make in
              (v1_differentials.final_drive, v1_differentials.centre_diff, v1_differentials.axle_diff)]
    for sp, folder in books:
        sp = replace(sp, box=replace(sp.box, output_folder=folder))
        path = os.path.join(out, sp.box.name + ".xlsx")
        xlsx.write_new(path, model.to_sheets(sp))
        read, problems = model.from_book(xlsx.read(path))
        a = assess.assess(replace(read, source_path=folder + "\\" + sp.box.name + ".xlsx"), problems, folder)
        print("=====", sp.box.name, "| output folder:", read.box.output_folder)
        print("  read problems:", [d.message for d in problems], "| refusal:", repr(a.lay_out_refusal()))
        for d in a.diagnostics:
            print("   ", d.message)
        for m in getattr(a.report, "modes", ()) or ():
            print("   mode", m)
        for gid, p in geometry.layout(read).placed.items():
            print(f"   {gid:14} centre ({p.centre[0]:9.3f}, {p.centre[1]:8.3f}, {p.centre[2]:9.3f})  axis {p.axis}")
