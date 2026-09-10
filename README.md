# Van de Stadt 67 ft — Project Technical Base

Engineering research repository for the future completion/refit/design study of the Van de Stadt 67 ft aluminium deck-saloon yacht, based primarily on Van de Stadt Design project No. 430 and the current unfinished hull in Gdansk, Poland.

## Working rule
Every technical value must be tagged by confidence:

- **CONFIRMED-430** — published by Van de Stadt Design for project No. 430.
- **CONFIRMED-HULL** — published for the current Gdansk aluminium hull.
- **REFERENCE** — taken from a closely related Van de Stadt aluminium cruising yacht, useful for engineering comparison but not evidence of the original No. 430 specification.
- **PROVISIONAL** — an engineering starting point for the future project; must be recalculated/approved.
- **TO-MEASURE** — must be physically measured or recovered from original drawings.

## Core dimensions

| Item | Value | Status |
|---|---:|---|
| Designer | Van de Stadt Design | CONFIRMED-430 |
| Design No. | 430 | CONFIRMED-430 |
| Design year | 1992 | CONFIRMED-430 |
| Type | Comfortable cruising yacht with deck saloon | CONFIRMED-430 |
| Hull material | Steel or aluminium | CONFIRMED-430 |
| LOA | 20.50 m | CONFIRMED-430 / HULL |
| LWL | 17.50 m | CONFIRMED-430 / HULL |
| Beam | 5.50 m (design list) / 5.75–5.80 m current hull listings | CONFLICT — VERIFY |
| Draft | 2.50 m original design / 2.8–3.0 m current hull listings | CONFLICT — VERIFY |
| Original design displacement | 51 t | CONFIRMED-430 |
| Original design ballast | 19 t | CONFIRMED-430 |
| Current unfinished hull dry weight | 11 t | CONFIRMED-HULL listing |
| Current hull ballast | 15 t | CONFIRMED-HULL listing; VERIFY physically |
| Total sail area | 241 m² | CONFIRMED-430 / HULL |
| Mainsail area | 131 m² | CONFIRMED-HULL listing |
| Headsail area | 110 m² | CONFIRMED-HULL listing |
| Max bridge clearance / air draft | approx. 32 m | CONFIRMED-HULL listing |
| Freeboard | approx. 1.8 m | CONFIRMED-HULL listing |
| Cabin headroom | approx. 2.0 m | CONFIRMED-HULL listing |
| Guest cabins | 3 | CONFIRMED-HULL listing |
| Guest heads | 3 | CONFIRMED-HULL listing |
| Fuel tanks | 2 | CONFIRMED-HULL listing; capacities unknown |
| Fresh-water tanks | 2 | CONFIRMED-HULL listing; capacities unknown |
| Black-water tanks | 1 | CONFIRMED-HULL listing; capacity unknown |

## Repository structure

- `docs/01-hull-geometry-weights.md` — dimensions, displacement, ballast, hull questions.
- `docs/02-rig-sails-deck.md` — mast, rig, sail plan, winches, anchoring/deck systems.
- `docs/03-propulsion-steering.md` — engine, shaft, propeller, steering, thruster.
- `docs/04-electrical-generation.md` — DC/AC architecture, alternators, batteries, generator, shore power.
- `docs/05-tanks-plumbing-hvac.md` — fuel/water/black/grey water, watermaker, hot water, HVAC.
- `docs/06-layout-interior-machinery.md` — accommodation, machinery spaces, access and serviceability.
- `docs/07-reference-yachts.md` — comparable Van de Stadt aluminium yachts and transferable engineering lessons.
- `docs/08-open-questions-survey.md` — physical survey and original-document acquisition checklist.
- `sources/SOURCES.md` — source register and confidence notes.

## Known high-value comparison yacht
The 2008 **Van de Stadt Stadtship 70** (21.0 m aluminium, design No. 670) is close enough in length and mission to be a useful systems reference. Published specifications include Perkins Sabre M150Ti 148 hp, ZF45A gearbox, 50 mm shaft, 4-blade folding propeller, Onan 7.5 kVA generator, 24 V 1000 Ah service bank, 12/24/220 V systems, 1150 L fuel, up to 3500 L water including wing/water-ballast tanks, 300 L waste tank and Spectra Newport 400 watermaker (64 L/h). **These are REFERENCE values only, not No. 430 equipment.**

## Immediate engineering priorities
1. Obtain/scan original Van de Stadt No. 430 drawings and calculation package if available.
2. Survey current hull: frames/stringers, plating, welds, keel, rudder, shaft line provisions, engine beds, tank boundaries, mast step/compression structure, chainplate structure and watertight bulkheads.
3. Establish real lightship mass by weighing or verified build records.
4. Establish ballast material, location and actual mass.
5. Freeze intended operational profile before equipment sizing: offshore cruising, crew level, autonomy, climate, target cruising speed, electrical hotel load and tender/toy requirements.
6. Build a weight-and-centre budget before choosing machinery and interior materials.

## Sources
Primary and comparison sources are recorded in `sources/SOURCES.md`. No unverified marketplace value should be treated as a design-office value without an explicit tag.

## Проектно-сметный офис / Project & estimating office

10.09.2026: добавлена общая операционная основа для будущей команды достройки яхты. Начать с [хендофа начальнику](office/HANDOFF-TO-HEAD.md), затем [карты офиса](office/README.md). Правила для исполнителей — [AGENTS.md](AGENTS.md). Исходная техническая база и её статусы сохранены; отраслевую специализацию выполнит будущая команда.
