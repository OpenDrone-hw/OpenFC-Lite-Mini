# Open items, Rev 2

Unresolved items carried out of the Rev 2 change log. Resolve before the next production
export.

## U3/U4 BOM fields carry a `TI ` prefix

Background on the part change: [`hardware/docs/DESIGN.md`](../docs/DESIGN.md), Rev 2 > Power.
Remaining work: strip the `TI ` prefix from the Value and MPN fields on U3/U4 so MPN
exact-match resolves cleanly, and optionally rename the library symbol, which is still named
`lib:LMR51420YDDCR`.

## D1 USB ESD protection (USBLC6-2P6) not placed

D1 is currently not placed. Restoring it is recommended: USB is the most-handled and
most-exposed interface, the RP2354A PHY is not rated for system-level ESD
(IEC 61000-4-2, 8 kV), and the part is tiny, cheap, and low-capacitance. Decision
pending.

## FB_OSD bench verification pending

The RP2350 FB_OSD driver merged upstream on 2026-04-22 (betaflight/betaflight#14882;
`src/platform/PICO/osd/` now exists upstream). The custom target wires the FB_OSD
framework but ships it disabled by default. Remaining work: bench-verify the analog OSD
chain with FB_OSD enabled on Rev 2 hardware.

## PIO block for the LED strip

[`hardware/docs/DESIGN.md`](../docs/DESIGN.md) puts the LED strip and the analog OSD on PIO2.
A program-size check against Betaflight source says they do not fit together: the OSD
steady-state program `osd_tx_pal/ntsc` is 31 instructions (`osd_tx.pio.h`) and WS2812 is 4
(`light_ws2811strip_pico.c`), against 32 instruction slots per PIO block, so `pio_add_program`
fails for whichever loads second. State-machine count is not the limit (2 of 4 used).

The board wires only one PIO UART (PIO UART0), so PIO1 has room: setting
`PIO_LEDSTRIP_INDEX=1` gives PIO0 = 4x DShot, PIO1 = PIO UART0 + WS2812, PIO2 = OSD.
Betaflight's RP2350A `target.h` defaults both `PIO_LEDSTRIP_INDEX` and `PIO_OSD_INDEX` to 2.

Remaining work: confirm the program sizes against the Betaflight tree actually built, then
fix the PIO allocation table in DESIGN.md to whichever map is right. Firmware configuration
only, no board change.

## OSD op-amp output headroom on +3.3 V

U1 (COS8051SOT) runs from +3.3V. With the DC-restore front end biasing the sync tip
0.3-0.5 V above ground and the stage running at gain 2, a 1 Vpp composite input puts the
output close to the rail. Remaining work: measure the output swing on Rev 2 hardware and
decide whether U1 needs moving to +5V.
