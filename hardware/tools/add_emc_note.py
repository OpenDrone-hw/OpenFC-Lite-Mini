#!/usr/bin/env python3
"""Add the EMC checklist as a textbox on the root schematic. Non-destructive.

The checklist text is read from EMC_CHECKLIST.md next to this script, so there is
only one copy of it in the repo.
"""
import kicad_sch_api as ksa
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(os.path.dirname(TOOLS), "OpenFC.kicad_sch")
CHECKLIST_MD = os.path.join(TOOLS, "EMC_CHECKLIST.md")


def load_checklist():
    """Return the checklist as plain text for the schematic textbox."""
    with open(CHECKLIST_MD) as f:
        lines = f.read().splitlines()
    out = []
    for line in lines:
        # Strip markdown heading markers and bold/code markers; keep the words.
        line = line.lstrip("#").strip() if line.startswith("#") else line
        line = line.replace("**", "").replace("`", "")
        out.append(line)
    return "\n".join(out).strip()


def main():
    if not os.path.exists(CHECKLIST_MD):
        print(f"ERROR: {CHECKLIST_MD} not found", file=sys.stderr)
        return 1

    print(f"Loading {ROOT}")
    sch = ksa.load_schematic(ROOT)

    # Place bottom-left, below all existing sheets
    # Existing sheet bounds: y max ~162.56, x: 31 to 218
    # A3 page ~420x297 or A4 297x210
    text_uuid = sch.add_text_box(
        text=load_checklist(),
        position=(12.7, 170.18),
        size=(250.0, 100.0),
        font_size=1.0,
        margins=(1.5, 1.5, 1.5, 1.5),
        stroke_width=0.15,
        stroke_type="default",
        justify_horizontal="left",
        justify_vertical="top",
    )
    print(f"Added text box uuid={text_uuid}")

    sch.save(ROOT)
    print(f"Saved {ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
