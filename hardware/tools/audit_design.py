#!/usr/bin/env python3
"""OpenFC Lite 20x20 design audit.

Exports the schematic netlist with kicad-cli and writes a part, GPIO and
Betaflight-guideline report to hardware/tools/design_audit.md (not tracked).
Nothing is hardcoded per revision: the MCU, IMU and microSD slot are found by
value or footprint, and the GPIO functions are read from the GPIO map table in
AGENTS.md, so the report checks the schematic against that table.

  python3 hardware/tools/audit_design.py [--kicad-cli PATH]

Exit status 1 when a check fails.
"""

from __future__ import annotations

import argparse
import collections
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HW = Path(__file__).resolve().parents[1]
REPO = HW.parent
SCH = HW / "OpenFC.kicad_sch"
AGENTS = REPO / "AGENTS.md"
OUT = HW / "tools" / "design_audit.md"
MAC_CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"

PASSIVE = re.compile(r"^(R|C|L|FB|TP)\d")
RAIL_33 = re.compile(r"(^|/)\+?3(\.3|V3)V?$", re.I)


# ---------- netlist ----------

def parse_sexpr(text: str):
    tokens = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', text)
    stack, cur = [], []
    for t in tokens:
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            done = cur
            cur = stack.pop()
            cur.append(done)
        else:
            cur.append(t[1:-1].replace('\\"', '"') if t.startswith('"') else t)
    return cur[0]


def children(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def value(node, key, default=""):
    for c in children(node, key):
        return c[1] if len(c) > 1 and isinstance(c[1], str) else default
    return default


def export_netlist(cli: str):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "board.net"
        subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadsexpr",
                        "-o", str(out), str(SCH)], check=True, capture_output=True)
        root = parse_sexpr(out.read_text())

    parts = {}
    for comp in children(children(root, "components")[0], "comp"):
        props = {value(p, "name"): value(p, "value") for p in children(comp, "property")}
        sheet = ""
        for sp in children(comp, "sheetpath"):
            sheet = value(sp, "names").strip("/") or "root"
        parts[value(comp, "ref")] = {
            "value": value(comp, "value"),
            "footprint": value(comp, "footprint").split(":")[-1],
            "mpn": props.get("MPN", ""),
            "lcsc": props.get("LCSC", ""),
            "dnp": "dnp" in props,
            "sheet": sheet,
        }

    nets = {}       # net name -> [(ref, pin, function)]
    pin_net = collections.defaultdict(dict)  # ref -> pin -> net
    for net in children(children(root, "nets")[0], "net"):
        name = value(net, "name")
        nodes = [(value(n, "ref"), value(n, "pin"), value(n, "pinfunction"))
                 for n in children(net, "node")]
        nets[name] = nodes
        for ref, pin, _ in nodes:
            pin_net[ref][pin] = name
    return parts, nets, pin_net


# ---------- AGENTS.md GPIO map ----------

def documented_gpio():
    text = AGENTS.read_text()
    m = re.search(r"### GPIO map\n(.*?)(\n\n|\Z)", text, re.S)
    if not m:
        sys.exit("AGENTS.md has no '### GPIO map' table")
    doc = {}
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 2 or not re.match(r"^\d", cells[0]):
            continue
        nums = []
        for part in cells[0].split(","):
            a, _, b = part.strip().partition("-")
            nums += range(int(a), int(b or a) + 1)
        for n in nums:
            doc[n] = cells[1]
    return doc


# ---------- helpers ----------

def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out)


def two_pin_partner(pin_net, ref, net):
    """For a two-pin part on `net`, the net on its other pin."""
    others = [n for n in pin_net[ref].values() if n != net]
    return others[0] if len(pin_net[ref]) == 2 and others else None


def caps_to_gnd(nets, pin_net, net):
    return sorted({r for r, _, _ in nets.get(net, []) if r.startswith("C")
                   and two_pin_partner(pin_net, r, net) == "GND"})


def pullup_33(nets, pin_net, net):
    return sorted({r for r, _, _ in nets.get(net, []) if r.startswith("R")
                   and RAIL_33.search(two_pin_partner(pin_net, r, net) or "")})


def find_ref(parts, pattern, field="value"):
    refs = [r for r, p in parts.items() if re.search(pattern, p[field], re.I)]
    return sorted(refs)[0] if refs else None


# ---------- audit ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--kicad-cli", default=shutil.which("kicad-cli") or MAC_CLI)
    args = ap.parse_args()

    parts, nets, pin_net = export_netlist(args.kicad_cli)
    doc = documented_gpio()
    lines, findings = [], []
    W = lines.append

    mcu = find_ref(parts, r"RP235")
    imu = find_ref(parts, r"BMI2|ICM-?4|LSM6")
    sd = find_ref(parts, r"TF-|micro ?SD")
    if not mcu:
        sys.exit("no RP235x found in the schematic")

    W("# OpenFC Lite 20x20 design audit\n")
    W(f"Netlist exported from `{SCH.name}` with kicad-cli. MCU {mcu} ({parts[mcu]['value']}), "
      f"IMU {imu} ({parts[imu]['value'] if imu else '-'}), microSD {sd or '-'}.\n")

    # 1. Parts
    W("## 1. Active parts and connectors\n")
    rows = []
    for ref in sorted(parts, key=lambda r: (re.sub(r"\d", "", r), int(re.sub(r"\D", "", r) or 0))):
        p = parts[ref]
        if PASSIVE.match(ref):
            continue
        rows.append([ref + (" DNP" if p["dnp"] else ""), p["value"], p["mpn"] or "-",
                     p["lcsc"] or "-", p["footprint"], p["sheet"]])
    W(md_table(["Ref", "Value", "MPN", "LCSC", "Footprint", "Sheet"], rows))
    counts = collections.Counter(PASSIVE.match(r).group(1) for r in parts if PASSIVE.match(r))
    W("\nPassives: " + ", ".join(f"{n} {k}" for k, n in sorted(counts.items())) + ".\n")

    # 2. GPIO map against AGENTS.md
    W("## 2. GPIO map: schematic against AGENTS.md\n")
    wired = {}
    for pin, net in pin_net[mcu].items():
        for r, p, func in nets[net]:
            if r == mcu and p == pin:
                m = re.match(r"GPIO(\d+)", func)
                if m:
                    wired[int(m.group(1))] = net
    rows = []
    for g in sorted(set(wired) | set(doc)):
        net = wired.get(g, "")
        others = sorted({r for r, _, _ in nets.get(net, []) if r != mcu})
        status = "ok"
        if g not in doc:
            status = "**not in AGENTS.md**"
        elif not net or net.startswith("unconnected"):
            status = "**documented, not wired**"
        rows.append([g, doc.get(g, "-"), net or "-", ", ".join(others) or "-", status])
        if status != "ok":
            findings.append(("MED", f"GPIO{g}: {status.strip('*')}"))
    W(md_table(["GPIO", "AGENTS.md function", "Net", "Other refs on net", "Status"], rows))
    W("")

    # 3. Rails
    W("## 3. Power rails\n")
    rows = []
    for net in sorted(n for n in nets if re.search(r"(^|/)\+", n)):
        caps = caps_to_gnd(nets, pin_net, net)
        rows.append([f"`{net}`", len(nets[net]), len(caps), ", ".join(caps) or "-"])
    W(md_table(["Rail", "Pins", "Caps to GND", "Caps"], rows))
    W("")

    # 4. Betaflight manufacturer guideline checks
    W("## 4. Checks\n")
    adc = {g: wired[g] for g in (26, 27, 28, 29) if g in wired}
    for g, net in adc.items():
        if "ADC" in doc.get(g, "") and not caps_to_gnd(nets, pin_net, net):
            findings.append(("HIGH", f"ADC input GPIO{g} `{net}` has no capacitor to GND"))

    def cs_net(func_word):
        for g, f in doc.items():
            if func_word in f and "CS" in f:
                names = re.search(r"SPI\d ([A-Z/]+)", f)
                if names and g in wired:
                    order = names.group(1).split("/")
                    first = min(k for k, v in doc.items() if v == f)
                    if order[g - first] == "CS":
                        return g, wired[g]
        return None, None

    for what in ("IMU", "microSD"):
        g, net = cs_net(what)
        if net is None:
            findings.append(("MED", f"no {what} CS found from the AGENTS.md GPIO map"))
        elif not pullup_33(nets, pin_net, net):
            findings.append(("HIGH", f"{what} CS GPIO{g} `{net}` has no pull-up to 3.3 V"))

    for g, f in doc.items():
        if "I2C" in f and g in wired and not pullup_33(nets, pin_net, wired[g]):
            findings.append(("MED", f"I2C GPIO{g} `{wired[g]}` has no pull-up to 3.3 V"))

    run = [n for p, n in pin_net[mcu].items()
           if any(r == mcu and pp == p and f.upper().startswith("RUN") for r, pp, f in nets[n])]
    if not run or not (RAIL_33.search(run[0]) or pullup_33(nets, pin_net, run[0])):
        findings.append(("HIGH", "RUN is neither tied to nor pulled up to 3.3 V"))

    led_g = next((g for g, f in doc.items() if "Status LED" in f), None)
    if led_g is None or led_g not in wired:
        findings.append(("MED", "no status LED GPIO in AGENTS.md or not wired"))
    else:
        leds, seen, frontier = set(), set(), [wired[led_g]]
        while frontier:  # follow series resistors from the GPIO to the LED
            net = frontier.pop()
            seen.add(net)
            for r, _, _ in nets.get(net, []):
                if r.startswith(("D", "LED")):
                    leds.add(r)
                elif r.startswith("R"):
                    partner = two_pin_partner(pin_net, r, net)
                    if partner and partner not in seen and partner != "GND" and not partner.startswith("+"):
                        frontier.append(partner)
        leds = sorted(leds)
        blue = [r for r in leds if re.search(r"blue|blu", parts[r]["value"] + parts[r]["mpn"], re.I)]
        W(f"Status LED on GPIO{led_g}: {', '.join(f'{r} ({parts[r]['value']})' for r in leds) or 'none'}.\n")
        if not blue:
            findings.append(("MED", f"status LED on GPIO{led_g} is not marked blue in its value or MPN"))

    W(md_table(["Severity", "Finding"], findings) if findings else "All checks pass.")
    W("")

    OUT.write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUT.relative_to(REPO)}: {len(findings)} finding(s)")
    for sev, msg in findings:
        print(f"  {sev}: {msg}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
