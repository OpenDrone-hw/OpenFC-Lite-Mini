# OpenFC-Lite-Mini — Project Instructions

## About this repo
OpenFC-Lite-Mini is an open-source Betaflight flight controller: **20×20 mm**, 6-layer, 3S–6S, built around the RP2354A (QFN-60). This repository covers the **Mini only**. The larger **30.5×30.5 mm OpenFC-Lite** will be a separate project derived from this one once the Mini is finalized; the two share the same schematic.

Design intent — a compact, low-cost FC:
- No barometer.
- No integrated ELRS receiver (use an external RX over UART).
- No onboard WS2812B LEDs (LED-strip pad only).
- Blackbox logging on a microSD slot (TF-021B-H265), not onboard SPI flash.

## Working agreement
- Stan is a hardware/embedded engineer. Be direct and critical — flag problems, skip praise.
- **Metadata yes, physical connections no.** Claude may edit *metadata* programmatically — KiCad text variables (`.kicad_pro`), symbol BOM/doc fields (MPN, Manufacturer, LCSC, Cost, BOM Comments, Datasheet, notes) — via kicad-skip or the pcbnew API. Claude must **never** change physical connections: nets, wiring, routing, placement, footprint assignments, or component values that alter the circuit. Those stay Stan's, done in KiCad.
- **NEVER raw-edit** `.kicad_sch`, `.kicad_pcb`, or `.kicad_pro` as text — use kicad-skip / the pcbnew API. (`.kicad_pro` is JSON; safe programmatic metadata edits there are fine.)
- Claude may edit documentation (README, this file, other Markdown, JSON config/export files). Keep docs accurate — no aspirational content.
- Git: `main` is protected. Work on feature branches and open PRs via `gh`. Commit/push only when asked.
- Single source of truth is this file + README.md. No separate memory store.

## What Claude can / cannot do here
**Can:** review schematics, PCB, gerbers, netlists, footprints; trace nets; extract and manage the BOM; **write metadata** (text variables, symbol BOM/doc fields) via kicad-skip/pcbnew; run DRC/ERC/DFM/EMC checks; power-budget and regulator analysis; SPICE simulation; component sourcing and pricing; fabrication-prep specs; documentation and diagrams; change lists and design specs.

**Cannot / will not:** change physical connections (nets, wiring, routing, placement, footprint assignments, or circuit-affecting component values); raw-edit S-expression files by hand; place fab orders or take other irreversible external actions without explicit confirmation.

## Tools
- **Skills:** `kicad` (schematic/PCB analysis), `bom` (BOM lifecycle), `lcsc` / `digikey` / `mouser` / `element14` (sourcing + datasheets), `jlcpcb` / `pcbway` (fab prep), `emc` (pre-compliance), `spice` (simulation), `kidoc` (engineering docs).
- **Repo scripts** (`hardware/tools/`, read-only analysis): `audit_design.py`, `openfc_netlist_extract.py`, `openfc_connectivity_report.py`, `openfc_pcb_extract.py`, and helpers.
- **Environment (macOS):** kicad-skip lives in system Python 3.13 (`~/Library/Python/3.13/lib/python/site-packages`). `pcbnew` is only importable under KiCad's bundled Python (`/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`). `kicad-cli` is at `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`.
- **Headless net extraction (no pcbnew):** `kicad-cli sch export netlist --format kicadsexpr -o /tmp/x.net hardware/OpenFC.kicad_sch`, then `python3 hardware/tools/openfc_netlist_extract.py --netlist /tmp/x.net`.

## Revisions
- **Rev 1** — RP2354B (QFN-80) physical prototype; received and bench brought-up. OSD non-functional.
- **Rev 2** — **current** design (RP2354A, QFN-60). Schematic + layout finalized, exported for fabrication. Migrated MCU QFN-80→QFN-60, re-derived the full GPIO map, reworked the OSD front end, split IMU/microSD onto separate SPI buses, added reverse-polarity protection, fully re-annotated refs. Full log in the README.

(No "V0.x" numbering — the earlier V0.1–V0.3 labels were export artifacts and are retired.)

## Key ICs (Rev 2 reference designators)
| Function | Ref | Part | LCSC | Bus / notes |
|---|---|---|---|---|
| MCU | U10 | RP2354A (QFN-60, 2 MB flash, 30 GPIO) | — | 12 MHz xtal X1; core SMPS inductor L4 (3.3µH) on VREG_LX |
| IMU | U9 | LSM6DSV16XTR (dev part) | C5267406 | SPI1; production part undecided — see IMU |
| 10V buck (switchable) | U3 | LMR51430YFDDCR (3A) | C5219261 | EN=GPIO27; 4.7µH / 22µF 16V / FB 100k:6.49k → 9.85V. ⚠️ Value field still `TI …`, MPN field still `LMR51420` — clean for BOM |
| 5V buck (always-on) | U4 | LMR51430YFDDCR (3A) | C5219261 | 4.7µH inductor (same MPN-field issue as U3) |
| 5V power mux | U5 | TPS2116DRLR | C3235557 | USB/BATT auto-select |
| 3.3V LDO | U7 | LP5912-3.3DRVR | C524780 | 500 mA |
| 1.8V gyro LDO | U6 | NCV8187AMT180TAG | C893189 | 300 mA |
| OSD comparator | U2 | TLV7031DPWR | C2876045 | sync separator (was TLV3201/U20) |
| OSD op-amp | U1 | COS8051SOT | C7463385 | video buffer (was TLV9061/U19) |
| OSD SPDT switch | U18 | SN74LVC1G3157DTBR | C2673087 | OSD pixel switch |
| microSD slot | Card1 | TF-021B-H265 | C498185 | SPI0 |
| VTX connector | U8 | SM06B-SRSS-TB (6-pin JST SH) | C160405 | digital VTX |
| ESC connector | P1 | SM08B-SRSS-TB (8-pin JST SH) | — | corrected/mirrored pinout (Rev 1 was reversed generic header) |
| RPP | D3/D10 | RB161QS-40 Schottky | C28646385 | battery reverse-polarity protection |

## IMU
- The footprint is LGA-14 (2.5×3 mm) with pins 2/3 → GND and pins 10/11 → NC, which is electrically safe for **both TDK (ICM-426xx/456xx) and ST (LSM6D*) families**. Selecting/swapping the IMU is a field change once a part is chosen.
- Rev 1 and Rev 2 populate **LSM6DSV16XTR** for development.
- **The production IMU is undecided** — to be chosen after more bench/flight testing.
- Family note: TDK parts use a CLKIN line to remove sample-timing jitter; ST parts have no CLKIN/SYNC. On the QFN-60, IMU CLKIN exists on the sheet but is **not routed to the MCU** (no spare GPIO) — fine for ST; revisit if a TDK IMU is chosen.

## GPIO map (RP2354A QFN-60, 30 GPIO — all used)
- UART0: TX=GPIO0, RX=GPIO1 (digital VTX on U8 JST SH connector)
- PIO UART0: TX=GPIO2, RX=GPIO3 (GPS)
- I2C0: SDA=GPIO4, SCL=GPIO5 (pull-ups to 3.3V; pin pairing SDA%4==0 / SCL%4==1)
- UART1: TX=GPIO6, RX=GPIO7 (external RX; SBUS inverted at the IO-mux in firmware)
- LED strip: GPIO8 (PIO2)
- IMU INT: GPIO9
- SPI1 (IMU): SCK=GPIO10, MOSI=GPIO11, MISO=GPIO12, CS=GPIO13
- OSD (3 consecutive pins): OSD_W=GPIO14, OSD_EN=GPIO15, OSD_SYNC=GPIO16
- Beeper: GPIO17 (N-MOS low-side)
- SPI0 (microSD): SCK=GPIO18, MOSI=GPIO19, MISO=GPIO20, CS=GPIO21
- Motors: M4=GPIO22, M3=GPIO23, M2=GPIO24, M1=GPIO25 (PIO0 DShot). Silk order reversed — resolved in the BF DShot resource order.
- LED0 status (blue): GPIO26
- 10V enable (PINIO1): GPIO27
- ADC (each via 1k+100nF RC): ESC current=GPIO28 (ADC2), VBAT=GPIO29 (ADC3). **Only 4 ADC channels exist; RSSI and external-ADC inputs dropped vs the QFN-80.**

## Power tree
```
+BATT → RPP (D3/D10) → U3 (EN=GPIO27)  → +10V (switchable VTX/cam)   [inductor L2, out cap C28, FB R29 100k / R30]
+BATT → RPP          → U4 (always-on)  → +5V_BUCK                    [inductor L3]
+5V_BUCK + +5V_USB → U5 (TPS2116 mux)  → +5V → U7 (LP5912) → +3.3V → RP2354A VREG (L4 on VREG_LX) → +1.1V core
+5V → U6 (NCV8187)                     → +1.8V_GYRO (IMU analog)
```

## PIO allocation
PIO0: DShot (motors). PIO1: PIO UART0. PIO2: LED strip + OSD.

## Schematic structure
Hierarchical KiCad 9: root `OpenFC.kicad_sch` + 6 sub-sheets — `rp2350a`, `power`, `imu`, `osd`, `blackbox`, `pads`.

## Connectors (JST SH, yellow preferred)
- **U8** — 6-pin SMD VTX: +10V / GND / TX / RX / GND / SBUS — matches the BF digital VTX standard ✓
- **P1** — 8-pin JST SH ESC (SM08B-SRSS-TB): corrected/mirrored pinout vs Rev 1's reversed generic header (was safety-critical — old pinout shorted VBAT to a GPIO).

## Layout rules
RP2350 buck and decoupling placement: see `hardware/tools/rp2350_layout_notes.md` (Raspberry Pi RP2350 datasheet §6.3.8.1 — buck C_IN/L/C_OUT must stay on the MCU side, copper cutaway under the switch node, etc.).

## Betaflight
- Target: Betaflight RP2350A (PICO platform); `BOARD_NAME = OPENFC_LITE_MINI_RP2350A`, `MANUFACTURER_ID = OPFC`. RP2354A uses the Pico SDK (C/C++) with PlatformIO.
- External RX over UART (no onboard/SPI RX).
- Analog OSD (FB_OSD) for RP2350 is still an open upstream PR stack (#14882 chain) — no flyable upstream binary yet; track before tape-out.
- Submission: schematic + config in `betaflight/config`; ~$500 T2 cloud-target fee. BF contacts: sugar K (project lead), vitroid (schematic-review channel).

## Repo conventions
- KiCad 9. Libraries are **project-local only**: `hardware/lib.kicad_sym`, `hardware/lib.pretty/`, `hardware/lib.3dshapes/`. Never global libraries.
- Python tools live in `hardware/tools/`.
- Production exports in `hardware/production/`, generated with the KiCad Fabrication Toolkit and named by revision (`rev1`, `rev2`, …). JLCPCB assembly; prefer LCSC basic parts.
- License: hardware under CERN-OHL-S.
