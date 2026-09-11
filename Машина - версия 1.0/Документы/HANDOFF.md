# Van de Stadt 67 ft — Research & Engineering Handoff

## Project objective
Build a traceable engineering knowledge base for the Polish aluminium Van de Stadt 67 ft hull, believed to correspond to Van de Stadt Design No. 430, and use it as the factual foundation for completion/refit engineering, equipment selection, weight control, layout decisions and budgeting.

The repository is not a generic yacht-spec collection. The target is to reconstruct as much of the actual design intent and physical configuration as possible, then distinguish that evidence from reference-yacht solutions and from new engineering proposals.

## Premium-class build direction
The completion target is now explicitly **premium-class bluewater yacht**, not a minimum viable completion and not a basic production-yacht fit-out.

Use Oyster 675, Contest 67CS and comparable high-spec custom aluminium yachts from KM Yachtbuilders/Bestevaer and other respected 65–75 ft builders as benchmarks for systems architecture, redundancy, hotel comfort, acoustic treatment, maintainability and finish.

A provisional builder-style target specification is maintained in `docs/16-premium-builder-specification.md`. Treat it as the design brief to test against the real Polish drawings.

Owner-defined baseline requirements currently include:
- main engine target 300 hp;
- two compact marine generator sets around 11.5–12 kVA each;
- two independent chilled-water chiller modules;
- one fan-coil unit per conditioned cabin/space as a design rule;
- 150 L/h watermaker;
- redundant freshwater pressure architecture: 24 VDC pump + 230 VAC pump, with dedicated 24→230 V inverter backup for the AC pump;
- electric toilets selectable between potable-tank freshwater and dedicated seawater flushing, both normally discharging to black-water holding tanks;
- three principal guest cabins: Master, forward VIP and side guest cabin;
- one compact convertible ensuite cabin with twin lower berths convertible to a double plus optional folding upper berth;
- TV in all guest cabins and saloon;
- premium centrally managed multi-zone audio, Sonos-style architecture or superior marine-integrated equivalent;
- two complete helm stations;
- target per helm: four approximately 20-inch-class primary navigation/MFD displays plus four dedicated instrument displays, controls and system monitoring;
- premium digital monitoring/switching while preserving local/manual operation of critical services;
- strong redundancy, acoustic isolation and serviceability throughout.

These are `PROVISIONAL DESIGN TARGETS` until checked against actual hull geometry, weights, stability and electrical/hydraulic loads.

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
Search archived brokerage listings, downloadable sale brochures, PDFs, cached pages and yacht databases. Extract equipment-level data: engine, gearbox, shaft/propeller, generators, AC/DC architecture, batteries, thrusters, steering, tankage, watermaker, HVAC, sanitation, bilge/fire, rig, deck hardware, windlass/anchors, navigation, domestic equipment and tender handling. Preserve source/date for each value.

### 4. Study premium 65–75 ft yachts as engineering benchmarks
The reference pool is broader than Van de Stadt alone. Prioritise:
- Van de Stadt 65–77 ft aluminium yachts for structural/design lineage;
- Oyster 675 for premium bluewater hotel/system integration;
- Contest 67CS for 24/230 V architecture, technical-room arrangement, redundant water services, 150 L/h watermaker, chiller HVAC and high-end accommodation;
- KM Yachtbuilders/Bestevaer for aluminium custom-yacht structure, autonomy, watertight integrity and machinery integration;
- other credible premium/custom 65–75 ft sailing yachts where a detailed builder/broker specification is available.

For every reference solution, record yacht, builder, year, displacement and source. Never copy equipment blindly: assess suitability for the heavier No. 430 hull and owner-defined premium brief.

### 5. Image-based reconstruction
Collect useful photographs of confirmed/probable sister or reference yachts, especially engine room, bilges, keel interior, steering gear, shaft line, tanks, mast step, chainplates, thruster, electrical panels, generators, cockpit/deck hardware, anchor locker and technical spaces. Mark inferred relationships as `REFERENCE` or `PROVISIONAL`.

## Polish hull drawing ingestion
The owner will provide the available drawings for the actual Polish hull in chat.

When drawings arrive:
1. Inventory every sheet/file before interpreting it.
2. Record file name, drawing title/number, revision, date, scale, author/builder and sheet size where visible.
3. Determine provenance.
4. Extract explicit dimensions/specifications before visual estimates.
5. Cross-reference repeated dimensions and flag inconsistencies.
6. Map stations/frames/bulkheads into one longitudinal coordinate system where possible.
7. Extract material grades, plate thicknesses, profiles, weld notes and structural details.
8. Reconstruct hull/deck/deckhouse structural arrangement.
9. Locate/dimension machinery spaces, engine beds, shaft line, rudder/steering, tanks, mast step, chainplates, thruster provision and service routes.
10. Extract GA/interior dimensions and usable equipment envelopes.
11. Compare drawing-derived values against repository matrix and premium target specification.
12. Replace assumptions with `CONFIRMED-HULL` only where genuinely supported.
13. Keep unresolved discrepancies in a conflict register.
14. Preserve originals unchanged.

## Derived engineering outputs from drawings
Produce progressively: master dimensions; frame/bulkhead table; plate/scantling and structural schedules; tank register; machinery envelope; propulsion and steering geometry; rig-foundation register; deck-hardware foundations; openings register; equipment-space map; weight ledger; design-displacement reconciliation; operating/full-load mass model; unresolved survey list.

Additionally, perform a **fit/gap analysis against `docs/16-premium-builder-specification.md`**. For every premium target system mark:
- FITS AS DRAWN;
- FITS WITH LOCAL MODIFICATION;
- STRUCTURAL MODIFICATION REQUIRED;
- SPACE CONFLICT;
- WEIGHT/STABILITY REVIEW REQUIRED;
- ELECTRICAL/HYDRAULIC CAPACITY REVIEW REQUIRED;
- NOT YET DETERMINABLE.

## Weight-control rule
Do not force current public/source values to reconcile. Maintain separate weights for bare/current hull, aluminium structure, ballast, machinery, tanks, fluids, rig, deck gear, batteries/electrical, HVAC/plumbing, interior, safety/navigation/domestic equipment, stores/crew and design displacement.

Premium equipment adds substantial weight. The 300 hp propulsion plant, two generators, dual chillers, lithium bank, large bridge electronics, AV, watermaker and high-end interior must all be included early in the longitudinal/vertical weight model.

## Future equipment-selection workflow
Do not select equipment solely by LOA. Sequence:
1. geometry/displacement target;
2. foundation, access and removal envelopes;
3. duty/load requirement;
4. mass and CG effect;
5. 2–5 realistic premium candidates;
6. compare dimensions, dry/wet mass, service access, consumption, acoustic data, compatibility, redundancy, service network and price;
7. select only after integration checks.

## Repository structure going forward
Keep existing system documents and add:
- `drawings/original/`
- `drawings/index.md`
- `docs/09-structural-scantlings.md`
- `docs/10-weight-budget.md`
- `docs/11-tank-register.md`
- `docs/12-machinery-integration.md`
- `docs/13-rig-foundations.md`
- `docs/14-equipment-selection.md`
- `docs/15-conflict-register.md`
- `docs/16-premium-builder-specification.md`
- `data/dimensions.csv`
- `data/frames-bulkheads.csv`
- `data/tanks.csv`
- `data/weights.csv`
- `data/equipment.csv`

## End goal
The repository should eventually answer with traceable evidence:
- What exactly was Van de Stadt No. 430 designed to be?
- What exactly has already been built in Poland?
- What differs between original design and Polish hull?
- What spaces, foundations and structural provisions exist?
- What is the real weight/displacement/ballast picture?
- Can the full premium-class target specification be integrated safely?
- What must be redesigned or structurally modified?
- What exact equipment package is selected?
- What are the final weight, power, hotel-load and build budgets?

The owner's Polish-hull drawings become the highest-priority source for the next phase.