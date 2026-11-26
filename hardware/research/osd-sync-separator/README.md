# Analog OSD sync separator: why it fails with some cameras

Research of 2026-10-25 into the composite video sync separator of the `osd` sheet (RP2354 PIO analog OSD, Betaflight
FB_OSD at master `d593400a`). Datasheets are linked inside the notes. Values marked "my calc" in the notes are
calculations: SPICE and a scope check come first.

## Finding

The discrete circuit (Schottky clamp to GND, comparator threshold at 0 V) puts the threshold one diode Vf above the sync
tip, so a low-sync or double-terminated camera never crosses it. Two fixes are proposed:

| Fix | What |
| --- | --- |
| (a) Bodge on the same footprints | Clamp to about +0.4 V, 1 Mohm bleed, threshold from a matched second diode about 60 to 70 mV above the tip, fast push-pull comparator |
| (b) Robust | Dedicated separator LMH1980 with CSOUT direct to the GPIO |

Recommended order in the notes: scope the sync pin first, then bodge (a) on one board, and move to the dedicated
separator in the next revision only if a camera still fails.

## Notes

| Note | Content |
| --- | --- |
| [sync_separator_designs.md](notes/sync_separator_designs.md) | Sync separator options and the two proposed fixes |
| [camera_cvbs_compatibility.md](notes/camera_cvbs_compatibility.md) | CVBS level variation between analog FPV cameras against the current circuit |
| [betaflight_fbosd_reference.md](notes/betaflight_fbosd_reference.md) | Betaflight RP2350 FB_OSD: reference hardware and what the firmware expects on the sync pin |
