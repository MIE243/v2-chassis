# Report: v2 printed gears and bore fits

Run of [RUN-BRIEF.md](RUN-BRIEF.md), 2026-11-24 (local evening). Nothing is committed.

**Revised top assembly:** `C:\Users\M0obo\Desktop\MIE243\v2-chassis\v2 Chassis Assembly.SLDASM`

Tools: SolidWorks 2024 (32.5.0, Student Edition, the only instance). SW-Agent bridge 0.1.0+e74d6ed (branch `codex/two-client-state-and-queue`), knowledge 2.1.0. Gear Generator `workbook` @ 52af385, driven headlessly through its own Update values code path (`swbuild.update_variables` and `store.updated_sidecar`). Native COM (pywin32, one STA worker) was used where SW-Agent has no route:
- SW-Agent's write gate covers standalone parts only. It has no route for assembly references, equations, new features or mates.
- Its preflight refused to open the top assembly because of the transfer case's embedded virtual belt (`Belt1-5^v2_TransferCase`).

## Step 0: references
- The repo was cloned to `Desktop\MIE243\v2-chassis`. The run brief assumed `OneDrive\Desktop`, which does not exist on this machine. The 75 record paths in the `.gear.json` and `.workbook.json` files were rewritten to the real location.
- All 64 assembly references and 18 part external references (in-context links and derived steering parts) pointed at `OneDrive\Desktop\MIE243\v1-chassis`. All 82 were repointed to their v2 twins with `ReplaceReferencedDocument`, with every document closed. `Desktop\MIE243\v1-chassis` exists on this machine, so this mattered.
- The top assembly was opened and walked recursively: all 98 components resolve under the repo root. The only exception is the embedded virtual belt, which SolidWorks keeps in its temp folder.
- One reference remains outside the repo: `Motor/25d-metal-gearmotor-75-99.SLDPRT` records its import source, `Downloads\...\25d-metal-gearmotor-75-99.step`. It is missing and harmless.

## Step 1: what each bore runs on (measured coaxial overlap in the chassis)
| Part | Runs on (measured) | Turns with / spins on | Fit |
| --- | --- | --- | --- |
| Gear_m1.25_N29 (sun) | InDog Ø8 input stub, 10 mm, Lock-mated | turns with | D 8.15 / 7.65 |
| v2_LoDog (Ø10) | InDog Ø8 input stub, 24 mm. No bushing modelled | spins (carrier vs input) | round 8.35 |
| Dog_m1.25_N20 (Ø14) | the Ø14 tube, then the Ø8 mainshaft once the tube is gone | spins | round 8.35 |
| v2_ModeHub | its own `Boss-Extrude1` was the Ø14 hollow tube (z -125.75 to -84.5), running through the Dog, drive sprocket and CD_SideF bores | spins on the mainshaft | round 8.35, tube suppressed (your decision) |
| v2_CD_SideF (Ø14) | the tube, then the mainshaft | spins | round 8.35 |
| v2_CD_Side | nothing modelled yet (rear output shaft is yours) | turns with | D 8.15 / 7.65 |
| v2_CD_Spider, v2_AX_Spider | cross pins not modelled | spin | round 8.35 |
| v2_FD_Pinion | front: Sprocket_Front Ø8 shaft. Rear: LockHub Ø8 shaft | turns with | D 8.15 / 7.65 |
| v2_AX_Side | half-shafts and wheel axles Ø8 | turns with | D 8.15 / 7.65 |
| v2_LockDog (Ø14) | nothing modelled (rear output line). Keyed to the carrier | spins on the rear output | round 8.35 |

## Steps 2 to 4: changes per part
Printed changes exactly one global, as measured with Gear Generator's own planner on every recorded part: `Backlash`, from `0.3 * "Module"` to `IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )`. The parts with no record got the same change through the Equation Manager.

| Part | Route | Backlash before → after | Bore before → after (measured) | Drive / flat | Custom features |
| --- | --- | --- | --- | --- | --- |
| Gear_m1.25_N29 | in place (GG Update) | 0.375 → 0.3 | Ø8 → Ø8.15 (z 0–10) | new native `D-Flat`: face at x = 3.575, across the flat **7.65** | none |
| Gear_m1.25_N13 ×3 | in place | 0.375 → 0.3 | Ø6 custom hole kept | – | Sketch1, Cut-Extrude1 kept |
| Ring_m1.25_N55 | in place | 0.375 → 0.3 | – | – | none |
| v2_InDog | in place | 0.375 → 0.3 | shaft stub Ø8 untouched | – | Sketch1, Boss-Extrude1 (shaft) kept |
| v2_LoDog | in place, plus custom sketch dim | 0.375 → 0.3 | Ø10 → **Ø8.35 over the full 24 mm** (`Bore Diameter` and `D4@Sketch1`) | round | carrier and pins kept. Only the carrier hole's diameter changed |
| Dog_m1.25_N20 | in place | 0.375 → 0.3 | Ø14 → Ø8.35 | round | none |
| Sleeve_m1.25_N20 | in place | 0.375 → 0.3 | – | – | none |
| v2_CD_Side | in place | 0.75 → 0.3 | Ø8 → Ø8.15 (z 15.761–21.753) | new `D-Flat`, across the flat 7.65 | none |
| v2_CD_Spider | in place | 0.75 → 0.3 | Ø8 → Ø8.35 | round | none |
| v2_FD_Pinion | in place | 0.675 → 0.3 | Ø8 → Ø8.15 (z 24.72–35.723) | new `D-Flat`, across the flat 7.65 | none |
| v2_FD_Ring | in place | 0.675 → 0.3 | custom hole Ø8 → Ø8.15 (z 18.112–24.46), 2026-11-25 | new `D-Flat` (config Default, front diff) and `D-Flat Rear` (config Rear, rear diff), across the flat 7.65, each lined up with the locked side gear's flat | Sketch1, Sketch2, Cut-Extrude1 kept |
| v2_AX_Side | in place | 0.525 → 0.3 | Ø8 → Ø8.15 (z 11.232–15.227) | new `D-Flat`, across the flat 7.65 | none |
| v2_AX_Spider | in place | 0.525 → 0.3 | Ø8 → Ø8.35 | round | none |
| v2_RangeHub | globals | 0.375 → 0.3 | mainshaft Ø8 untouched | – | Sketch1, Boss-Extrude1 kept |
| v2_RangeSleeve | globals | 0.375 → 0.3 | Ø26 relief kept | – | Relief Sketch, Relief Bore kept |
| v2_ModeHub | globals | 0.375 → 0.3 | Ø14 bore with Ø8 tube → Ø8.35 (z 0–9) | round | **Boss-Extrude1 (the hollow tube) suppressed**, not deleted |
| v2_CD_SideF | globals | 0.75 → 0.3 | Ø14 → Ø8.35 | round | none |
| v2_LockDog | globals (bore only) | unchanged (0.375) | Ø14 → Ø8.35 | round | none |
| v2_LockHub, v2_LockCollar | untouched | – | – | – | – |
| Sleeve_m1.25_N17 | not in any assembly: untouched | – | – | – | – |

Notes:
- The records written by the in-place route say "bore 8.15 (or 8.35), no allowance", not "8 + allowance".
- The `D-Flat` is an extruded boss named `D-Flat`, with its sketch `D-Flat Sketch` on the Front plane. A cut cannot make a D out of an existing round hole. The boss fills the segment beyond a vertical chord at x = 3.575 mm, from the bore's start to its end, and merges into the part (one body each).
- Phase of the flat: the seed tooth-space sketch of each D gear is centred at 0°, on +X, as Gear Generator places its flats. So every flat faces the middle of a tooth space.
- The flat's dimensions are numeric, not linked to globals.
- No mesh loop closes between D-fixed gears. The sun is the only D gear on the input. CD_Side and the rear FD_Pinion do not mesh with each other. Each axle ring is locked (Concentric1, lock rotation) to its neighbouring side gear and so, since 2026-11-25, D-fitted to the same half-shaft. The flats still over-constrain nothing: ring and side gear do not mesh with each other, the spiders spin on their pins, and the pinion is on its own shaft. Locking the ring to a side gear makes each axle diff a spool (both wheels turn together).
- Chassis mate **"Hollow shaft locked in CD front side gear [replaces GearMate2]" is suppressed in all configurations**, because it used the tube's face. Nothing else was changed in any assembly.
- No workbook was built or updated.

### 2026-11-25: axle ring gears D-fitted
The axle ring (`v2_FD_Ring`) is locked to the side gear beside it (front `v2_AX_Side-1`, rear `v2_AX_Side-2`), so it now has the side gear's D-bore. Measured in ring coordinates, the side gear's flat lies at −149.673° in the front diff and −14.533° in the rear diff. The 135.14° between them is not a whole number of tooth pitches, so one flat cannot line up with both without moving a gear. The ring therefore has two configurations:
- **Default** (front diff): `D-Flat` at −149.673°; `D-Flat Rear` suppressed.
- **Rear** (rear diff, component `v2_FD_Ring-1` now references it): `D-Flat Rear` at −14.533°; `D-Flat` suppressed.

Measured: one body, bore Ø8.15, flat 3.575 from the axis over z 18.112–24.46, no feature errors in either configuration. In each diff, the ring's flat and the side gear's flat point the same way (0.000° apart). Mate errors: 0 in the front diff, the rear diff and the chassis, before and after. No gear moved. Saved: the ring and both diff sub-assemblies. The chassis and transfer case were left unsaved (they held the user's unsaved changes). Physically, either ring prints and works in either diff. The two configurations exist so that the CAD lines up.

## Step 5: verification
- **References after close and reopen:** 98 components, all under the repo root (the virtual belt excepted). None suppressed, none lightweight.
- **Mate errors:** 0 in all six assemblies, before and after, at their saved configurations and in every configuration checked below. The suppressed mates are the original intentional ones (old 1:1 gear mates, sleeve gear mates, steering straight-demo mates) plus the tube mate above.
- **Feature errors:** 0 in all 20 gear and lock parts after reopen. Each is one body and none is dirty.
- **Sleeve positions:** unchanged. Range 55.5 / 55.5 / 48 / 40.5 and mode 84.5 / 90.5 / 90.5 / 90.5 (2H / 4H / N / 4L). Hubs 55.5 and 84.5.
- **Interference (mm³), baseline → after:**

| Assembly / configuration | Before | After |
| --- | --- | --- |
| Transfer Case/v2_TransferCase.SLDASM | 2H | 606.269 | 666.243 |
| Transfer Case/v2_TransferCase.SLDASM | 4H | 398.074 | 416.905 |
| Transfer Case/v2_TransferCase.SLDASM | N | 291.729 | 347.007 |
| Transfer Case/v2_TransferCase.SLDASM | 4L | 320.665 | 375.692 |
| Differentials/v2_CenterDiff_Assem.SLDASM | Open | 0 | 1.448 |
| Differentials/v2_CenterDiff_Assem.SLDASM | Locked | 0 | 1.448 |
| Differentials/v2_FrontDiff.SLDASM | Default | 0 | 0 |
| Differentials/v2_RearDiff.SLDASM | Default | 0 | 0 |
| Steering/v2_Steering.SLDASM | Straight (demo) | 221.387 | 221.387 |
| v2 Chassis Assembly.SLDASM | Default | 606.269 | 705.871 |
| v2 Chassis Assembly.SLDASM | Demo 4H straight | 406.464 | 467.806 |

  What changed:
  - **D-flat against round shafts (expected):** sun × InDog 10.28, FD_Pinion × LockHub 11.31, FD_Pinion × Sprocket_Front 10.46, AX_Side × each half-shaft 4.1. This is the flat cutting into a still-round Ø8 shaft; the sun's segment, worked out by hand, is 10.28 mm³. It goes away once the shafts get their 7.5 mm flats.
  - **Meshes (larger):** sun × planet 43 → 52 (4H), planet × ring 38 → 49 (chassis demo), sleeves on hubs and dogs up by 15–35, Sleeve_N20 × ModeHub 0 → 10 (4L), CD_SideF × CD_Spider 0 → 1.45. The printed default backlash (0.3 mm) is **smaller** than the machined 0.3 × module these gears had (module 1.25 to 2.5), so the teeth got thicker. The mesh overlaps other than the spider were already there in the baseline from tooth phase; no gear was moved.
  - **Unchanged:** chain against sprocket, and steering pin against wheel yoke.
- **Differential and transfer-case motion: NOT VERIFIED.** Turning components through the API (`Transform2`, and `IDragOperator` with every TransformType and DragMode tried, then rebuild or ForceRebuild3) does not re-solve coupled mates in this session. Even the untouched Lock mate InDog to sun did not follow. The result is a test-method failure, not evidence about the model. Every configuration (TC 2H/4H/N/4L, CD Open/Locked, chassis Default and Demo 4H straight) rebuilds with 0 mate errors, and no gear or lock mate was edited. Please check by hand with Rotate Component, or run the "Drivetrain demo 4H" study.
- **Saved and reopened:** every changed file was saved from SolidWorks 2024, all documents closed, and the top assembly reopened from disk for the checks above.

## Open items for you
1. **Front-output torque link (decision 3).** The tube is suppressed and its chassis mate too. Nothing now carries torque from the CD front side gear through the mode hub to the front drive. Not modelled, as instructed.
2. **Shafts.** The D-bores assume a 7.5 mm across-flat shaft (the brief's proposal; Gear Generator's README calls 7.0 common). Until the shafts have flats, the D segments read as interference.
3. **Backlash.** If the tighter printed backlash is not wanted for module 1.25 and up, type a Backlash (for example 0.3 × module again) per gear.
4. **LoDog.** The Ø10 bore had nothing else in it and no bushing modelled. It is now Ø8.35 over its whole 24 mm, which needed the carrier sketch's `D4@Sketch1`.
5. **LockDog** was taken as free on the rear output (round 8.35), following the brief's "free, joins future case". Change it if it is meant to be keyed.
6. **Out of scope, left alone:**
   - FD_Ring's custom Ø8 hole sat on the half-shaft with no clearance. Since 2026-11-25 it is a D-bore (Ø8.15, 7.65 across the flat).
   - The planets' custom Ø6 holes run on Ø5.3 carrier pins (the brief said Ø3).
   - Sleeve_m1.25_N17 is in no assembly.
   - The workbooks still do not match the assemblies.
7. Known before this run and unchanged: chain against mode-sleeve rim, 4L sense in the chassis motion, no key between sprocket dog and sprocket, U-joint wobble, materials unassigned.
