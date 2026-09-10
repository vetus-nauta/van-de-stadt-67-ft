# 04 — Electrical, Generation & Energy Architecture

## Status

No original No. 430 electrical specification has been located publicly. The current unfinished hull has no published installed generation package.

## Closest published reference: Stadtship 70

| Item | Reference installation |
|---|---|
| DC/AC systems | 12 / 24 / 220 V |
| Main service bank | 24 V, 1000 Ah |
| Engine start battery | 12 V, 55 Ah |
| Navigation/light battery | 12 V, 200 Ah |
| Generator start battery | 12 V, 55 Ah |
| Main alternator | Mastervolt 120 A |
| Genset | Onan 7.5 kVA |
| Inverter/charger | Mastervolt Combi Ultra 24/3500-100 |
| Battery charger | Mastervolt IVO Smart 12 V |
| Shore isolation | 3 × Mastervolt Mass GI 3.5 isolation transformers |
| Hydrogeneration | fixed Watt & Sea unit below hull |

**REFERENCE only.** This provides a useful architecture benchmark, not a target bill of materials.

## Future-project architecture to evaluate

### DC bus
A 24 V house system is a logical baseline for a 20.5 m yacht because it reduces current and cable size for large DC consumers compared with 12 V. A 48 V subsystem may be worth studying for high-power consumers, but only if system integration, spares availability and isolation are properly engineered.

### Battery chemistry
Compare:

- LiFePO4 house bank with proper BMS, contactors, temperature protection and alternator control.
- AGM/lead-acid dedicated engine/generator starts.
- Independent emergency/communications supply where required.

Do not size batteries by nominal Ah alone. Build a 24-hour energy balance.

## Loads to include in energy model

- Navigation displays, radar, AIS, VHF, autopilot.
- Interior/exterior lighting.
- Refrigeration/freezers.
- Fresh-water pumps and black/grey-water pumps.
- Watermaker.
- HVAC/chiller circulation and fan coils.
- Galley appliances.
- Laundry/dishwasher.
- Windlass/winches/thruster peaks.
- Hydraulic pumps, if used.
- Entertainment/IT/Starlink/networking.
- Bilge/fire/alarm systems.
- Tender/toy charging if planned.

For every load record: voltage, rated W/A, duty cycle, daily Wh, start surge, critical/noncritical status.

## AC architecture

Study at least:

- 230 V 50 Hz European hotel bus.
- Shore input rating(s).
- Isolation transformer(s) or galvanic isolation strategy.
- Generator rating after real hotel-load calculation.
- Inverter-backed essential AC bus.
- Load shedding priorities.
- Separate high-load circuits for induction cooking, boilers, HVAC, laundry and watermaker as applicable.

## Generator sizing

The Stadtship 70’s 7.5 kVA generator is useful historical context but is likely small for a modern 67 ft yacht if electric cooking, meaningful HVAC and modern hotel loads are expected. Final genset size must come from simultaneous-load analysis, not yacht length.

Consider whether one larger genset or two smaller units better suits the operating profile. Two units add redundancy and permit efficient low-load operation but cost space, mass and maintenance.

## Charging sources

Evaluate:

- High-output regulated main-engine alternator(s).
- Genset charger/inverter.
- Shore charging.
- Solar on deckhouse/bimini where visually and structurally acceptable.
- Hydrogenerator for long-distance sailing only if mission justifies drag/complexity.

## Aluminium-yacht electrical requirements

Particular attention is required to:

- DC negative/earthing philosophy.
- Isolation of hull from stray DC currents.
- Shore earth and isolation-transformer arrangement.
- Bonding strategy.
- Galvanic corrosion monitoring.
- Insulated return where appropriate.
- Cable penetrations and chafe isolation through aluminium structure.
- Dissimilar-metal mounting hardware.

The final architecture should be reviewed by a marine electrical engineer familiar with aluminium yachts.

## Instrumentation to reserve

- Tank levels.
- DC battery voltage/current/SOC.
- Generator and shore source status.
- AC load per phase/source.
- Bilge high-water alarms.
- Fire/heat/smoke alarms.
- Engine-room temperature.
- Inverter/charger status.
- Isolation/ground fault monitoring.
- Navigation-light failure monitoring where practicable.
