# OpenFC-Lite-Mini

Open-source Betaflight flight controller — **20×20 mm**, 6-layer, 3S–6S, built around the RP2354A microcontroller. Compact and low-cost: external RX over UART, microSD blackbox, analog OSD.

<p>
<img src="images/openfc-lite-mini-rev1-top.png" width="400" alt="OpenFC-Lite-Mini Rev 1 Top" />
<img src="images/openfc-lite-mini-rev1-bottom.png" width="400" alt="OpenFC-Lite-Mini Rev 1 Bottom" />
</p>

> This repository is the **Mini** (20×20). A larger **OpenFC-Lite** (30.5×30.5 mm, bigger pads, more I/O, full-size SD) will be derived from this design once the Mini is finalized.

## At a glance

| | |
|---|---|
| MCU | RP2354A — dual Cortex-M33 @ 150 MHz, 2 MB stacked flash, QFN-60 (30 GPIO) |
| IMU | LSM6DSV16XTR 6-axis, SPI1 (LGA-14 footprint; production part not yet locked, see [IMU](#imu)) |
| Blackbox | microSD card slot (TF-021B-H265) on SPI0 |
| OSD | analog, PIO-driven (sync separator + video op-amp + SPDT switch) |
| Power | 3S–6S; switchable 10V (VTX/cam) + always-on 5V, reverse-polarity protected |
| Size | 20×20 mm, 6-layer |
| RX | external, over UART |
| USB | USB-C, USB-CDC for configuration |

Intentionally omitted to keep it small and cheap: barometer, integrated ELRS receiver, onboard WS2812B LEDs (LED-strip pad only), onboard SPI blackbox flash (microSD instead).

## Status

**Rev 2** is the current design: schematic and layout finalized and exported for fabrication. Rev 2 migrates the MCU from the QFN-80 RP2354B to the **QFN-60 RP2354A** (30 GPIO, fully allocated), reworks the analog-OSD front end, swaps the IMU and microSD onto separate SPI buses, and adds battery reverse-polarity protection. See the [Rev 2 Change Log](#rev-2-change-log) for the full list.

**Rev 1** boards were received and brought up. The custom Betaflight target builds and flashes; USB enumeration, IMU, SD-card blackbox, and the switchable 10V VTX rail were confirmed working on bench. The analog OSD chain did not work on Rev 1 (snow, sync too marginal to lock) — the Rev 2 front-end rework addresses this and must be re-verified on the next boards.

## Specifications

### Core
- **MCU:** RP2354A — dual-core ARM Cortex-M33 @ 150 MHz, 2 MB integrated stacked flash, QFN-60, 30 GPIO
- **Clock:** 12 MHz crystal (X1) on XIN/XOUT
- **IMU:** 6-axis MEMS on SPI1, dedicated 1.8V analog LDO (see [IMU](#imu))
- **Blackbox:** TF-021B-H265 microSD card slot on SPI0
- **USB:** USB-C, USB-CDC for configuration

### Power tree
| Rail | Source | Regulator | Notes |
|---|---|---|---|
| +10V (switchable) | +BATT | LMR51430YFDDCR (U3, 3A) | EN gated by GPIO27 (PINIO1). VTX/cam rail. 4.7µH / 22µF 16V / FB 100k:6.49k → 9.85V. |
| +5V (always-on) | +BATT | LMR51430YFDDCR (U4, 3A) | 4.7µH inductor. |
| +5V (USB/BATT mux) | +5V_BUCK + +5V_USB | TPS2116DRLR (U5) | Auto-selects active source. |
| +3.3V | +5V | LP5912-3.3DRVR (U7) | 500 mA LDO. |
| +1.8V (gyro analog) | +5V | NCV8187AMT180TAG (U6) | 1.2 A LDO, high PSRR (80 dB to 10 kHz). Isolated IMU analog supply; gyro draws only mA so the rating is far in excess. |
| +1.1V (MCU core) | +3.3V | RP2354A internal VREG | External SMPS inductor (L4, 3.3µH) on VREG_LX. |

Battery input has reverse-polarity protection (RB161QS-40 Schottky, D3/D10).

### Motor outputs
- 4× PIO-driven DShot outputs (DShot600, bidirectional telemetry supported)
- M1=GPIO25, M2=GPIO24, M3=GPIO23, M4=GPIO22 *(descending GPIO — silk order is mapped back to M1–M4 in the Betaflight DShot resource order)*

### Connectors
- **USB-C** — configuration and firmware flashing
- **U8** — 6-pin SMD JST SH digital VTX connector (matches Betaflight standard: +10V/GND/TX/RX/GND/SBUS)
- **P1** — 8-pin JST SH (SM08B-SRSS-TB) ESC harness
- I2C0 expansion pads (SDA/SCL, with pull-ups to 3.3V)

### Serial / I/O
- **UART0** (GPIO0/1) — digital VTX / MSP DisplayPort
- **UART1** (GPIO6/7) — external serial RX (CRSF/SBUS/etc.)
- **PIO UART0** (GPIO2/3) — software UART, default GPS
- **I2C0** (GPIO4/5) — external expansion
- **SPI1** (GPIO10/11/12, CS=GPIO13, INT=GPIO9) — IMU
- **SPI0** (GPIO18/19/20, CS=GPIO21) — microSD blackbox

### Analog inputs
- VBAT sense (GPIO29 / ADC3) — divider + 1k+100nF RC filter
- ESC current sense (GPIO28 / ADC2) — onboard sense circuit, 1k+100nF RC filter

*(The QFN-60 has only 4 ADC channels — GPIO26/27 are used as digital LED0 / 10V-enable, leaving GPIO28/29 for VBAT and current. The separate RSSI and external-ADC inputs from the QFN-80 layout are not available on this part.)*

### Additional
- Addressable LED strip output (GPIO8, PIO2)
- Status LED — LED0, blue (GPIO26)
- Beeper output, N-MOS low-side switch (GPIO17)
- 10V rail enable (GPIO27) — exposed as PINIO1/USER1 in firmware

### Analog OSD
- TLV7031DPWR (U2) — fast comparator, sync separator on the incoming composite video
- COS8051SOT (U1) — wide-band video op-amp output buffer (175 MHz / 150 V/µs RRIO)
- SN74LVC1G3157DTBR (U18) — SPDT analog switch: camera passthrough, black-pixel inject, white-pixel inject
- AC-coupled input with DC-restore (sync clamp) front end, biasing the sync tip off the 0 V rail before the gain stage
- Driven by RP2354A PIO2 — pixel-level timing for character overlay on PAL/NTSC composite

## GPIO map

All 30 GPIO of the QFN-60 are allocated:

| GPIO | Function | | GPIO | Function |
|---|---|---|---|---|
| 0 | UART0 TX (VTX) | | 15 | OSD enable |
| 1 | UART0 RX (VTX) | | 16 | OSD sync |
| 2 | PIO UART0 TX (GPS) | | 17 | Beeper |
| 3 | PIO UART0 RX (GPS) | | 18 | SPI0 SCK (microSD) |
| 4 | I2C0 SDA | | 19 | SPI0 MOSI (microSD) |
| 5 | I2C0 SCL | | 20 | SPI0 MISO (microSD) |
| 6 | UART1 TX (RX) | | 21 | microSD CS |
| 7 | UART1 RX (RX) | | 22 | Motor M4 |
| 8 | LED strip | | 23 | Motor M3 |
| 9 | IMU INT | | 24 | Motor M2 |
| 10 | SPI1 SCK (IMU) | | 25 | Motor M1 |
| 11 | SPI1 MOSI (IMU) | | 26 | LED0 status (blue) |
| 12 | SPI1 MISO (IMU) | | 27 | 10V enable (PINIO1) |
| 13 | IMU CS | | 28 | ESC current (ADC2) |
| 14 | OSD write | | 29 | VBAT sense (ADC3) |

## IMU

The IMU footprint is LGA-14 (2.5×3 mm), routed with pins 2/3 → GND and pins 10/11 → NC, so it accepts **both TDK (ICM-426xx/456xx) and ST (LSM6D*) families**. Choosing the IMU is a part-population decision, not a layout change.

- **Rev 1 and Rev 2** populate **LSM6DSV16XTR** for development.
- **The production IMU is not yet decided** — to be selected after more bench and flight testing.
- Note: TDK parts use a CLKIN line to eliminate sample-timing jitter; ST parts have no CLKIN/SYNC. The IMU CLKIN net exists on the sheet but is **not routed to the MCU** on the QFN-60 (no spare GPIO) — fine for an ST gyro; revisit if a TDK IMU is chosen.

## Firmware

A custom Betaflight target (`OPENFC_LITE_MINI_RP2350A`, `MANUFACTURER_ID = OPFC`) defines:

- Motor map matching the silkscreen (M1..M4 = GPIO25..GPIO22) via the DShot resource order
- `USE_SDCARD_SPI` on SPI0 for blackbox
- `USE_PINIO` on GPIO27 for the switchable 10V VTX rail
- FB_OSD framework wired but disabled by default (enable once the analog OSD chain is verified on hardware — note the RP2350 FB_OSD driver is still an open upstream PR stack)

Build (requires a Betaflight checkout with `pico-sdk` and the BF-pinned ARM toolchain):

```sh
make picotool_install
make arm_sdk_install
make CONFIG=OPENFC_LITE_MINI_RP2350A
```

Output is a `.uf2` in `obj/`. Hold BOOTSEL, plug in USB, and drag the UF2 onto the `RP2350` mass-storage drive that mounts.

## PIO Allocation

The RP2350 has 3 PIO blocks × 4 state machines (12 total):

| Block | Function |
|---|---|
| PIO0 | DShot motor output (4 SMs, one per motor) |
| PIO1 | Software UART (PIO UART0 — TX and RX programs) |
| PIO2 | LED strip + analog OSD pixel timing |

## Revision History

| Rev | Status | Notes |
|---|---|---|
| **Rev 1** | prototype | RP2354B (QFN-80). Received and bench brought-up; OSD non-functional. |
| **Rev 2** | current | RP2354A (QFN-60). Design finalized and exported for fabrication. See [Rev 2 Change Log](#rev-2-change-log). |

## Rev 2 Change Log

Rev 2 was a substantial redesign over the Rev 1 prototype. **All schematic and board edits are made manually in KiCad.** Items below are reflected in the current schematic unless flagged **OPEN**.

### MCU
- **RP2354B (QFN-80) → RP2354A (QFN-60).** 48 → 30 GPIO. The peripheral map was re-derived from scratch and now uses every GPIO (see [GPIO map](#gpio-map)). Reference designators were fully re-annotated. Dropped vs the QFN-80 layout: the second PIO UART, the SBUS hardware inverter, and the separate RSSI / external-ADC analog inputs.
- **Internal core SMPS inductor (L4, 3.3µH)** added on VREG_LX for the RP2354A's integrated 1.1V buck.

### Power
- **U3/U4 bucks**: LMR51420 (2A) → **LMR51430YFDDCR** (3A, C5219261), same SOT-23-6.
- **R30** (10V FB, R29=100k top): 6.8k → **6.49k** (E96). Vout = 0.6·(1 + 100/6.49) = **9.85V** (~1.5% low — fine).
- **C28** (10V buck output cap): **22µF 16V X5R 0603**. DC-bias derates effective C to ~7–11µF; with the 4.7µH inductor this raises 10V ripple but is acceptable for a digital VTX rail.
- **L2/L3 inductors**: both rails **4.7µH (XRTC303020D4R7MBCA)**. 10V ripple ≈1.17A p-p at 6S; peak well under the 3A part.
- **U6 gyro LDO**: **NCV8187AMT180TAG** (1.2 A, high PSRR 80 dB to 10 kHz) — gyro analog is single-digit mA, so hugely overspec'd; the 1.2 A rating comfortably clears BF §3.1.2's ≥500 mA. Kept for its PSRR. Low stock → consign if needed.
- **Battery reverse-polarity protection** added (RB161QS-40 Schottky, D3/D10).
- **OPEN — U3/U4 BOM fields**: the symbol Value still carries a `TI ` prefix and the MPN/LCSC field still reads `LMR51420YDDCR`. Clean both so LCSC/MPN exact-match resolves to the LMR51430 (C5219261) for assembly.

### MCU / USB
- **R12/R13/R14**: kept at 30Ω. USB FS is impedance-tolerant; single resistor value = better DFM.
- **OPEN — D1 USB ESD (USBLC6-2P6)**: not currently placed. **Recommend restoring.** USB is the most-handled / most-exposed interface; the RP2354A PHY isn't rated for system-level (IEC 61000-4-2 8kV) ESD, and the part is tiny/cheap/low-C. Pending final call.

### LEDs
- All indicator LEDs **0201 → 0402** (0201 too fragile — broke during nut install).
- **D2** (LED0 status, GPIO26): green → **blue** (XL-1005UBC, C22355736). BF §3.1.4.6.
- **LED series resistors recalculated for ~1mA** (greens = XL-1005UGC, C965793).

  | LED | Color | Source | New R (E24) | I |
  |---|---|---|---|---|
  | D2 (LED0) | Blue | GPIO26 (~3.3V) | 510Ω | ~1.0mA |
  | D7 | Green | +3.3V | 680Ω | ~1.0mA |
  | D5 | Green | +5V (5V_BUCK) | 2.4kΩ | ~1.0mA |
  | D4 | Green | +10V | 7.5kΩ | ~1.0mA |

### Signals / connectivity
- **IMU and microSD split onto separate SPI buses**: IMU on **SPI1** (SCK/MOSI/MISO = GPIO10/11/12, CS=GPIO13, INT=GPIO9); microSD on **SPI0** (SCK/MOSI/MISO = GPIO18/19/20, CS=GPIO21). CS lines grouped into each bus. IMU CLKIN/SYNC is **not routed to the MCU** (ST gyro; no spare GPIO).
- **SBUS inverter removed.** BF PICO inverts at the RP2350 pad IO-mux (`gpio_set_inover/outover(GPIO_OVERRIDE_INVERT)`), auto-set for SBUS on native + PIO UARTs. The RX line wires straight to a UART RX GPIO; firmware inverts.
- **ESC connector P1**: now an 8-pin JST SH (SM08B-SRSS-TB) with the corrected, mirrored pinout (was a reversed generic header on Rev 1 — a safety-critical fix; the old pinout shorted VBAT to a GPIO on a standard BF harness).
- **Beeper**: N-MOS low-side switch (Q-FET + 1k gate + 100k pulldown, BEEPER = GPIO17). Flyback diode across the buzzer.
- **microSD** wired compatible with both SPI and SDIO; uses **SPI** (see SDIO decision below).

### Analog OSD (front-end rework)

OSD was non-functional on Rev 1: in pass-through the monitor switched to AV (it saw a feed) but showed snow — sync reached the monitor but was too marginal to lock. Wiring/pinouts were verified correct against datasheets; this was a component-suitability + front-end problem. Root cause: the DC-coupled gain-×2 buffer parked the sync tip on the 0 V rail. **Bench-confirm the fix on the next boards.**

- **U19 op-amp**: TLV9061IDPWR → **COS8051SOT (C7463385)** — 175 MHz / 150 V/µs RRIO video amp (AD8051-class), SOT-23-5. TLV9061 was under-spec for composite video (≈5 MHz closed-loop at gain 2; chroma needs ≈28 V/µs vs 6.5). New ref **U1**.
- **OSD output front-end**: added **AC-coupling + DC-restore (sync clamp)** to bias the sync tip ~0.3–0.5 V above ground before the gain stage; op-amp powered from +5 V for headroom. New nets `VID_DC` / `VID_FILT` / `OSD_LVL`.
- **U20 comparator (sync sep)**: TLV3201AIDBVR → **TLV7031DPWR (C2876045)** — push-pull, RRI, X2SON-5 (~75% smaller), 7 mV hysteresis (vs 1.2 mV). 3 µs prop delay is symmetric → preserves HSYNC/VSYNC pulse-width discrimination, adds a constant ~22 px horizontal offset → **retune PIO `hshiftA/B/C`** (drop ~225 clocks). Bench-verify field lock; conservative fallback is TLV3201AIDCKR (SC70-5, pin-compatible, 40 ns) if the X2SON regresses sync. New ref **U2**.
- **OSD_EN select pull-down**: weak pull-down on U18 pin 6 (S / OSD_EN) so the select never floats and defaults to pass-through before firmware drives the GPIO.
- **U18 SN74LVC1G3157DTBR** and **D9 SDM02U30LP3-7B** — unchanged, verified correct.

### Decisions / investigations
- **IMU** — production part undecided; see [IMU](#imu).
- **U5 power MUX** — **TPS2116DRLR** confirmed (auto-select USB/BATT).
- **SDIO on Pico** — **stay on SPI.** Betaflight PICO supports SD blackbox over **SPI only** (PR #14567); no SDIO under `src/platform/PICO/`. SDIO would give ~10× throughput but needs a 4-bit HW bus *and* firmware that doesn't exist.
- **Motor order** — silk left reversed (eases routing); resolved in the BF target's DShot resource order so M1–M4 map to the pads.
- **OPEN — FB_OSD upstream**: the RP2350 analog-OSD driver PR stack (#14882) is still open; no flyable upstream binary yet. Track before tape-out.
- **SWD connector** — **not adding.** RP2354A flashes over USB (UF2/BOOTSEL); SWD pads optional.

## Repository Structure

```
OpenFC-Lite-Mini/
├── README.md
├── LICENSE
├── hardware/                ← KiCad 9 project, libraries, and production files
│   ├── OpenFC.kicad_pro     ← Project file
│   ├── OpenFC.kicad_pcb     ← PCB layout
│   ├── OpenFC.kicad_sch     ← Top-level schematic (hierarchical)
│   ├── *.kicad_sch          ← Sub-sheets
│   ├── lib.kicad_sym        ← Project-local symbol library
│   ├── lib.pretty/          ← Project-local footprint library
│   ├── lib.3dshapes/        ← Project-local 3D models
│   ├── production/          ← JLCPCB production exports, per revision (gitignored — re-exportable)
│   ├── research/            ← IMU selection + routing-validation notes
│   └── tools/               ← Analysis scripts (Python, kicad-skip / pcbnew API)
└── images/                  ← Board renders
```

All symbol, footprint, and 3D model libraries are project-local — no external library setup required.

## Schematic Hierarchy

- `OpenFC.kicad_sch` — top-level
- `rp2350a.kicad_sch` — RP2354A microcontroller, crystal, USB-C, status LED, supporting circuitry
- `power.kicad_sch` — power supply and regulation (10V buck, 5V buck, 3.3V/1.8V LDOs, 5V mux, reverse-polarity protection)
- `imu.kicad_sch` — 6-axis IMU on SPI1 (LGA-14 2.5×3 footprint; populates LSM6DSV16XTR for dev — see [IMU](#imu))
- `osd.kicad_sch` — analog OSD chain (TLV7031 sync sep + COS8051 video buffer + SN74LVC1G3157 switch)
- `blackbox.kicad_sch` — TF-021B-H265 microSD card slot on SPI0
- `pads.kicad_sch` — solder pads and connectors

## License

Hardware licensed under [CERN-OHL-S-2.0](https://ohwr.org/cern_ohl_s_v2.txt). See [LICENSE](LICENSE) for details.
</content>
</invoke>
