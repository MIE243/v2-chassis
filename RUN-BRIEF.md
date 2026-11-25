# Run brief: Printed gears and bore fits (v2)

You own this run end to end and report straight to the user. There is no other session coordinating it. Plan for several hours of SolidWorks time; tell the user the estimate before you start.

The user's original request is preserved verbatim in [docs/ORIGINAL-REQUEST.md](docs/ORIGINAL-REQUEST.md). **The decisions below were made after it and override it where they differ.**

## Decisions already made
1. **SolidWorks 2024.**
2. **Gears first; shafts are the user's.** Do not create shaft parts and do not change the shafts modelled into parts (`v1_InDog` input-shaft stub, `v1_RangeHub` mainshaft section, `v1_LockHub`, `v1_Sprocket_Front` front shaft, the rear wheels' half-shafts). The user will CAD shafts by hand.
3. **The Ø14 × 1 mm hollow front output is dropped.** Every Ø14 bore becomes a **round Ø8.35** bore running free on the Ø8 mainshaft: `v1_CD_SideF`, `v1_ModeHub`, `Dog_m1.25_N20`. With the tube gone, nothing carries torque from the front side gear through the mode hub. **Do not model that link.** List it as an open item for the user.
4. **Lock set** (`v1_LockDog`, `v1_LockHub`, `v1_LockCollar`): teeth unchanged, bores only where a bore exists. `v1_LockCollar` is not touched at all.
5. **Fits:** a part locked to its shaft gets a D-bore: **Ø8.15 round, 7.65 across the flat as cut**. A part that spins on its shaft gets a **round Ø8.35** bore.
   - **Shaft across-flat: 7.5 mm** (a 0.5 mm deep flat). This is a proposal, not a project spec. Gear Generator's README calls 7.0 the common 8 mm D-shaft. If the user has changed this line before the run, use their value: the D-bore across-flat as cut is that value + 0.15.
6. **This repo is the working copy.** Edit files in place here. The baseline commit is the backup (`git restore` a file to undo it).
7. **Planets** keep no bore (they ride Ø3 pins; out of scope). **Sprockets** are not Gear Generator parts; leave them alone.

## Prerequisites (check first; stop and tell the user if any is missing)
- SolidWorks 2024 running, the only instance.
- Gear Generator, branch `workbook` at or after 046aa35 (github.com/M0ooBot/SW-Gear-Generater). It must have Process **Printed** (the default), **Bore allowance** and **Drive: Round / Flat**. Read its README sections *Changing a built gear*, *Printed gears* and *The bore* before using it.
- The SW-Agent plugin (`sw_status` works).
- Windows Python with pywin32 for native COM.

## Step 0: references must resolve inside this repo
The SolidWorks files still store absolute paths into `C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\`. If that folder exists on this machine (OneDrive may sync it), SolidWorks can load v1 parts into the v2 assemblies.
- With every document closed, repoint each v2 assembly's references to their v2 twins (`ISldWorks.ReplaceReferencedDocument` works on closed files), or confirm that no `v1-chassis` folder exists on this machine.
- Then open the top assembly and assert that every component's `GetPathName` (recursively) lies under this repo's root. Stop if any does not.
- The `.gear.json` and `.workbook.json` records were rewritten to `...\MIE243\v2-chassis\...`. If this repo lives somewhere else, rewrite those paths to the real location before opening a record in Gear Generator.

## Step 1: survey, read-only, before any change
- The component tree and configurations of every assembly above.
- For each gear part: its feature tree against the `"features"` list in its `.gear.json`. Anything extra is a **custom feature that must survive**. Known custom work: the planet carrier in `v1_LoDog`; `v1_RangeSleeve` (copy of Sleeve_m1.25_N17, Face Width 26, Ø26 relief Z 5–21); `v1_RangeHub` (copy of v1_InDog, Face Width 20, mainshaft section); `v1_ModeHub` (copy of Dog_m1.25_N20, Face Width 9); `v1_CD_SideF` (copy of v1_CD_Side); the lock parts. Parts copied this way have **no `.gear.json`** but carry Gear Generator's globals.
- **Measure what each bore actually runs on** in the assembly (the mating shaft's cylinder, concentric mates), and whether the part turns with that shaft or spins on it. If a shaft is not Ø8, or locked versus free is unclear, stop and ask. **`v1_LoDog` has a Ø10 bore: find out what runs in it**, and whether 10 was meant for a bushing, before changing it.
- **Record baseline numbers** to compare against later: mate errors and warnings per assembly; interference volume per configuration (TC 2H/4H/N/4L; centre diff Open/Locked; chassis Default and Demo 4H straight); sleeve positions.

## Expected fits (a starting hypothesis; Step 1 confirms or corrects every row)
| Part | Used as | Kind | Bore now | Expected | How |
| --- | --- | --- | --- | --- | --- |
| `Gear_m1.25_N29` | Sun, input shaft | spur 29T m1.25 | 8 | **D 8.15 / 7.65** | Printed in place; D-flat (see Step 3) |
| `Gear_m1.25_N13` ×3 | Planets on Ø3 pins | spur 13T | – | Printed only | in place |
| `Ring_m1.25_N55` | Ring, fixed | internal 55T | – | Printed only | in place |
| `v1_InDog` | High dog + input stub | dog 17T | (shaft built in) | Printed teeth; shaft untouched | in place |
| `v1_LoDog` | Low dog + carrier | dog 17T | 10 | likely **round 8.35**; verify | in place |
| `v1_RangeHub` | Range hub + mainshaft | hub 17T | (shaft built in) | Printed teeth; shaft untouched | globals (no record) |
| `v1_RangeSleeve` | Range sleeve | internal 17T | – | Printed only | globals (no record) |
| `Sleeve_m1.25_N17` | check whether it is still in any assembly | internal 17T | – | Printed only, if used | in place |
| `v1_ModeHub` | Mode hub | hub 20T | 14 | **round 8.35** | globals (no record) |
| `Dog_m1.25_N20` | Front dog on the drive sprocket | dog 20T | 14 | **round 8.35** | in place |
| `Sleeve_m1.25_N20` | Mode sleeve | internal 20T | – | Printed only | in place |
| `v1_CD_Side` | Centre diff side, rear output | bevel 18T m2.5 | 8 | **D 8.15 / 7.65** | Printed in place; native D-flat |
| `v1_CD_SideF` | Centre diff side, front | bevel 18T m2.5 | 14 | **round 8.35** | globals (no record) |
| `v1_CD_Spider` ×2 | Spiders on the cross pin | bevel 12T m2.5 | 8 | **round 8.35** | in place |
| `v1_FD_Pinion` (front + rear) | Pinion on the driveshaft | bevel 15T m2.25 | 8 | **D 8.15 / 7.65** | Printed in place; native D-flat |
| `v1_FD_Ring` (front + rear) | Ring, bolts to diff case | bevel 30T m2.25 | – | Printed only | in place |
| `v1_AX_Side` (×4 uses) | Axle side gears on the half-shafts | bevel 18T m1.75 | 8 | **D 8.15 / 7.65** | Printed in place; native D-flat |
| `v1_AX_Spider` (×4 uses) | Spiders on the cross pin | bevel 12T m1.75 | 8 | **round 8.35** | in place |
| `v1_LockDog` | Lock dog (free, joins future case) | dog 20T | check | bore only, if it has one | – |
| `v1_LockHub` | Lock hub, keyed to rear side gear | hub 20T | (shaft built in) | untouched | – |
| `v1_LockCollar` | Lock sleeve | internal 20T | – | **do not touch** | – |

All bevel pairs are module 1.75 or larger, so Gear Generator's bevel warning below module 1.6 does not apply. Bevel profile shift stays 0 (the app applies Gleason addendum itself).

## Step 2: Printed regeneration (keep tooth count, module, pressure angle, position, custom features)
- **Preferred: in place.** Gear Generator → Open .gear.json → with that part active, set Process = Printed → **Update values**. This keeps the file, its name, its custom features and every mate that references it. Making a built machined part printed through Update keeps its file and name.
- **Parts with no record** (`v1_RangeHub`, `v1_RangeSleeve`, `v1_ModeHub`, `v1_CD_SideF`): first confirm exactly which globals Printed changes, by comparing what Update did to a recorded part of the same kind. Then set those globals in the Equation Manager (the README says this "works just as well"). The printed backlash default is `IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )`.
- Only where the in-place route is refused **and** the change matters, build a new part individually (output folder set explicitly), re-add the custom features, and swap it in with Replace Components. New printed builds default to a `_P` file name. Either accept that and replace the component, or type the original name into a staging folder. Never overwrite a file in place by copying over it.

## Step 3: bores
- Update values refuses to add a Bore allowance to a part built without one, and refuses to change Drive. Two routes:
  - **(a) In place (preferred):** set `"Bore Diameter"` to the as-cut size (8.35 or 8.15). The record then says "bore 8.35, no allowance" rather than "8 + 0.35": note that in the report.
  - **(b) A new build** with Bore 8, Bore allowance 0.35 or 0.15, and Drive Flat (spur only), then Step 2's replacement procedure.
- **D-flats on spur gears and on every bevel** (the app cuts no flat on a bevel): add a native SolidWorks cut, named `D-Flat`, after the bore feature. The flat plane sits at 7.65 − 8.15/2 = **3.575 mm from the axis**, through the full length of the bore. Put it where Gear Generator puts its flats: on the gear's +X side, square to X, facing the middle of a tooth space. Then every gear's flat has a known phase. The app's assembly does not model flats, so check that no loop of meshes between D-fixed gears is now over-constrained.
- Keep any wall thickness warning in view: the bore must stay well inside the root circle and the hub.

## Step 4: fit into the assemblies
Rebuild each affected sub-assembly bottom-up. If parts were edited in place, the mates should survive. Re-attach any mate that dangles; do not delete working mates. Gear positions must not move (notebook 2026-11-22).

## Step 5: verify (compare with the Step 1 baseline)
- Every component path is under the repo root; nothing missing, nothing suppressed by error, nothing lightweight.
- **Mate errors and warnings** per assembly. Known noise: SolidWorks 2024 code-51 warnings on gear-linked mates after drags. Old 1:1 gear mates between coaxial parts are **intentionally suppressed** (replaced by locked-rotation concentrics); they are not dangling.
- **Interference** per configuration, against the baseline. Teeth in mesh must show no interference now that backlash is printed.
- **Differential motion:** centre diff Open behaves as a differential (carrier held, side gears counter-rotate; carrier turned, sides follow); Locked moves as one body. Axle diffs: note that they are currently locked by a Concentric1 lock-rotation mate (the user's decision) and test the gear train through them.
- **Transfer case:** every config rebuilds; sleeves sit where they did; ratios 4H 1:1 and 4L carrier ÷2.897 (1 + 55/29).
- **Measured bores:** for each changed part, the cylinder diameter and the across-flat distance as built.
- Save, close everything, reopen the top assembly from disk, and repeat the reference and mate checks.

## Stop and ask the user when
- a bore runs on something that is not Ø8, or locked versus free is unclear;
- the only route would drop a custom feature, or move a gear;
- a mate cannot be re-attached cleanly;
- a step would need `v1_LockCollar`, or a workbook Build or Update.
If one interface is blocked, carry on with the independent work and report exactly what remains.

## Known state before this run (as of 2026-11-16; confirm, do not "fix")
- In 4H/N/4L the mode sleeve's rear rim overlaps about 13 chain links (~26 mm³). Proposed fix, not chosen: a 4 mm spacer collar on the sprocket dog.
- In the full chassis motion, 4L turns backwards (the sense of the planet–ring mesh), so there is no 4L demo.
- No rotational key yet between the sprocket dog and the drive sprocket in the transfer case.
- About 1% U-joint wobble at the front wheels when steered.
- Materials are not assigned. The workbooks no longer match the assemblies.

## Report (write `REPORT-v2-gears.md` at the repo root, and summarise it to the user)
- Path to the revised top assembly.
- Per part: before and after for Process, backlash, bore, drive / flat, and the route used (in place, globals, or new build), with every custom feature kept.
- Verification: each check above with its numbers, against the baseline.
- Open items: the front-output torque link (decision 3), anything blocked, anything that needs the user's word.
- Do not commit unless the user asks.

## Reference
- `docs/notebook/`: the notebook entries this work depends on (gear specs and positions, BOM, 11-22 conventions, 11-24 CAD details).
- `tools/reference/`: helper scripts from the v1 build (Gear Generator drivers, fit and interference checks, mate and DOF probes, a persistent COM worker). Their paths point at the original machine; use them as examples, not as-is.
