# Open items, Rev 2

Unresolved items carried out of the Rev 2 change log. Resolve before the next production
export.

## U3/U4 BOM fields stale after buck upgrade

U3/U4 were changed from LMR51420YDDCR (2 A) to LMR51430YFDDCR (3 A, LCSC C5219261), same
SOT-23-6, but the symbol fields were not fully updated: the Value still carries a `TI `
prefix and the MPN/LCSC field still reads `LMR51420YDDCR`. Clean both fields so LCSC/MPN
exact-match resolves to the LMR51430 (C5219261) for assembly.

## D1 USB ESD protection (USBLC6-2P6) not placed

D1 is currently not placed. Restoring it is recommended: USB is the most-handled and
most-exposed interface, the RP2354A PHY is not rated for system-level ESD
(IEC 61000-4-2, 8 kV), and the part is tiny, cheap, and low-capacitance. Decision
pending.

## FB_OSD upstream driver not merged

The RP2350 analog-OSD driver PR stack (betaflight/betaflight#14882) is still open
upstream; there is no flyable upstream binary yet. The custom target wires the FB_OSD
framework but ships it disabled by default. Track the PR stack before tape-out.
