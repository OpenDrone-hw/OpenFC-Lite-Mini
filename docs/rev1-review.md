---
date: 2026-06
---

# Rev 1 bench review

Findings from the bench review of Rev 1 (June 2026). Check each point against the current revision before acting on
it: later revisions may already address it.

| # | Area | Finding |
| --- | --- | --- |
| 1 | IMU | The gyro has a SYNC/CLKIN line, but this gyro has no sync input (only the ICM parts and some older ST parts do) |
| 2 | Schematic | Swap CLKIN for CS on the SPI bus: CS belongs with MISO, MOSI and SCK. Same for `FLASH_CS` |
| 3 | Blackbox | Wire the SD card so both SPI and SDIO work: SPI now, SDIO once Betaflight supports it on the RP2350 |
| 4 | USB | USB series resistors should be 27 Ohm per Raspberry Pi, not 30 (R12, R13); the AVDD resistor (R14) 33 Ohm, not 30 |
| 5 | ESD | ESD protection on USB only is inconsistent with the other pads; decide whether it is needed at all |
| 6 | LEDs | 0201 LEDs break when the stack nut is tightened: use 0402 or move them out of tool reach, and recalculate the resistors (the LEDs are too bright) |
| 7 | Power | Clarify TPS2116 versus TPS2117 for the power multiplexer |
| 8 | SBUS | Remove the SBUS inverter |
| 9 | Mounting | Change the hole size to 4 mm |
| 10 | Silkscreen | Match pad names to Betaflight resource names (PIOUART and the rest) |
