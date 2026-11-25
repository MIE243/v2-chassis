---
date: 2026-11-22
authors:
  - Mo Zhou
sprint: 3
commits: []
tags:
  - v2-cad
---
## List of work left in CAD 
- Differential cases
	- Might interfere with shaft support and chassis design
	- Must require gears to be final before this can begin
- Shaft supports (ball bearings etc.)
- Stand for the car as speced in CD3
	- Requires chassis to be designed
- How the sleeves actually get ran/moved
	- Require gears to be final
- Chassis for the whole car
	- This could possibly be done together with shaft supports in one step?
- Proper shaft design and redoing gear designs to allow for gear locks etc. (like D shafts or something like that)
	- This might have to be built first before any other work can begin, TBD if this can run along others
- Detailed wheels
- Proper sprockets CAD
- How the input shaft is connected to the motor
	- Maybe through an adapter?
- IF MODULAR
	- Specific design for each of the modules
## What comes after CAD is done
- Engineering drawings
- Bill of materials
## Important notes before splitting work
- Design around the same origin point
- Differential case designs must use the empty file that already exists for them
- The entire geartrain stays locked no gears are allowed to be changed especially in position
- Empty parts should be created in assembly with proper mate to origin already. Work should be done in those sub parts/sub assemblies only to avoid merge conflicts
## Open Questions
- Still do modularity?
	- Decided yes in meeting

## Conventions
- Screws
	- Use toolbox screws ANSI Metric
- Nuts 
	- Use toolbox ANSI Metric
- Ball Bearings
	- TBD McMaster-Carr standard ball bearings
- Shaft collars
	- Probably don't need?
	- If needed take from McMaster-Carr
- Heat Set Inserts
	- Get from McMaster-Carr
	- For each screw size use standard across all screws of same size
- Washers and Spacers
	- Get from McMaster-Carr
- Anything else
	- TBD

## Tolerance Conventions
- TOLERANCES ARE OFFSETS OUTWARDS
- Attachment: 0.15 mm 
	- For parts that rotate together consider making them print attached together
- Spinning: 0.35 mm