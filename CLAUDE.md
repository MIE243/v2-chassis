# v2-chassis

MIE243 low-cost teaching vehicle: a 4x4 drivetrain chassis (transfer case with planetary range box and chain front output, centre / front / rear bevel differentials, steering). **v2 starts as an exact copy of v1** (team repo MIE243/v1-chassis, branch `v1-drivetrain-cad`, commit 51868f8, plus `v1 Chassis Assembly.SLDASM` as the user saved it on 2026-11-24). File names still carry the `v1_` prefix; do not rename them.

**The current job is in [RUN-BRIEF.md](RUN-BRIEF.md).** Read it in full before touching SolidWorks.

## Frame
- Origin: centre of the input shaft (chassis assembly origin). **+Z forward** (front of car), **+X vehicle left**, **+Y up**, mm. All shafts lie in Y = 0.
- Diff cone apexes: centre (0, 0, -141.5), front (-63.5, 0, 133.25), rear (0, 0, -252.75).
- `v1 Chassis Master Geometry.SLDPRT` is out of date (sketch not yet rotated to this frame). The assemblies are the truth; positions are in `docs/notebook/2026-11-16 v1 Chassis Gear Specs and Positions.md`.
- Notebook rule (2026-11-22): **the geartrain stays locked: no gear may move position.**

## Assemblies
| File | Notes |
| --- | --- |
| `v1 Chassis Assembly.SLDASM` | Top level. Config "Demo 4H straight" and Animation study "Drivetrain demo 4H" exist alongside Default. |
| `Transfer Case/v1_TransferCase.SLDASM` | Configs 2H / 4H / N / 4L. Range sleeve distance 2H/4H 55.5, N 48, 4L 40.5; mode sleeve 2H 84.5, 4H/N/4L 90.5. |
| `Differentials/v1_CenterDiff_Assem.SLDASM` | **The centre diff the chassis uses** (not `v1_CentreDiff.SLDASM`, which is Gear Generator's original pair). Configs Default (= Open), Open, Locked. |
| `Differentials/v1_FrontDiff.SLDASM`, `v1_RearDiff.SLDASM` | Axle diffs, built from the shared `v1_FD_*` and `v1_AX_*` parts (one file used front and rear). |
| `Steering/v1_Steering.SLDASM` | Front axles + U-joints. Config "Straight (demo)". |
| `Differentials/v1_FinalDrive.SLDASM`, `v1_AxleDiff.SLDASM`, `v1_CentreDiff.SLDASM` | Gear Generator's original pair assemblies; reference only. |

## Standing rules
- **SolidWorks 2024 only.** Never save a file from SolidWorks 2026: the team opens these in 2024.
- **One SolidWorks instance.** No mouse or keyboard control. Drive SolidWorks through SW-Agent where it covers the operation, otherwise native COM (pywin32) from a dedicated STA thread on Windows. Launch Windows processes hidden (`powershell Start-Process -WindowStyle Hidden`); never `cmd.exe /c start "title"` (it pops a dialog on the user's screen).
- **Never stop a Gear Generator build or a COM call mid-call and then close SolidWorks**: on 2024 that crashed and reset the toolbars.
- **Always set Gear Generator's output Folder explicitly.** A blank folder means the app's remembered folder, which once sent a build into another project.
- **Never Build or Update a workbook** (`*.xlsx` / `*.workbook.json`), above all `Transfer Case/v1_TransferCase.xlsx`. The assemblies no longer match the workbooks; Update cannot add parts and a new revision drops user-added components. Work gear by gear.
- **Never edit `Differentials/v1_LockCollar.SLDPRT`** (the lock sleeve; notebook 2026-11-24).
- **Never open anything from a `v1-chassis` folder** in the same SolidWorks session. The file names are identical, so SolidWorks can bind v2 assemblies to v1 parts.
- Before writing SolidWorks API code, check the SW-Macro-Database (github.com/MoZ200701/SW-Macro-Database; via SW-Agent `db_search`, `gotchas_for`).
- Tell the user up front how long SolidWorks will be tied up.
- **Git:** commit or push only when the user asks. No Co-Authored-By or AI attribution lines.

## Tolerance convention (notebook 2026-11-22, confirmed by the user as diametral)
- Turns with the shaft (attachment): **+0.15 mm on the diameter**, D-bore. Ø8 shaft → Ø8.15.
- Spins on the shaft: **+0.35 mm on the diameter**, round bore. Ø8 shaft → Ø8.35.
