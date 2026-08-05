# Changelog

Newest first. Dates are fabrication export dates.

## Rev2 (2026-06-04)

Validated build, export set `OpenFC-Lite-Mini-rev2`. Substantial redesign over the Rev 1 prototype; all schematic and board edits made manually in KiCad. Remaining open items: [`hardware/research/open-items.md`](hardware/research/open-items.md).

### MCU
- **RP2354B (QFN-80) to RP2354A (QFN-60).** 48 to 30 GPIO. The peripheral map was re-derived from scratch and now uses every GPIO (see [DESIGN.md](hardware/docs/DESIGN.md)). Reference designators were fully re-annotated. Dropped vs the QFN-80 layout: the second PIO UART, the SBUS hardware inverter, and the separate RSSI / external-ADC analog inputs.
- **Internal core SMPS inductor (L4, 3.3uH)** added on VREG_LX for the RP2354A's integrated 1.1V buck.

### Power
- **U3/U4 bucks**: LMR51420 (2A) to **LMR51430YFDDCR** (3A, C5219261), same SOT-23-6.
- **R30** (10V FB, R29=100k top): 6.8k to **6.49k** (E96). Vout = 0.6 x (1 + 100/6.49) = **9.85V**, about 1.5% low, fine.
- **C28** (10V buck output cap): **22uF 16V X5R 0603**. DC-bias derates effective C to roughly 7-11uF; with the 4.7uH inductor this raises 10V ripple but is acceptable for a digital VTX rail.
- **L2/L3 inductors**: both rails **4.7uH (XRTC303020D4R7MBCA)**. 10V ripple about 1.17A p-p at 6S; peak well under the 3A part.
- **U6 gyro LDO**: **NCV8187AMT180TAG** (1.2 A, high PSRR, 80 dB to 10 kHz). Gyro analog load is single-digit mA, so the rating is far in excess; kept for its PSRR. Low stock, consign if needed.
- **Battery reverse-polarity protection** added (RB161QS-40 Schottky, D3/D10).

### USB
- **R15/R24/R37** (USB series resistors): kept at 30R. USB FS is impedance-tolerant; a single resistor value is better DFM.

### LEDs
- All indicator LEDs **0201 to 0402** (0201 too fragile: broke during nut install).
- **D2** (LED0 status, GPIO26): green to **blue** (XL-1005UBC, C22355736), per BF section 3.1.4.6.
- **LED series resistors recalculated for about 1mA** (greens = XL-1005UGC, C965793):

  | LED | Color | Source | New R (E24) | I |
  |---|---|---|---|---|
  | D2 (LED0) | Blue | GPIO26 (~3.3V) | 510R | ~1.0mA |
  | D7 | Green | +3.3V | 680R | ~1.0mA |
  | D5 | Green | +5V (5V_BUCK) | 2.4k | ~1.0mA |
  | D4 | Green | +10V | 7.5k | ~1.0mA |

### Signals / connectivity
- **IMU and microSD split onto separate SPI buses**: IMU on **SPI1** (SCK/MOSI/MISO = GPIO10/11/12, CS=GPIO13, INT=GPIO9); microSD on **SPI0** (SCK/MOSI/MISO = GPIO18/19/20, CS=GPIO21). CS lines grouped into each bus. IMU CLKIN/SYNC is not routed to the MCU (ST gyro, no spare GPIO).
- **SBUS inverter removed.** BF PICO inverts at the RP2350 pad IO-mux (`gpio_set_inover/outover(GPIO_OVERRIDE_INVERT)`), auto-set for SBUS on native and PIO UARTs. The RX line wires straight to a UART RX GPIO; firmware inverts.
- **ESC connector P1**: now an 8-pin JST SH (SM08B-SRSS-TB) with the corrected, mirrored pinout. Rev 1 used a reversed generic header, a safety-critical defect: the old pinout shorted VBAT to a GPIO on a standard BF harness.
- **Beeper**: N-MOS low-side switch (Q-FET + 1k gate + 100k pulldown, BEEPER = GPIO17). Flyback diode across the buzzer.
- **microSD** wired compatible with both SPI and SDIO; uses **SPI**. Betaflight PICO supports SD blackbox over SPI only (PR #14567); SDIO would give about 10x throughput but needs a 4-bit HW bus and firmware that does not exist.

### Analog OSD (front-end rework)
OSD was non-functional on Rev 1: in pass-through the monitor switched to AV (it saw a feed) but showed snow; sync reached the monitor but was too marginal to lock. Wiring and pinouts were verified correct against datasheets; this was a component-suitability and front-end problem. Root cause: the DC-coupled gain-x2 buffer parked the sync tip on the 0 V rail.

- **Op-amp**: TLV9061IDPWR to **COS8051SOT (C7463385)**, a 175 MHz / 150 V/us RRIO video amp (AD8051-class), SOT-23-5. TLV9061 was under-spec for composite video (about 5 MHz closed-loop at gain 2; chroma needs about 28 V/us vs 6.5). New ref **U1**.
- **OSD output front-end**: added **AC-coupling + DC-restore (sync clamp)** to bias the sync tip 0.3-0.5 V above ground before the gain stage; op-amp powered from +5 V for headroom. New nets `VID_DC` / `VID_FILT` / `OSD_LVL`.
- **Comparator (sync sep)**: TLV3201AIDBVR to **TLV7031DPWR (C2876045)**: push-pull, RRI, X2SON-5 (about 75% smaller), 7 mV hysteresis (vs 1.2 mV). Its 3 us prop delay is symmetric, preserving HSYNC/VSYNC pulse-width discrimination, and adds a constant ~22 px horizontal offset compensated in the PIO `hshiftA/B/C` timing (about 225 clocks). Fallback if the X2SON regresses sync: TLV3201AIDCKR (SC70-5, pin-compatible, 40 ns). New ref **U2**.
- **OSD_EN select pull-down**: weak pull-down on U18 pin 6 (S / OSD_EN) so the select never floats and defaults to pass-through before firmware drives the GPIO.
- **U18 SN74LVC1G3157DTBR** and **D9 SDM02U30LP3-7B**: unchanged, verified correct.

### Decisions
- **U5 power MUX**: **TPS2116DRLR** confirmed (auto-select USB/BATT).
- **Motor order**: silk left reversed (eases routing); resolved in the BF target's DShot resource order so M1-M4 map to the pads.
- **SWD connector**: not added. RP2354A flashes over USB (UF2/BOOTSEL).
- **IMU**: LSM6DSV16XTR populated for development; production part selected after bench and flight testing.

## Rev1 (2026-04-28)

First prototype, export set `OpenFC-Lite-Mini-rev1`. RP2354B (QFN-80). Boards received and bench brought up: the custom Betaflight target built and flashed; USB enumeration, IMU, SD-card blackbox, and the switchable 10V VTX rail confirmed working. The analog OSD chain did not work (snow, sync too marginal to lock); the Rev2 front-end rework addressed this.
