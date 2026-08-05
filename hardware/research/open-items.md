# Open items, Rev 2

Unresolved items carried out of the Rev 2 change log. Resolve before the next production
export.

## U3/U4 BOM fields carry a `TI ` prefix

U3/U4 were changed from LMR51420YDDCR (2 A) to LMR51430YFDDCR (3 A, LCSC C5219261), same
SOT-23-6. The MPN field now reads `TI LMR51430YFDDCR` (correct part) and the LCSC field
reads `C5219261` (correct). Remaining work: strip the `TI ` prefix from the Value and MPN
fields so MPN exact-match resolves cleanly, and optionally rename the library symbol,
which is still named `lib:LMR51420YDDCR`.

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
