# Van de Stadt 67 ft — Research & Engineering Handoff

## Project objective
Build a traceable engineering knowledge base for the Polish aluminium Van de Stadt 67 ft hull, believed to correspond to Van de Stadt Design No. 430, and use it as the factual foundation for completion/refit engineering, equipment selection, weight control, layout decisions and budgeting.

The repository is not a generic yacht-spec collection. The target is to reconstruct as much of the actual design intent and physical configuration as possible, then distinguish that evidence from reference-yacht solutions and from new engineering proposals.

## Evidence classes
Every technical statement should carry one of these statuses:

- `CONFIRMED-430` — directly supported by original Van de Stadt Design No. 430 documentation.
- `CONFIRMED-HULL` — directly supported by drawings, measurements, photographs, builder/seller documentation or physical inspection of the Polish hull.
- `REFERENCE` — solution/data from another identified yacht, preferably Van de Stadt 65–77 ft and especially aluminium yachts of similar displacement/layout.
- `PROVISIONAL` — engineering assumption or candidate solution for the future build.
- `TO-MEASURE` — cannot be established reliably without a measurement/inspection of the Polish hull.
- `CONFLICT` — two or more credible sources disagree; preserve all values and resolve later.

Never silently promote `REFERENCE` or `PROVISIONAL` data to the actual No. 430 specification.

## Immediate research programme

### 1. Recover original Design No. 430 documentation
Search specifically for original or derivative material associated with Van de Stadt Design No. 430, not merely pages containing the words “Van de Stadt 67”. Target:

- general arrangement / GA;
- lines plan / body plan / sheer plan / half-breadth;
- construction plan;
- frame/station plan and spacing;
- shell plating plan and plate thicknesses;
- deck and deckhouse structure;
- longitudinal/stringer arrangement;
- bulkhead positions and scantlings;
- keel structure and ballast arrangement;
- rudder, stock, bearings and steering geometry;
- engine-bed / machinery-space drawings;
- shaft-line geometry, stern tube and P-bracket if applicable;
- tank plans and capacities;
- sail plan and rig dimensions;
- mast step, chainplates and rig-load structure;
- deck hardware positions and reinforcement;
- accommodation/interior layout;
- plumbing/electrical/system diagrams if any;
- stability, hydrostatics, weight estimate, centres of gravity and design displacement;
- drawing index, revision numbers, dates and designer notes.

Record drawing number, title, revision/date, scale and provenance for every recovered drawing.

### 2. Identify actual completed Van de Stadt 67 / No. 430 yachts
Do not rely only on model-name searches. Work backwards from hull geometry, designer/project number, old sale listings, registries, builders, yacht names and photographs.

For each candidate completed yacht, establish whether it is:

1. confirmed Design No. 430;
2. probable No. 430;
3. another Van de Stadt 67;
4. only a dimensional/reference analogue.

Capture yacht name, year, builder, hull material, LOA/LWL/beam/draft/displacement/ballast and all available technical particulars.

### 3. Recover historical brokerage particulars
Search archived brokerage listings, downloadable sale brochures, PDFs, cached pages and yacht databases. The objective is equipment-level data that normally disappears from short listings:

- main engine make/model/power/year/hours;
- gearbox and ratio;
- shaft diameter/material;
- propeller make/type/diameter/pitch;
- exhaust arrangement;
- generator make/model/kVA;
- shore power, isolation transformer and charger/inverter architecture;
- battery banks and capacities;
- alternators;
- bow/stern thrusters;
- steering system and autopilot drive;
- fuel/fresh/grey/black-water capacities;
- pumps and watermakers;
- hot-water system;
- HVAC/heating;
- bilge and fire systems;
- mast/boom manufacturer and materials;
- standing rigging dimensions/material;
- furlers;
- winches and deck hardware;
- windlass, anchors and chain;
- navigation/electronics;
- domestic equipment;
- tender/garage/davit solutions where relevant.

Preserve the source and date for each value.

### 4. Study real Van de Stadt 65–77 ft aluminium yachts as engineering references
Use nearby Van de Stadt designs to reconstruct plausible engineering ranges where No. 430 data is absent. Prioritise yachts close in displacement and intended service, not simply close in LOA.

Extract:

- machinery-room layout;
- engine power and installation envelope;
- gearbox/shaft/propeller sizing;
- generator sizing;
- tankage and tank location;
- battery-bank mass and position;
- hydraulic systems;
- steering architecture;
- bow-thruster installation;
- rig and deck hardware;
- service access;
- ventilation;
- watermaker/HVAC placement;
- anchor handling;
- interior arrangement and technical voids.

Keep these as `REFERENCE` until supported by the Polish hull/original drawings.

### 5. Image-based reconstruction
Collect useful photographs of confirmed/probable sister or reference yachts, especially:

- engine room;
- bilges;
- keel interior;
- rudder quadrant/steering gear;
- shaft line;
- tanks;
- mast step;
- chainplates;
- bow-thruster tunnel;
- electrical panels;
- generator;
- cockpit/deck hardware;
- anchor locker;
- deckhouse/interior bulkheads.

Use photographs to infer arrangement only when geometry is visible. Mark inferred dimensions/relationships as `REFERENCE` or `PROVISIONAL`, never confirmed.

## Polish hull drawing ingestion
The owner will provide the available drawings for the actual Polish hull in chat.

When drawings arrive:

1. Inventory every sheet/file before interpreting it.
2. Record file name, drawing title/number, revision, date, scale, author/builder and sheet size where visible.
3. Determine whether each drawing is original Van de Stadt, builder production documentation, later modification, sales documentation or unknown provenance.
4. Extract all explicit dimensions and specifications before making visual estimates.
5. Cross-reference repeated dimensions between drawings and flag inconsistencies.
6. Map stations/frames/bulkheads into one longitudinal coordinate system where possible.
7. Extract material grades, plate thicknesses, profiles, weld notes and structural details.
8. Reconstruct the actual hull/deck/deckhouse structural arrangement.
9. Locate and dimension machinery spaces, engine beds, shaft line, rudder/steering, tanks, mast step, chainplates, thruster provision and major service routes.
10. Extract GA/interior dimensions and usable equipment envelopes.
11. Compare drawing-derived values against the existing repository matrix.
12. Replace assumptions with `CONFIRMED-HULL` values only where the drawings genuinely support them.
13. Keep unresolved discrepancies in a dedicated conflict register.
14. Do not alter or “clean up” original source drawings. Store originals separately from derived notes/data.

## Derived engineering outputs from the drawings
After drawing ingestion, produce progressively:

- master dimensions table;
- station/frame/bulkhead table;
- plate/scantling schedule;
- structural member schedule;
- tank register with geometry, estimated/declared volume and longitudinal position;
- machinery-space envelope;
- propulsion geometry sheet;
- rudder/steering geometry sheet;
- rig foundation / mast-step / chainplate register;
- deck-hardware foundation register;
- openings/hatches/ports register;
- equipment-space/envelope map;
- weight ledger by system and longitudinal position;
- known-weight vs design-displacement reconciliation;
- preliminary lightship/operating/full-load mass model;
- unresolved measurement list for the next physical hull survey.

## Weight-control rule
The current public/source values contain a major unresolved discrepancy: original No. 430 design displacement and ballast values do not directly reconcile with the advertised/current Polish-hull mass and ballast figures. Do not force these numbers to agree.

Maintain separate columns for:

- bare/current hull mass;
- aluminium structure;
- ballast actually installed;
- machinery;
- tanks dry;
- fluids;
- rig;
- deck gear;
- electrical/batteries;
- HVAC/plumbing;
- interior/joinery;
- safety/navigation/domestic equipment;
- stores/crew/operating load;
- design displacement.

The drawings and later weighing/survey data should resolve the mass model.

## Future equipment-selection workflow
Do not select equipment solely by LOA. For each major system, first establish the actual constraints from drawings and calculations.

Sequence:

1. establish geometry and displacement target;
2. establish space, foundation and access envelopes;
3. establish duty/load requirement;
4. establish mass and centre-of-gravity effect;
5. identify 2–5 realistic modern candidates;
6. compare dimensions, dry/wet weight, service access, power/fuel/electrical demand, compatibility and price;
7. select a preferred solution only after integration checks.

This applies especially to main engine, gearbox, shaft/propeller, generator, batteries, thruster, steering/autopilot, windlass, rig, winches, watermaker, HVAC and pumps.

## Repository structure going forward
Keep the existing system documents. Add as information becomes available:

- `drawings/original/` — source drawings supplied by owner (when repository/file tooling permits binary storage)
- `drawings/index.md` — drawing register and provenance
- `docs/09-structural-scantlings.md`
- `docs/10-weight-budget.md`
- `docs/11-tank-register.md`
- `docs/12-machinery-integration.md`
- `docs/13-rig-foundations.md`
- `docs/14-equipment-selection.md`
- `docs/15-conflict-register.md`
- `data/dimensions.csv`
- `data/frames-bulkheads.csv`
- `data/tanks.csv`
- `data/weights.csv`
- `data/equipment.csv`

## End goal
The repository should eventually answer, with traceable evidence:

- What exactly was Van de Stadt No. 430 designed to be?
- What exactly has already been built in Poland?
- What differs between the original design and the Polish hull?
- What spaces, foundations and structural provisions actually exist?
- What is the real weight/displacement/ballast picture?
- What equipment can physically and technically be integrated?
- What must be designed or modified before completion?
- What is the resulting equipment list, weight budget and build budget?

The owner's Polish-hull drawings become the highest-priority source for the next phase.