# Original request (verbatim, 2026-11-24)

Superseded where it differs by the decisions in [../RUN-BRIEF.md](../RUN-BRIEF.md): the run works in place in this repo (no separate working copy), uses SolidWorks 2024, gears take priority over shafts, and the Ø14 hollow output is dropped.

---

Revise the entire v1 chassis drivetrain in SolidWorks. Work from this repo and assembly:

C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis
v1 Chassis Assembly.SLDASM

Use SW-Agent where it supports the operation. For missing operations, use the Gear Generator backend and native SolidWorks COM directly from Windows in a dedicated STA thread, where your environment permits. Switch to that route if SW-Agent lacks a capability. Keep mouse and keyboard control off.

Create a separate working copy of the chassis with its dependencies. Use the existing transfer case and front, center, and rear differential assemblies as the baseline. Consult the MIE243 Engineering Design Notebook, especially “2026-11-16 v1 Chassis Gear Specs and Positions” and “2026-11-24 CAD Details,” plus the original `.gear.json` records and workbooks.

- Regenerate all Gear Generator drivetrain gears using the **Printed** preset. Keep their tooth counts, modules, pressure angles, and intended shaft positions. Build replacement gears individually where needed and fit them into the existing assemblies. Preserve any custom features added after generation.
- Convert the drivetrain shafts to D-shafts. Where a gear or hub turns with the shaft, use a matching D-bore with **+0.15 mm diametral allowance**. Where a part spins freely on the shaft, keep the bore **circular** and use **+0.35 mm diametral allowance**. For an 8 mm shaft, those are 8.15 mm and 8.35 mm respectively.
- Verify each fit from the actual assembly. The project documents Ø8 mm shaft stock, a Ø14 mm hollow front output with a 1 mm wall, and a Ø10 mm low-range dog bore. Confirm what each bore runs on. Find the across-flat dimensions in the project or measure existing geometry. If they are unspecified, propose dimensions and flag the Ø14 mm tube-end design before committing it. Gear Generator supports bevel bore allowance, but a shaft-locked bevel gear needs a separate native D-flat feature or a hub.
- Replace the affected components in the working copy. Rebuild, reopen, and check resolved references, dangling mates, interference, differential motion, and the transfer-case shift and lock configurations.

Do the CAD work and return the path to the revised assembly, a concise list of changes, and what you verified. If a specific design decision blocks one interface, continue with the independent work and report exactly what remains.
