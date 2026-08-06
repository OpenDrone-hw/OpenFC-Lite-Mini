# OpenFC-Lite-Mini Design Notes

Detailed design description of the OpenFC-Lite-Mini. Values are extracted from the KiCad design files: `hardware/OpenFC.kicad_sch` and its sub-sheets, `hardware/OpenFC.kicad_pcb`.

## Architecture

Betaflight flight controller on the RP2354A: dual-core ARM Cortex-M33 @ 150 MHz, 2 MB integrated stacked flash, QFN-60, 30 GPIO, all allocated. 12 MHz crystal (X1) on XIN/XOUT. USB-C with USB-CDC for configuration and UF2 flashing.

Intentionally omitted to keep the board small and cheap: barometer, integrated ELRS receiver, onboard WS2812B LEDs (LED-strip pad only), onboard SPI blackbox flash (microSD instead).

## Power tree

| Rail | Source | Regulator | Notes |
|---|---|---|---|
| +10V (switchable) | +BATT | LMR51430YFDDCR (U3, 3A) | EN gated by GPIO27 (PINIO1). VTX/cam rail. 4.7uH / 22uF 16V / FB 100k:6.49k, Vout 9.85V |
| +5V (always-on) | +BATT | LMR51430YFDDCR (U4, 3A) | 4.7uH inductor |
| +5V (USB/BATT mux) | +5V_BUCK + +5V_USB | TPS2116DRLR (U5) | Auto-selects active source |
| +3.3V | +5V | LP5912-3.3DRVR (U7) | 500 mA LDO |
| +1.8V (gyro analog) | +5V | NCV8187AMT180TAG (U6) | 1.2 A LDO, high PSRR (80 dB to 10 kHz), isolated IMU analog supply; gyro load is single-digit mA |
| +1.1V (MCU core) | +3.3V | RP2354A internal VREG | External SMPS inductor (L4, 3.3uH) on VREG_LX |

Both buck inductors are 4.7uH (XRTC303020D4R7MBCA). Battery input has reverse-polarity protection (RB161QS-40 Schottky, D3/D10).

Layout constraint on the core buck: RP2350 datasheet section 6.3.8.1 forbids putting the VREG input cap, L4, or the VREG output cap on the opposite side of the board from the MCU, so that cluster stays on the MCU side. Copper is cut away under the VREG_LX node on the top layer and on layer 2, and the GND return to the QFN centre pad uses two adjacent vias. Sources: [RP2350 datasheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf), [Hardware design with RP2350](https://datasheets.raspberrypi.com/rp2350/hardware-design-with-rp2350.pdf).

## Motor outputs

4x PIO-driven DShot outputs (DShot600, bidirectional telemetry supported). M1=GPIO25, M2=GPIO24, M3=GPIO23, M4=GPIO22: descending GPIO order, mapped back to M1-M4 in the Betaflight DShot resource order (silk order left reversed to ease routing).

## Connectors

- **USB-C**: configuration and firmware flashing
- **U8**: 6-pin SMD JST SH digital VTX connector, Betaflight standard pinout (+10V/GND/TX/RX/GND/SBUS)
- **P1**: 8-pin JST SH (SM08B-SRSS-TB) ESC harness
- I2C0 expansion pads (SDA/SCL, pull-ups to 3.3V)

## Serial and I/O

Pin assignments are in the GPIO map below.

- **UART0**: digital VTX / MSP DisplayPort
- **UART1**: external serial RX (CRSF/SBUS/etc.)
- **PIO UART0**: software UART, default GPS
- **I2C0**: external expansion
- **SPI1**: IMU, plus a dedicated interrupt line
- **SPI0**: microSD blackbox

## Analog inputs

- VBAT sense (GPIO29 / ADC3): divider + 1k+100nF RC filter
- ESC current sense (GPIO28 / ADC2): onboard sense circuit, 1k+100nF RC filter

The QFN-60 has only 4 ADC channels; GPIO26/27 are used as digital LED0 and 10V-enable, leaving GPIO28/29 for VBAT and current. The separate RSSI and external-ADC inputs from the QFN-80 layout are not available on this part.

## Additional I/O

- Addressable LED strip output (GPIO8)
- Status LED: LED0, blue (GPIO26)
- Beeper output, N-MOS low-side switch (GPIO17), flyback diode across the buzzer
- 10V rail enable (GPIO27), exposed as PINIO1/USER1 in firmware

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

The IMU footprint is LGA-14 (2.5 x 3 mm), routed with pins 2/3 to GND and pins 10/11 NC, so it accepts both TDK (ICM-426xx/456xx) and ST (LSM6D*) families. Choosing the IMU is a part-population decision, not a layout change. Rev 1 and Rev 2 populate the **LSM6DSV16XTR** for development; the production IMU is selected after bench and flight testing (comparison data: `hardware/research/imu-selection/`). The IMU runs from a dedicated 1.8V analog LDO (U6).

TDK parts use a CLKIN line to eliminate sample-timing jitter; ST parts have no CLKIN/SYNC. The IMU CLKIN net exists on the sheet but is not routed to the MCU on the QFN-60 (no spare GPIO): fine for an ST gyro, revisit if a TDK IMU is chosen.

## Analog OSD

- TLV7031DPWR (U2): fast comparator, sync separator on the incoming composite video
- COS8051SOT (U1): wide-band video op-amp output buffer (175 MHz / 150 V/us RRIO)
- SN74LVC1G3157DTBR (U18): SPDT analog switch: camera passthrough, black-pixel inject, white-pixel inject
- AC-coupled input with DC-restore (sync clamp) front end, biasing the sync tip off the 0 V rail before the gain stage
- U1 and U2 both run from +3.3V
- OSD write / enable / sync are GPIO14/15/16: three consecutive GPIO with the write line lowest, as the Betaflight FB_OSD driver requires
- PIO-driven: pixel-level timing for character overlay on PAL/NTSC composite

## PIO allocation

The RP2350 has 3 PIO blocks x 4 state machines (12 total):

| Block | Function |
|---|---|
| PIO0 | DShot motor output (4 SMs, one per motor) |
| PIO1 | Software UART (PIO UART0, TX and RX programs) |
| PIO2 | LED strip + analog OSD pixel timing |

The block the LED strip runs on is unresolved: an instruction-memory budget check puts the
OSD and WS2812 programs over the 32-slot limit of a single PIO block, which would move the
LED strip to PIO1. Firmware configuration only, no board impact. See
[`hardware/research/open-items.md`](../research/open-items.md).

## Firmware

A custom Betaflight target (`OPENFC_LITE_MINI_RP2350A`, `MANUFACTURER_ID = OPFC`) defines:

- Motor map matching the silkscreen (M1..M4 = GPIO25..GPIO22) via the DShot resource order
- `USE_SDCARD_SPI` on SPI0 for blackbox
- `USE_PINIO` on GPIO27 for the switchable 10V VTX rail
- FB_OSD wired but disabled by default. Upstream driver status and the pending bench verification: [`hardware/research/open-items.md`](../research/open-items.md).

The target config is not yet published in [betaflight/config](https://github.com/betaflight/config); building requires adding the target files to a Betaflight checkout (with `pico-sdk` and the BF-pinned ARM toolchain):

```sh
make picotool_install
make arm_sdk_install
make CONFIG=OPENFC_LITE_MINI_RP2350A
```

Output is a `.uf2` in `obj/`. Hold BOOTSEL, plug in USB, and drag the UF2 onto the `RP2350` mass-storage drive that mounts.

Betaflight PICO supports SD blackbox over SPI only (PR #14567, no SDIO under `src/platform/PICO/`), so the microSD is wired for SPI even though the slot routing is SDIO-compatible. SBUS inversion is handled at the RP2350 pad IO-mux (`gpio_set_inover/outover(GPIO_OVERRIDE_INVERT)`), auto-set for SBUS on native and PIO UARTs, so there is no hardware inverter: the RX line wires straight to a UART RX GPIO. That RX line stays on hardware UART1 rather than the PIO UART, because the PIO UART path re-runs `gpio_set_function` and clears the pad inversion.

## Variants and revisions

This repo is the 20x20 member of the OpenFC-Lite family; the 30.5 x 30.5 mm sibling is [OpenFC-Lite](https://github.com/incutec-hw/OpenFC-Lite), described in the repository README. Open engineering items are tracked in [`hardware/research/open-items.md`](../research/open-items.md).

## Revisions

## Rev2 (2026-06-04)

Validated build, export set `OpenFC-Lite-Mini-rev2`. Substantial redesign over the Rev 1 prototype; all schematic and board edits made manually in KiCad. Remaining open items: [`hardware/research/open-items.md`](../research/open-items.md).

### MCU
- **RP2354B (QFN-80) to RP2354A (QFN-60).** 48 to 30 GPIO. The peripheral map was re-derived from scratch and now uses every GPIO (see the GPIO map above). Reference designators were fully re-annotated. Dropped vs the QFN-80 layout: the second PIO UART, the SBUS hardware inverter, and the separate RSSI / external-ADC analog inputs.
- **Internal core SMPS inductor (L4, 3.3uH)** added on VREG_LX for the RP2354A's integrated 1.1V buck.

### Power
- **U3/U4 bucks**: LMR51420 (2A) to **LMR51430YFDDCR** (3A, C5219261), same SOT-23-6.
- **R30** (10V FB, R29=100k top): 6.8k to **6.49k** (E96). Vout = 0.6 x (1 + 100/6.49) = **9.85V**, about 1.5% low, fine.
- **C28** (10V buck output cap): **22uF 16V X5R 0603**. DC-bias derates effective C to roughly 7-11uF; with the 4.7uH inductor this raises 10V ripple but is acceptable for a digital VTX rail.
- **L2/L3 inductors**: both rails **4.7uH (XRTC303020D4R7MBCA)**. 10V ripple about 1.17A p-p at 6S; peak well under the 3A part.
- **U6 gyro LDO**: **NCV8187AMT180TAG** (1.2 A, high PSRR, 80 dB to 10 kHz). Gyro analog load is single-digit mA, so the 1.2 A rating is far in excess of BF section 3.1.2's 500 mA minimum; kept for its PSRR. Low stock, consign if needed.
- **Battery reverse-polarity protection** added (RB161QS-40 Schottky, D3/D10).

### USB
- **R15/R24/R37** (USB series resistors): kept at 30R. USB FS is impedance-tolerant; a single resistor value is better DFM.

### LEDs
- All indicator LEDs **0201 to 0402** (0201 too fragile: broke during nut install).
- **D2** (LED0 status, GPIO26): green to **blue** (XL-1005UBC, C22355736), per BF section 3.1.4.6.
- **LED series resistors resized down to the low-mA range** (greens = XL-1005UGC, C965793). As built on Rev 2, currents computed at Vf about 2.6 V (green) and 2.8 V (blue):

  | LED | Color | Source | Series R | I |
  |---|---|---|---|---|
  | D2 (LED0) | Blue | GPIO26 (~3.3V) | R52 + R53 = 150R | ~3.3mA |
  | D7 | Green | +3.3V | R36 = 510R | ~1.4mA |
  | D5 | Green | +5V_BUCK | R50 = 2.4k | ~1.0mA |
  | D4 | Green | +10V | R33 = 7.5k | ~1.0mA |
  | D8 | Green | +5V, cathode via R40 to the U6 PG pin | R40 = 2.4k | ~1.0mA |

  D4, D5 and D8 hit the 1 mA target. D2 and D7 sit above it. D8 lights when 1.8V_PG pulls low.

### Signals / connectivity
- **IMU and microSD split onto separate SPI buses**: IMU on **SPI1**, microSD on **SPI0**, CS lines grouped into each bus. Pin assignments are in the GPIO map above. IMU CLKIN/SYNC is not routed to the MCU (ST gyro, no spare GPIO).
- **SBUS inverter removed**, firmware inverts at the pad IO-mux instead. See Firmware above.
- **ESC connector P1**: now an 8-pin JST SH (SM08B-SRSS-TB) with the corrected, mirrored pinout. Rev 1 used a reversed generic header, a safety-critical defect: the old pinout shorted VBAT to a GPIO on a standard BF harness.
- **Beeper**: N-MOS low-side switch (Q-FET + 1k gate + 100k pulldown, BEEPER = GPIO17). Flyback diode across the buzzer.
- **microSD** wired compatible with both SPI and SDIO; uses **SPI** (rationale under Firmware above). SDIO would give about 10x throughput but needs a 4-bit HW bus and firmware that does not exist.

### Analog OSD (front-end rework)
OSD was non-functional on Rev 1: in pass-through the monitor switched to AV (it saw a feed) but showed snow; sync reached the monitor but was too marginal to lock. Wiring and pinouts were verified correct against datasheets; this was a component-suitability and front-end problem. Root cause: the DC-coupled gain-x2 buffer parked the sync tip on the 0 V rail.

- **Op-amp**: TLV9061IDPWR to **COS8051SOT (C7463385)**, a 175 MHz / 150 V/us RRIO video amp (AD8051-class), SOT-23-5. TLV9061 was under-spec for composite video (about 5 MHz closed-loop at gain 2; chroma needs about 28 V/us vs 6.5). Ref changed U19 to **U1**.
- **OSD output front-end**: added **AC-coupling + DC-restore (sync clamp)** to bias the sync tip 0.3-0.5 V above ground before the gain stage. New nets `VID_DC` / `VID_FILT` / `OSD_LVL`. The op-amp runs from **+3.3 V** (U1 pin 5); output headroom at gain 2 is an open item, see [`hardware/research/open-items.md`](../research/open-items.md).
- **Comparator (sync sep)**: TLV3201AIDBVR to **TLV7031DPWR (C2876045)**: push-pull, RRI, X2SON-5 (about 75% smaller), 7 mV hysteresis (vs 1.2 mV). Its 3 us prop delay is symmetric, preserving HSYNC/VSYNC pulse-width discrimination, and adds a constant ~22 px horizontal offset that the PIO `hshiftA/B/C` timing must absorb (about 225 clocks). Fallback if the X2SON regresses sync: TLV3201AIDCKR (SC70-5, pin-compatible, 40 ns). Ref changed U20 to **U2**.
- **OSD_EN select pull-down**: weak pull-down on U18 pin 6 (S / OSD_EN) so the select never floats and defaults to pass-through before firmware drives the GPIO.
- **U18 SN74LVC1G3157DTBR** and **D9 SDM02U30LP3-7B**: unchanged, verified correct.

### Decisions
- **U5 power MUX**: **TPS2116DRLR** confirmed (auto-select USB/BATT).
- **Motor order**: silk left reversed (eases routing); resolved in the BF target's DShot resource order so M1-M4 map to the pads.
- **SWD connector**: not added. RP2354A flashes over USB (UF2/BOOTSEL).
- **IMU**: LSM6DSV16XTR populated for development; production part selected after bench and flight testing.

## Rev1 (2026-04-28)

First prototype, export set `OpenFC-Lite-Mini-rev1`. RP2354B (QFN-80). Boards received and bench brought up: the custom Betaflight target built and flashed; USB enumeration, IMU, SD-card blackbox, and the switchable 10V VTX rail confirmed working. The analog OSD chain did not work (snow, sync too marginal to lock); the Rev2 front-end rework addressed this.
