# OpenFC-Lite-Mini EMC Checklist

Written against the Rev 2 RP2354A design. Refdes and pad numbers are from
`hardware/OpenFC.kicad_pcb`.

## Noise sources (ranked by threat)

| Source | Frequency | Notes |
|---|---|---|
| LMR51430 bucks U3, U4 | 1.1 MHz fundamental + harmonics to ~200 MHz | Strongest radiator |
| RP2354A internal core buck (L4) | ~400 kHz variable | Hard to isolate, close to MCU |
| 12 MHz crystal X1 | 12 MHz + harmonics | Can alias into RX bands |
| DShot600 motor outputs | 600 kHz, 12-20 ns edges | Broadband from fast edges |
| SPI1 IMU clock | up to 10 MHz | Low level, well shielded |
| SPI0 SD card | up to 25 MHz | Bursty, noisy |
| USB D+/D- | 12 Mbps FS | Contained if routed right |

## 1. Buck switch node loops (L2, L3)

- CIN GND + COUT GND on local top-side island, NOT merged into main GND pour
- 2 adjacent stitching vias per buck to inner GND plane
- SW node: just wide enough for current (~0.5 mm), short (<5 mm), minimum area
- No GND pour directly under SW trace on top AND on layer 2
- No GND pour directly under inductor body
- L2 and L3 >5 mm apart (avoid mutual coupling)
- FB trace away from SW node, under a GND shield layer

## 2. Core SMPS node (L4)

- RP2350 datasheet section 6.3.8.1: VREG input cap, L4 and VREG output cap stay on the MCU side
- Copper cut away under the VREG_LX node on the top layer and on layer 2
- GND return to the QFN centre pad via 2 adjacent vias

## 3. IMU (U9) immunity

- Place >=10 mm from any switch node (L2, L3, L4)
- Over solid inner GND plane, no splits underneath
- 1.8V_GYRO rail: continuous GND return, no crossings
- NCV8187 LDO (U6) output within 5 mm of IMU VDD pin
- IMU CS/SCK/MOSI/MISO tightly grouped with GND ref, NOT over SW nodes
- 100 nF VDD + 100 nF VDDIO within 1 mm of pins
- SPI0 (SD card) not parallel to SPI1 (IMU) with <0.5 mm spacing

## 4. ADC inputs (VBAT, ESC current)

- RC filters (1k + 100nF) within 5 mm of MCU ADC pins (already in schematic)
- ADC traces short, routed over GND plane
- VBAT divider resistors away from buck switch nodes
- No long traces parallel to digital clocks

The QFN-60 carries only these two analog inputs. RSSI and external-ADC inputs do not
exist on this board.

## 5. USB D+/D-

- 30 ohm series R (R15/R24/R37) immediately next to MCU pads 51/52
- 90 ohm differential impedance target
- Continuous GND plane beneath full length, no splits
- GND stitching vias flanking any layer transition
- ESD diode AT the connector (not near the MCU). **D1 (USBLC6-2P6) is currently unpopulated**,
  see `hardware/research/open-items.md`
- CC1/CC2 5.1 kOhm pull-downs present and correct

## 6. Motor outputs M1-M4

- On board edge (already - P1)
- 22-33 ohm series R in-line at MCU (currently 0 ohm)
- Route over GND plane, distance from IMU
- DShot edges radiate

## 7. Crystal X1 (12 MHz)

- Crystal + 2 load caps directly under XIN/XOUT pads (21/22), <3 mm stubs
- GND guard ring tied to inner plane via 2+ vias
- No ground flood BETWEEN XIN/XOUT traces
- Load caps same side as crystal
- No high-speed signals within 5 mm

## 8. Power rail filtering / bulk caps

- Bulk 47-100 uF low-ESR electrolytic at BATT input (ceramics alone insufficient)
- +5V and +10V outputs: ferrite bead + bulk cap at each connector (VTX, RX)
- Common-mode choke or ferrite bead on VTX 10V line helps conducted EMI
- Large ground copper area around each regulator

## 9. Connector ESD / surge

- TVS 5V uni-directional on every external I/O pad:
  - RX UART, SBUS, LED strip, buzzer, current sense, camera video
- No external pad currently has ESD protection: USB D1 is unpopulated
- Series R (100-470 ohm) on LED strip + ESD diode
- Series R on beeper drive

## 10. GND plane topology (6-layer)

- Solid continuous GND plane on layer 2 under top signals, no splits
- No separate analog/digital GND islands
- Star point: all power-entry GNDs meet at same pour region
- GND stitching vias every 5-10 mm
- No splits under IMU, ADC pins, or crystal

## 11. RX / VTX rail considerations

- No onboard RF: the RX is external, over UART
- LED_STRIP output kept away from UART lines (WS2812 bursts noisy)
- 10V VTX rail traces >=20 mil wide, inner plane or heavy top/bottom copper
- Bulk 22-47 uF electrolytic at VTX connector for load transients
- Optional: ferrite bead in series before bulk cap

## 12. Signal integrity

- DShot600 PIO outputs: if trace >30 mm, add 22-33 ohm series termination
- SPI0 (SD card) at 25 MHz: <50 mm bus, same layer, continuous GND ref
- LED_STRIP 1 MHz bursts: 22 ohm series at MCU output

## 13. Shielding / enclosure

- Mounting hole via stitches for frame-as-shield (optional)
- Conformal coating over buck area (usually not needed for FPV)

## Priority

**Must-fix before fab:**
1. Buck hot-loop GND islands + separate stitching vias (U3, U4)
2. SW node area minimization + copper cutaway beneath
3. IMU physical distance from L2/L3/L4 (>=10 mm)
4. USB ESD placed AT connector, GND continuity under diff pair
5. Crystal guard ring + direct placement under XIN/XOUT

**Strongly recommended:**
6. 22-33 ohm series on motor lines + LED strip
7. ESD diodes on RX UART, current sense and video pads
8. Bulk electrolytic at battery input and VTX connector
9. Ferrite bead + bulk on 5V/10V outputs to connectors

**Nice to have:**
10. Common-mode choke on USB D+/D-
11. Conformal coating zone around bucks
