# Modular joints in v2 Chassis Modular

Built 2026-11-25. Top assembly: `v2 Chassis Modular.SLDASM`. Modules are in `Modules/`.

## Joints
Each joint is a male tongue (4.00 mm wide) in a female slot, modelled on `Experiment/Modular Joint Demo.SLDASM`. The tongue and slot lie in the part reference plane listed below.

| Joint | Line | Male (plane) | Female (plane) | Axial gap as modelled |
| --- | --- | --- | --- | --- |
| J1 | mainshaft, M3 ↔ M4 | `v2_M2M4_Shaft` (Right) | `v2_RangeHub` (Right) | 0 |
| J2 | mainshaft, M4 ↔ M5 | `v2_CD_Carrier` stub (Right) | `v2_M2M4_Shaft` rear (Right) | 0.30 mm |
| J3 | Ø14 tube, M4 ↔ M5 | `v2_CD_SideF` (Right) | `v2_ModeHub` (Right) | — |
| J4 | rear output, M5 ↔ M6 | `v2_LockHub` (Right) | `v2_RearDiff_Axle` (Top) | 0.15 mm |
| J5 | front output, M4 ↔ M1 | `v2_Sprocket_Front` (Plane1) | `v2_FrontDiff_Axle` (Top) | 0.15 mm |

## Top-level mates
**Every configuration:** "M0 on origin" (the anchor).

**Attached (Default, Demo 4H straight):**
- "M2 on chassis" and "M3 on chassis": origin coordinate mates to M0.
- "M4 on M3", "M5 on M4", "M6 on M5", "M1 on M4": origin coordinate mates between neighbouring modules. All modules share the chassis origin, so this is their exact position.
- "J1 tongue" … "J5 tongue": tongue plane parallel to slot plane. This is the only mate at each joint and carries the rotation.

**Detach only:**
- "Mn slide Front" and "Mn slide Right" for M1 to M6: module Front and Right planes coincident with M0's, so each module is free in +Y only.
- Every module except M0 is **rigid** in Detach, so dragging moves the whole module.
- Each module uses its own **Detach** configuration, which holds its joint tongues vertical (parallel to the module Right plane):
  - M3: N with the range hub vertical.
  - M4: 2WD with the M2M4 shaft, mode hub and front sprocket vertical.
  - M5: Open with GearMate2 off and the carrier, front side gear and lock hub vertical.
  - M6: rear driveshaft vertical.
  - M1: front driveshaft vertical.

**Suppressed everywhere (stale since the shaft split):** "Rear output shaft locked in rear pinion", "Front output shaft locked in front pinion", "Cross pin parallel to spider axis".

## Why the modules are placed by neighbour origin mates, not through the shafts
The first build located each module through its joint: concentric + axial mates on the shafts, plus a roll mate. Every one of those mates grabbed a face of a part that spins inside a flexible module. SolidWorks' solver then jammed the drivetrain unpredictably:
- In 2H, driving the input or a rear wheel moved nothing (error 51 on every joint mate).
- Moving single mates around only shifted where it jammed.

With neighbour origin mates for position and tongue-only joints for rotation, every drive test passes (below).

## M3 planetary fix
The original M3 mates locked the whole drivetrain. With the ring gear fixed, the "Pl copy 1 meshes Ring" gear mate pinned the planets, which pinned the sun and the input.
- **Now:** "Epicyclic: sun drives carrier (29:84 same way)", plus the original "Sun meshes Pl copy 1–3" (13:29).
- **Behaviour:** for gears on a moving carrier, SolidWorks measures gear-mate rotation relative to the carrier, so the sun–planet mates are correct epicyclic relations.
- **Suppressed:** "Pl copy 1 meshes Ring".
- **Measured** (input −20°):
  - carrier −6.905° (1/2.897)
  - planets +22.308° (true absolute spin)
  - range hub −20° in H, 0° in N, −6.905° in L (correct direction, so 4L no longer runs backwards)

## Hand-turn verification (2026-11-25)
Each driver was turned 15° with a temporary angle mate, and every gear, shaft and wheel was measured. 0 mate errors in every case.
- **Default (2H, 2WD, centre diff Locked).** Drivers: input, mainshaft, carrier, or a rear wheel.
  - The input, range hub, mainshaft, carrier, both side gears, lock hub, mode hub, rear driveshaft and pinion turn 1:1.
  - The rear ring and both rear wheels turn at ½.
  - The planets turn −1.115 × the input.
  - The front driveline stays still (2WD) and turns on its own from the front driveshaft or front sprocket.
- **Demo 4H straight (4WD).** All six drivers turn everything, front and rear. Front and rear wheels both turn at ½ of the input.

## Open design items
1. **Tongue and slot widths:** tongues are 4.00 mm and slots 3.85–3.87 mm, so they interfere by 0.13–0.15 mm. The +0.15 allowance looks reversed; slots of about 4.15 mm are probably intended.
2. **M5 tongue phase when Locked:** relative to the carrier's tongue, the lock hub tongue (J4) sits at 77.06° and the front side gear tongue (J3) at 63.78°.
   - The J4 offset is exactly the "LockDog keyed to Carrier" angle mate.
   - The J3 offset comes from the side gear and spider mesh phase.
   - With the diff Locked they can never all line up (39° residual).
   - In a real assembly: lift M4 before M5, or re-phase the J3 tongue relative to the side gear teeth.
3. **Lock dog key angle:** the 77.06° above is inherited from v1. It is not changed.
4. **M1 in Detach:** the solver nudges M1 0.92 mm up when switching into Detach. It is free in Y there.
5. **Motion study:** the copied "Drivetrain demo 4H" study in the modular top points at pre-modular components and needs rebuilding.
