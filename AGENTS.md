# OpenFC-Lite-Mini

Open-source RP2350 flight controller, 20 x 20 mm mounting pattern.

Validate: `kicad-cli sch erc hardware/OpenFC.kicad_sch && kicad-cli pcb drc --schematic-parity --refill-zones hardware/OpenFC.kicad_pcb`

## Boundaries

- Sourcing (suppliers, prices, quotes, RFQs, contacts) never lives in OpenDrone repositories.
- Never text-edit `.kicad_sch`, `.kicad_pcb` or `.kicad_dru`: use KiCad, or kicad-skip / the pcbnew API with KiCad closed. `.kicad_pro` is JSON and may be edited for metadata.
- Agents write metadata fields only (MPN, Manufacturer, LCSC, Datasheet, text variables), never nets, wiring, routing, placement, footprint assignment or circuit values.
- KiCad libraries stay project-local; import parts with `easyeda2kicad` only.
- KiCad files do not merge: one person holds a board layout at a time.

## Pointers

- Shared parts catalogue: `hardware/KiCad-Library/PARTS-USED.md`
- Release standard: https://github.com/OpenDrone-hw/.github/blob/main/RELEASES.md
