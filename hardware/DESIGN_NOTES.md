# Design Notes

Engineering notes extracted from the on-canvas comments in the KiCad schematic
(`*.kicad_sch`). This file is the human-readable mirror of the design rationale
annotated directly on the sheets — keep the two in sync.

> **Variant note:** these notes were authored on the RP2354**B** sibling design.
> This repository is the RP2354**A** variant; the MCU package, GPIO count, and a
> small amount of I/O (e.g. one UART) differ. Notes are reproduced verbatim; lines
> that are explicitly MCU-variant-specific are flagged inline.

---

## Power (`power.kicad_sch`)

**Topology:** power delivery circuitry for the flight controller.

### Buck regulators (LMR51430)
- 4.5–36 V input · synchronous buck · 1.1 MHz switching.
- `LMR51430` = 3 A output, `LMR51420` = 2 A output (pin-compatible).
- FPWM version of the LMR51430 chosen for less output ripple at low voltage and
  more consistency, at the cost of efficiency.

**Vout calculations** — `Vout = Vref × (1 + R_top / R_bottom)`, Vref = 0.6 V:
- **+10 V rail (U3):** `0.6 × (1 + 100 / 6.49) = 0.6 × 16.408 = 9.845 V`
- **+5 V rail (U4):** `0.6 × (1 + 100 / 13.7) = 0.6 × 8.299 = 4.980 V`

### 5 V power MUX (TPS2116 / TPS2117)
- Switches up to 4 A (TPS2117) from `+5V_USB` or `+5V_BUCK` to `+5V`.
- Prefers buck over USB; threshold voltage ≈ 3.5 V.
- The threshold is deliberately low to prevent accidental switchover to USB during
  peak consumption (worst case in flight). Two diodes ease the switchover.

### 1.8 V gyro LDO
- 1.8 V, 1.2 A LDO, high PSRR.
- 1.2 A is far more than needed, but: PSRR of 80 dB up to 10 kHz.
- Power-Good output drives an LED. Max 30 mA on PG (open-collector/drain);
  datasheet assumes 6 mA for a typical application.

### 3.3 V main LDO
- 3.3 V, 0.5 A main LDO.
- Up to 6.5 V input (from 5 V) · thermal protection · short-circuit protection ·
  reverse-current protection · low noise for RF and analog circuits.

---

## MCU & peripherals (`rp2350a.kicad_sch`)

**Topology:** RP2350 pin mapping and universal peripherals.

- **[B-variant note]** RP2354B: larger variant with integrated flash (2 MB) and more GPIO.
- **[variant note]** 2354 variant has internal flash; SS pull-down for boot mode.
- Decoupling caps: place close to the IC — one is enough for two adjacent pins.
- `4.7 µF` on the opposite side of the regulator.
- **Crystal:** per datasheet — 10 pF loading plus stray capacitance ≈ 12 pF.
- **Core supply:** 1.1 V SMPS per RP datasheet — inductor polarity is important.
- **ADC / VREG:** RC low-pass filters on ADC and VREG, as in the Pico datasheet.
- **VBAT sense:** 1/11 scale divider.
- **LED strip:** WS2812 level shifting — most accept 3.3 V logic, but 5 V is more robust.
- **Buzzer:** N-MOS low-side switch.
- Peripheral intents annotated on sheet: MSP DisplayPort / VTX, CRSF receiver,
  GPS (external), extra external UART, I²C for external sensors, status LED, USB port.

---

## IMU (`imu.kicad_sch`)

**Topology:** IMU SPI wiring and local decoupling.

- **Universal IMU wiring + LGA footprint** — accepts BMI270, LSM6, TDK, etc.
- **CLKIN:** not supported by the LSM6DSV16XTR, but it is just a simple wire and
  may be used with other pin-compatible IMUs. Left in place, at least for testing.

---

## Analog OSD (`osd.kicad_sch`)

**Topology:** analog OSD using a PIO state machine on the RP2350. Video path:

- **Input:** 75 R input termination.
- **Sync detection:** comparator detects sync pulses, read by RP2350 PIO.
  `VID_DC` clamped to ≈ −0.2 V DC.
- **Chroma filter:** fc = 500 kHz.
- **DC restoration** stage.
- **Pixel select:** SPDT analog switch. A resistor divider lets the GPIO port
  select between high (VOH = 1 V → white) and low (VOL = 0.3 V → black) pixels.
- **Output:** non-inverting buffer for low output impedance; 6 dB gain for 75 R
  source and 75 R termination at the VTX.

---

## Blackbox (`blackbox.kicad_sch`)

- SPI wiring and local decoupling for the microSD card slot.

---

## Pads & I/O (`pads.kicad_sch`)

- Solder pads and JST connectors for I/O.
- **[variant note]** All solder pads broken out on the 30×30 Lite variant.
- Broken-out lines: free UART (GPS), free UART (extra), digital video connector,
  ESC, buzzer, I²C out, extra ADC, RSSI, arm-mounted LED strip, RX pads (for when
  broken off).
