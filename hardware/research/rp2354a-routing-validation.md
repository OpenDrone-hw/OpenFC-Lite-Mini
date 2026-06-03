# RP2354A Routing Validation vs RP2350 silicon + Betaflight PICO

**Date:** 2026-06-03 · MCU swapped from RP2354B (U2, QFN-80) → **RP2354A (U10, QFN-60, GPIO0–29)**.
Validated against (a) RP2350 datasheet GPIO function mux (Table 3) + pico-sdk `io_bank0.h`, and
(b) Betaflight PICO platform code in `betaflight/src/platform/PICO`. All 30 GPIO are allocated —
**zero spare**.

## Current pin map (from netlist, U10)

| GPIO | Function | Verdict |
|---|---|---|
| 0 | UART0 TX (VTX data) | ✅ HW UART0 TX valid |
| 1 | UART0 RX (VTX data) | ✅ HW UART0 RX valid |
| 2 | PIO-UART0 TX | ✅ PIO any pin |
| 3 | PIO-UART0 RX | ✅ PIO any pin |
| **4** | **I2C0 SCL** | ❌ **BUG — GPIO4 is hardware I2C0 SDA, not SCL** |
| **5** | **I2C0 SDA** | ❌ **BUG — GPIO5 is hardware I2C0 SCL, not SDA** |
| 6 | BEEPER | ✅ PWM any pin |
| 7 | LED strip (WS2812) | ✅ PIO |
| 8 | UART1 TX (ext RX) | ✅ HW UART1 TX valid |
| 9 | UART1 RX (ext RX / VTX SBUS) | ✅ HW UART1 RX valid; SBUS inversion via GPIO INOVER on HW UART ✓ |
| 10 | SPI1 SCK (microSD) | ✅ HW SPI1 SCK valid |
| 11 | SPI1 MOSI | ✅ |
| 12 | SPI1 MISO | ✅ |
| 13 | SPI1 CS | ✅ (CS = any GPIO) |
| 14 | OSD_W | ✅ FB_OSD needs 3 consecutive, lowest=W |
| 15 | OSD_EN | ✅ = W+1 |
| 16 | OSD_SYNC | ✅ = EN+1 |
| 17 | GYRO_INT | ✅ EXTI any GPIO |
| 18 | SPI0 SCK (IMU) | ✅ HW SPI0 SCK valid |
| 19 | SPI0 MOSI | ✅ |
| 20 | SPI0 MISO | ✅ |
| 21 | IMU CS | ✅ |
| 22–25 | M4/M3/M2/M1 (DShot) | ✅ PIO0, no consecutive requirement, in-window |
| 26 | ADC0 VBAT | ✅ ADC range 26–29 |
| 27 | ADC1 CURRENT | ✅ |
| 28 | 10V_ENABLE (digital out) | ✅ (spends an ADC pin on digital — fine) |
| 29 | LED0 status (digital out) | ✅ |

## Issue 1 — I2C0 SDA/SCL swapped (BLOCKING, schematic fix)
Both the RP2350 silicon mux **and** the BF PICO I2C driver require **even GPIO = SDA, odd = SCL**:
GPIO4 = I2C0 **SDA**, GPIO5 = I2C0 **SCL**. Schematic has them reversed. BF `bus_i2c_pico.c`
hard-enforces `SDA%4==0 / SCL%4==1` and **silently fails to bind the device** otherwise; hardware
I2C0 cannot remap the polarity. **Fix (Stan, schematic): swap so GPIO4=I2C0_SDA, GPIO5=I2C0_SCL.**
(Matches the rule already noted in CLAUDE.md.) Only matters if I2C is used (external/optional —
no onboard baro), but it's wrong as drawn.

## Issue 2 — OSD + LED cannot share one PIO block (FIRMWARE config, no respin)
Verified program sizes in BF source: OSD steady-state `osd_tx_pal/ntsc` = **31 instr / 1 SM**
(`osd_tx.pio.h:60`); WS2812 = **4 instr / 1 SM** (4-entry array, `light_ws2811strip_pico.c:63`).
A PIO block has **32 instruction slots** total. 31 + 4 = **35 > 32** → `pio_add_program` for the
second one fails. SM count is fine (2/4); instruction memory is the limiter. BF's RP2350A
`target.h` defaults *both* `PIO_LEDSTRIP_INDEX=2` and `PIO_OSD_INDEX=2` → latent collision.
**Fix is firmware-only:** board wires only **one** PIO UART (PIOUART0 GPIO2/3), so PIO1 has room.
Set **`PIO_LEDSTRIP_INDEX=1`**. Final PIO map: PIO0 = 4× DShot; PIO1 = PIOUART0 (2 SM) + WS2812
(1 SM, 4 instr); PIO2 = OSD (1 SM, 31 instr). All fit. **No board change.**

## BMI270 / IMU — fully valid ✅
- SPI0 on GPIO18/19/20/21 is a textbook-correct SCK/MOSI/MISO/CSn quad. BMI270 driver SPI = 10 MHz,
  ICM-426xx = 24 MHz — both within the bus. INT on GPIO17 (EXTI, unconstrained). CS GPIO21.
- Footprint drop-in confirmed earlier (§8c of imu-selection): BMI270, ST LSM6D\*, TDK 426xx/456xx all fit.
- **CLKIN is not wired to the MCU** (`/IMU/CLKIN` dead-ends at U9.9 — no free GPIO on the A). Fine for
  ST/Bosch (pin 9 = INT2, unused). A TDK 426xx would lose its CLKIN jitter removal — accept, or free a pin.

## Constraints created by the RP2354A (30 GPIO, all used)
- **Zero spare GPIO.** No room for CLKIN, GPS, a 2nd PIO UART, or analog RSSI without dropping something.
- **Only 2 ADC used** (VBAT, CURRENT). Analog RSSI and EXT-ADC are gone (GPIO28/29 spent on 10V_EN + LED0).
  Fine for digital/ELRS RX (RSSI via telemetry); note if analog RSSI is ever wanted.
- **SWCLK/SWDIO (pads 24/25) unconnected.** Recommend breaking SWD out to debug pads (lesson from the
  OSD no-debug-pads regret) — costs no GPIO (dedicated pins).
- Hardware UART count = 2 (UART0 VTX, UART1 ext-RX/SBUS) + 1 PIO UART. SBUS must stay on the **hardware**
  UART — BF PICO **PIOUART RX inversion does not work** (gpio_set_function clobbers INOVER); only the HW
  UART path keeps the invert. So SBUS on GPIO9 (HW UART1) = correct; do not move it to the PIO UART.

## Change-list (for Stan)
1. **Swap I2C0 SDA/SCL** → GPIO4=SDA, GPIO5=SCL. (schematic)
2. **Firmware:** `PIO_LEDSTRIP_INDEX=1` so OSD (PIO2) and LED (PIO1) don't overflow PIO2. (config)
3. Consider breaking out **SWD** (pads 24/25) to debug pads. (schematic, free)
4. Note CLKIN unwired — accept for ST/Bosch; only an issue if committing to a TDK 426xx for jitter removal.
