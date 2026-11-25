# v2-chassis

MIE243 low-cost teaching vehicle: a 4x4 drivetrain chassis (transfer case with planetary range box and chain front output, centre / front / rear bevel differentials, steering). **v2 starts as an exact copy of v1** (team repo MIE243/v1-chassis, branch `v1-drivetrain-cad`, commit 51868f8, plus `v2 Chassis Assembly.SLDASM` as the user saved it on 2026-11-24). Files were renamed from `v1_` to `v2_` (and `v1 Chassis …` to `v2 Chassis …`) on 2026-11-24, with every SolidWorks reference repointed; older notes and `tools/reference/` still use the v1 names.

**The current job is in [RUN-BRIEF.md](RUN-BRIEF.md).** Read it in full before touching SolidWorks.

## Frame
- Origin: centre of the input shaft (chassis assembly origin). **+Z forward** (front of car), **+X vehicle left**, **+Y up**, mm. All shafts lie in Y = 0.
- Diff cone apexes: centre (0, 0, -141.5), front (-63.5, 0, 133.25), rear (0, 0, -252.75).
- `v2 Chassis Master Geometry.SLDPRT` is out of date (sketch not yet rotated to this frame). The assemblies are the truth; positions are in `docs/notebook/2026-11-16 v1 Chassis Gear Specs and Positions.md`.
- Notebook rule (2026-11-22): **the geartrain stays locked: no gear may move position.**

## Assemblies
| File | Notes |
| --- | --- |
| `v2 Chassis Assembly.SLDASM` | Top level. Config "Demo 4H straight" and Animation study "Drivetrain demo 4H" exist alongside Default. |
| `Transfer Case/v2_TransferCase.SLDASM` | Configs 2H / 4H / N / 4L. Range sleeve distance 2H/4H 55.5, N 48, 4L 40.5; mode sleeve 2H 84.5, 4H/N/4L 90.5. |
| `Differentials/v2_CenterDiff_Assem.SLDASM` | **The centre diff the chassis uses** (not `v2_CentreDiff.SLDASM`, which is Gear Generator's original pair). Configs Default (= Open), Open, Locked. |
| `Differentials/v2_FrontDiff.SLDASM`, `v2_RearDiff.SLDASM` | Axle diffs, built from the shared `v2_FD_*` and `v2_AX_*` parts (one file used front and rear). |
| `Steering/v2_Steering.SLDASM` | Front axles + U-joints. Config "Straight (demo)". |
| `Differentials/v2_FinalDrive.SLDASM`, `v2_AxleDiff.SLDASM`, `v2_CentreDiff.SLDASM` | Gear Generator's original pair assemblies; reference only. |

## Modular layout (2026-11-25)
`v2 Chassis Modular.SLDASM` is the modular top assembly. The original `v2 Chassis Assembly.SLDASM` and its sub-assemblies are kept unchanged for comparison. Full details: [docs/MODULAR-JOINTS.md](docs/MODULAR-JOINTS.md).
| Module | Contents | Configs | Placed by (attached) |
| --- | --- | --- | --- |
| `M0_Chassis` | empty frame, the anchor | Default | "M0 on origin" |
| `M1_FrontAxle` | `v2_FrontDiff` (with `v2_FrontDiff_Axle`) + `v2_Steering` | Default, Demo 4H straight, Detach | "M1 on M4" |
| `M2_Motor` | gearmotor | Default | "M2 on chassis" |
| `M3_RangeBox` | input dog, sun, planets, ring, carrier, LoDog, range hub, range sleeve | H / N / L / Detach | "M3 on chassis" |
| `M4_FrontDrive` | `v2_M2M4_Shaft`, mode hub (Ø14 tube), mode sleeve, front dog, sprockets, chain | 2WD / 4WD / Detach | "M4 on M3" |
| `M5_CentreDiff` | centre diff, cross pin in `v2_CD_Carrier`, lock set | Default / Open / Locked / Detach | "M5 on M4" |
| `M6_RearAxle` | `v2_RearDiff`, `v2_RearDiff_Axle`, rear wheels | Default, Demo 4H straight, Detach | "M6 on M5" |

- Modules are placed by origin coordinate mates to their neighbour, never through faces of spinning parts, because that jams SolidWorks' solver. The shaft joints J1–J5 carry rotation only ("Jn tongue").
- **Default** and **Demo 4H straight** are attached; the drivetrain turns by hand from any shaft or wheel.
- **Detach:** neighbour mates are off. Every module except M0 is rigid and slides in +Y only, with every tongue held vertical by the module's own Detach configuration.
- M3's planetary uses "Epicyclic: sun drives carrier (29:84 same way)". The planet ↔ ring gear mate is suppressed, because it locked the train.

## Standing rules
- **SolidWorks 2024 only.** Never save a file from SolidWorks 2026: the team opens these in 2024.
- **One SolidWorks instance.** No mouse or keyboard control. Drive SolidWorks through SW-Agent where it covers the operation, otherwise native COM (pywin32) from a dedicated STA thread on Windows. Launch Windows processes hidden (`powershell Start-Process -WindowStyle Hidden`); never `cmd.exe /c start "title"` (it pops a dialog on the user's screen).
- **Never stop a Gear Generator build or a COM call mid-call and then close SolidWorks**: on 2024 that crashed and reset the toolbars.
- **Always set Gear Generator's output Folder explicitly.** A blank folder means the app's remembered folder, which once sent a build into another project.
- **Never Build or Update a workbook** (`*.xlsx` / `*.workbook.json`), above all `Transfer Case/v2_TransferCase.xlsx`. The assemblies no longer match the workbooks; Update cannot add parts and a new revision drops user-added components. Work gear by gear.
- **Never edit `Differentials/v2_LockCollar.SLDPRT`** (the lock sleeve; notebook 2026-11-24).
- **Never open anything from a `v1-chassis` folder** in the same SolidWorks session. The v2 files now carry `v2_` names, but parts such as `Gear_m1.25_N29` still share names with v1, so SolidWorks could bind v2 assemblies to v1 parts.
- Before writing SolidWorks API code, check the SW-Macro-Database (github.com/MoZ200701/SW-Macro-Database; via SW-Agent `db_search`, `gotchas_for`).
- Tell the user up front how long SolidWorks will be tied up.
- **Git:** commit or push only when the user asks. No Co-Authored-By or AI attribution lines.

## Tolerance convention (notebook 2026-11-22, confirmed by the user as diametral)
- Turns with the shaft (attachment): **+0.15 mm on the diameter**, D-bore. Ø8 shaft → Ø8.15.
- Spins on the shaft: **+0.35 mm on the diameter**, round bore. Ø8 shaft → Ø8.35.
