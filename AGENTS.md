# Agent notes

Facts for AI agents working in this repo.

- KiCad 10 project. Top schematic `hardware/OpenFC.kicad_sch` (hierarchical: `rp2350a`, `power`, `imu`, `osd`, `blackbox`, `pads` sub-sheets), board `hardware/OpenFC.kicad_pcb` (6 copper layers).
- Clone with `git clone --recursive`; the `libs/KiCad-Library` submodule is referenced by the project lib tables for shared parts. Project-local libraries: `hardware/lib.kicad_sym`, `hardware/lib.pretty/`, `hardware/lib.3dshapes/`.
- Never edit `.kicad_*` files as text. Use kicad-skip or the pcbnew API, and only for metadata (text variables, symbol BOM/doc fields). Never change nets, placement, or component values.
- Checks and exports:

```
kicad-cli sch erc --exit-code-violations hardware/OpenFC.kicad_sch
kicad-cli pcb drc --exit-code-violations hardware/OpenFC.kicad_pcb
kicad-cli sch export netlist --format kicadsexpr -o /tmp/OpenFC.net hardware/OpenFC.kicad_sch
```

- Fabrication Toolkit config: `hardware/fabrication-toolkit-options.json` (tracked). Exports land in `hardware/production/` (gitignored).
- Design detail: `hardware/docs/DESIGN.md`. Engineering research and open items: `hardware/research/`.
- Docs are deterministic: current fact only, no TODOs or plans.
- `main` is protected; push feature branches and open PRs.
