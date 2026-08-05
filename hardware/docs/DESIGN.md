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

## Motor outputs

4x PIO-driven DShot outputs (DShot600, bidirectional telemetry supported). M1=GPIO25, M2=GPIO24, M3=GPIO23, M4=GPIO22: descending GPIO order, mapped back to M1-M4 in the Betaflight DShot resource order (silk order left reversed to ease routing).

## Connectors

- **USB-C**: configuration and firmware flashing
- **U8**: 6-pin SMD JST SH digital VTX connector, Betaflight standard pinout (+10V/GND/TX/RX/GND/SBUS)
- **P1**: 8-pin JST SH (SM08B-SRSS-TB) ESC harness
- I2C0 expansion pads (SDA/SCL, pull-ups to 3.3V)

## Serial and I/O

- **UART0** (GPIO0/1): digital VTX / MSP DisplayPort
- **UART1** (GPIO6/7): external serial RX (CRSF/SBUS/etc.)
- **PIO UART0** (GPIO2/3): software UART, default GPS
- **I2C0** (GPIO4/5): external expansion
- **SPI1** (GPIO10/11/12, CS=GPIO13, INT=GPIO9): IMU
- **SPI0** (GPIO18/19/20, CS=GPIO21): microSD blackbox

## Analog inputs

- VBAT sense (GPIO29 / ADC3): divider + 1k+100nF RC filter
- ESC current sense (GPIO28 / ADC2): onboard sense circuit, 1k+100nF RC filter

The QFN-60 has only 4 ADC channels; GPIO26/27 are used as digital LED0 and 10V-enable, leaving GPIO28/29 for VBAT and current. The separate RSSI and external-ADC inputs from the QFN-80 layout are not available on this part.

## Additional I/O

- Addressable LED strip output (GPIO8, PIO2)
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
- Driven by RP2354A PIO2: pixel-level timing for character overlay on PAL/NTSC composite

## PIO allocation

The RP2350 has 3 PIO blocks x 4 state machines (12 total):

| Block | Function |
|---|---|
| PIO0 | DShot motor output (4 SMs, one per motor) |
| PIO1 | Software UART (PIO UART0, TX and RX programs) |
| PIO2 | LED strip + analog OSD pixel timing |

## Firmware

A custom Betaflight target (`OPENFC_LITE_MINI_RP2350A`, `MANUFACTURER_ID = OPFC`) defines:

- Motor map matching the silkscreen (M1..M4 = GPIO25..GPIO22) via the DShot resource order
- `USE_SDCARD_SPI` on SPI0 for blackbox
- `USE_PINIO` on GPIO27 for the switchable 10V VTX rail
- FB_OSD wired but disabled by default. The RP2350 FB_OSD driver is merged upstream (betaflight/betaflight#14882, merged 2026-04-22).

The target config is not yet published in [betaflight/config](https://github.com/betaflight/config); building requires adding the target files to a Betaflight checkout (with `pico-sdk` and the BF-pinned ARM toolchain):

```sh
make picotool_install
make arm_sdk_install
make CONFIG=OPENFC_LITE_MINI_RP2350A
```

Output is a `.uf2` in `obj/`. Hold BOOTSEL, plug in USB, and drag the UF2 onto the `RP2350` mass-storage drive that mounts.

Betaflight PICO supports SD blackbox over SPI only (PR #14567, no SDIO under `src/platform/PICO/`), so the microSD is wired for SPI even though the slot routing is SDIO-compatible. SBUS inversion is handled at the RP2350 pad IO-mux (`gpio_set_inover/outover(GPIO_OVERRIDE_INVERT)`), auto-set for SBUS on native and PIO UARTs, so there is no hardware inverter: the RX line wires straight to a UART RX GPIO.

## Variants and revisions

This repo is the 20x20 member of the OpenFC-Lite family. Its sibling [OpenFC-Lite](https://github.com/incutec-hw/OpenFC-Lite) (30.5 x 30.5 mm, RP2354B QFN-80: bigger pads, more I/O, OSD debug pads) shares this design. Fabrication sets are generated per revision into `hardware/production/` (gitignored) with the Fabrication Toolkit; the revision history is in [CHANGELOG.md](../../CHANGELOG.md). Open engineering items are tracked in [`hardware/research/open-items.md`](../research/open-items.md).
