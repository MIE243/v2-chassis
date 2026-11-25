# Modular joints in v2 Chassis Modular

Built 2026-11-25. Top assembly: `v2 Chassis Modular.SLDASM`. Modules are in `Modules/`.

## Joints
Each joint is a male tongue (4.00 mm wide) in a female slot, modelled on `Experiment/Modular Joint Demo.SLDASM`. The tongue and slot lie in the part reference plane listed below.

| Joint | Line | Male (plane) | Female (plane) | Axial gap |
| --- | --- | --- | --- | --- |
| J1 | mainshaft, M3 ↔ M4 | `v2_M2M4_Shaft` (Right) | `v2_RangeHub` (Right) | 0 (coincident) |
| J2 | mainshaft, M4 ↔ M5 | `v2_CD_Carrier` stub (Right) | `v2_M2M4_Shaft` rear (Right) | 0.30 mm |
| J3 | Ø14 tube, M4 ↔ M5 | `v2_CD_SideF` (Right) | `v2_ModeHub` (Right) | (positioned by J2) |
| J4 | rear output, M5 ↔ M6 | `v2_LockHub` (Right) | `v2_RearDiff_Axle` (Top) | 0.15 mm |
| J5 | front output, M4 ↔ M1 | `v2_Sprocket_Front` (Plane1) | `v2_FrontDiff_Axle` (Top) | 0.15 mm |

## Mates (top assembly)
**Attached (Default, Demo 4H straight):**
- "Jn axis": concentric on the Ø8 shafts (not on J3, which shares J2's axis).
- "Jn axial": coincident for J1; distance mates (the gaps above) for J2, J4 and J5.
- "Jn tongue": tongue plane parallel to slot plane. This is the engagement, and it sets the rotational phase.
- "M1/M4/M5/M6 roll": module Top plane parallel to M0's Top plane, so a housing cannot turn about its shaft.
- "M2 on chassis", "M3 on chassis": origin mates to M0.

**Detach only (suppressed in the attached configurations):**
- "Mn slide Front" and "Mn slide Right" for M1 to M6: module Front and Right planes coincident with M0's, so each module is free in +Y only.
- Nine "... vertical" mates: each tongue and slot plane parallel to M0's Right plane.
- Referenced configurations in Detach: M3 **N**, M4 **2WD**, M5 **Detach**.

The joint and roll mates and the M2/M3 mounts are suppressed in Detach. "M0 on origin" is active in every configuration.

**Suppressed everywhere (stale since the shaft split):** "Rear output shaft locked in rear pinion", "Front output shaft locked in front pinion", "Cross pin parallel to spider axis".

## Why the module configurations are set this way in Detach
- **M3 N:** with the ring gear fixed, SolidWorks gear mates in the planetary lock the input train's rotation. In H or L the range hub cannot turn its slot vertical. In N the range sleeve releases the hub.
- **M4 2WD:** in 4WD the chain ties the mode hub (J3) to the front sprocket (J5).
- **M5 Detach:** a copy of Open with GearMate2 (rear side gear ↔ spider 2) suppressed, so the carrier, front side gear and lock hub turn independently. This is a CAD-only freedom, the same as turning each shaft by hand before lifting.

## Open design items
1. **Tongue and slot widths:** tongues are 4.00 mm and slots 3.85 to 3.87 mm, so they interfere by 0.13 to 0.15 mm. The +0.15 allowance looks reversed; slots of about 4.15 mm are probably intended.
2. **M5 tongue phase when Locked:** relative to the carrier's tongue, the lock hub tongue (J4) sits at 77.06° and the front side gear tongue (J3) at 63.78°.
   - The J4 offset is exactly the "LockDog keyed to Carrier" angle mate.
   - The J3 offset comes from the side gear and spider mesh phase.
   - Rotating the lock group shifts both by equal and opposite amounts, so with the diff Locked they can never all line up (39° residual).
   - In a real assembly the mesh phase changes in one-tooth steps (20°). Lining them up needs the J3 tongue re-phased relative to the side gear teeth, or an accepted lift order: lift M4 before M5.
3. **Lock dog key angle:** the 77.06° above is a design choice inherited from v1. It is not changed.
4. **M1 in Detach:** the solver moves M1 0.92 mm up when switching into Detach. It is free in Y there, and Default reseats it exactly.
5. **Motion study:** the copied "Drivetrain demo 4H" study in the modular top still points at the pre-modular components and needs rebuilding.
