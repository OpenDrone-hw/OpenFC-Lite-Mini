# Composite video sync separator options for a 20x20 mm RP2350 FPV flight controller (3.3 V, PIO sync read)

Scope: why the current circuit fails with two cameras, what dedicated and discrete separators exist at 3.3 V, what the Betaflight FB_OSD firmware needs from the sync pin, and two concrete fixes (minimal rev/bodge, robust IC). Datasheet numbers below were read from the PDFs on 2026-10-25 (pdftotext of the TI/Renesas/Diodes/andesource files). Items marked "my calc" or "my estimate" are NOT sourced and must be verified in SPICE or on the bench.

## Q1. Discrete options and why the current circuit fails

### Takeaway
The current circuit puts the comparator threshold (IN- = 0 V) at a distance of one Schottky Vf above the clamped sync tip, not at a fixed ~70 mV above it as every dedicated separator does. With Vf larger than half the sync amplitude (low-sync camera, or camera + 75R double termination) the blanking level never rises above 0 V and the output sticks low. The fix is to clamp the tip to a small positive bias and place the threshold a fixed ~70 mV above the tip, ideally tracking the clamp diode with a second matched diode.

### Cited Findings
- Reference behaviour (LM1881): input is AC coupled, sync tips are clamped to 1.5 V DC at pin 2, and a comparator threshold "set just above this voltage" strips the sync; the separation is nominally 70 mV (55 min, 85 max), independent of signal amplitude. At 0.5 Vpp input that is near the middle of the sync pulse, at 2 Vpp it is 11 % of sync. Input clamp charge current 0.8 mA, discharge current 11 uA typ (6 to 16). Input range 0.5 to 2 Vpp., [TI LM1881 datasheet](https://www.ti.com/lit/ds/symlink/lm1881.pdf) (sections 6.4 and 7.3.1)
- Same TI datasheet recommends, for low-impedance (75 ohm) sources, a 620 ohm series resistor plus 510 pF to ground (corner 500 kHz, about 18 dB attenuation of subcarrier, adds 40 to 200 ns delay). The current 680 ohm + 470 pF is the same filter (fc = 1/(2 pi 680 470p) = 498 kHz, my calc). Filter is not the problem., [TI LM1881 datasheet](https://www.ti.com/lit/ds/symlink/lm1881.pdf)
- LMH1980 uses the same principle: fixed slice 70 mV above a sync-tip clamp at 0.7 V, "allows for proper sync separation even for improperly terminated or attenuated input signals"; sync amplitude spec 0.14 V min, 0.30 typ, 0.60 max; DC bounce between two consecutive sync tips must be below 25 mVpp or outputs may be wrong. Handles "non-terminated or double-terminated input conditions" assuming 1 Vpp normally terminated., [TI LMH1980 datasheet](https://www.ti.com/lit/ds/symlink/lmh1980.pdf)
- EL1881: fixed 70 mV sync-tip slicing for 0.5 to 2 Vpp input (sync tip amplitude 143 to 572 mV), 55/70/85 mV slice spec., [Renesas EL1881 datasheet](https://www.renesas.com/en/document/dst/el1881-datasheet)
- Diode used today: Diodes Inc SDM02U30LP3Q (X3-DFN, 30 V, 100 mA), VF max 0.37 V at IF = 10 mA, 0.20 V typ at 10 mA and 125 C. No low-current Vf given in the datasheet (only curve). Note the datasheet read is the LP3Q variant, confirm it is the fitted part., [Diodes SDM02U30LP3Q](https://www.diodes.com/assets/Datasheets/SDM02U30LP3Q.pdf)
- TLV7031: VIO +-8 mV max, hysteresis 2 / 7 / 17 mV (min/typ/max, 25 C), common-mode range VEE to VCC+0.1 V, IB 2 pA, tPHL = tPLH = 3 us typ at 100 mV overdrive, 15 pF, 5 V. Pinouts: DCK/DBV "North West" (OUT 1, VEE 2, IN+ 3, IN- 4, VCC 5) and "South East" (IN+ 1, VEE 2, IN- 3, OUT 4, VCC 5) variants exist., [TI TLV7031 datasheet](https://www.ti.com/lit/ds/symlink/tlv7031.pdf) (5.7, 5.8)
- Sync-slicing principle in patents: clamp tip, then slice at about 50 % between tip and blanking, or negative peak detector into a comparator; sample/hold variants sample back porch/burst for the reference., [US7782397](https://patents.google.com/patent/US7782397), [US7215379](https://patents.google.com/patent/US7215379), [US4185299](https://patents.justia.com/patent/4185299)
- Nominal levels: 1 Vpp composite with 0.3 V sync, 0 to 0.7 V video, 75 ohm termination required., [piclist post](https://pic.hallikainen.org/piclist/2001/a/01/27/031715a.txt) (secondary source). Source+load both 75 ohm gives half amplitude, so double termination halves sync (about 143 mV from 286 mV)., [edaboard thread](https://www.edaboard.com/threads/camera-switching.416766/?amp=1) (forum, secondary)

### Inferences (my calc, unverified on hardware)
- Current circuit: tip = -Vf(I), blanking = -Vf + Vsync, threshold = 0 V. Works only if 0 < Vsync - Vf with margin. Vf of this class of Schottky at tens of uA is plausibly 0.10 to 0.25 V (my estimate, no datasheet number). Vsync is 286 to 300 mV (1 Vpp, terminated), about 143 mV (double terminated), 570 mV (unterminated source into our 75R is 1 Vpp, but a camera with a 75R internal source and no load sees 2 Vpp). With 143 mV sync and Vf of 0.1 to 0.25 V, blanking sits at about +0.04 V down to -0.11 V: threshold falls at or beyond blanking, the comparator output sticks low or chatters. This matches "fails with two cameras" (likely low-sync or double-terminated ones) but the cameras' actual sync amplitude has NOT been measured. First bench action: scope the IN+ node on the two failing cameras.
- Second issue: IN+ swings to -Vf (below VEE) but the TLV7031 spec only guarantees VCM >= VEE. Out of range operation, ESD diode conduction possible. Clamping the tip to a positive bias removes this.
- Third risk: TLV7031 is a 315 nA micropower part with 3 us typ delay (at 100 mV overdrive; lower overdrive will be slower, general comparator behaviour). Sync pulse is 4.7 us, the firmware classifies pulses by width (see Q3). Delay is symmetric nominally but overdrive-dependent delay changes pulse width. Betaflight contributor advice is a comparator of 50 ns or less (Q3). Replace with a fast part (Q4).
- Time constants vs 15.6 kHz / 64 us line: coupling cap 1 uF with bleed resistor Rb: tilt per line is dV = Vavg * 64us / (Rb*C); with Rb = 1 Mohm, C = 1 uF, tau = 1 s, tilt per line about 0.04 % (negligible). Recovery after a content or hot-plug change is on the order of tau (0.5 to 1 s) which is acceptable for FPV. Vertical serrations/broad pulses (about 27 us low in 32 us) pull the average down for a few lines; bleed current into the tip diode makes a clamp that recovers within lines. Tilt over a field (20 ms) with tau = 1 s is about 2 % of a few hundred mV, small. LMH1980 limit: tip DC bounce must stay below 25 mVpp between tips.
- LM1881 clamp: 0.8 mA charge versus 11 uA discharge, i.e. a 70:1 asymmetry; a discrete clamp should likewise charge fast (diode) and leak slowly (Rb), the ratio sets the sensitivity to chroma/noise below the sync tip.

### Gaps
- No datasheet number for SDM02U30 Vf at 1 to 100 uA (curve not extracted). Measure.
- No measured sync amplitudes for the two failing cameras.
- No TI TLV3501/TLV7031/LMV7219 application note on video sync separation found in searches; only principle sources above. The "transistor sync separator" search returned patents only, no usable component values (e.g. [KR200162111Y1](https://patents.google.com/patent/KR200162111Y1/en), [US3629501A](https://patents.google.com/patent/US3629501A/enExample)), so a discrete BJT separator is not recommended or characterised here.
- EEVblog thread on sync separation not found. A mikrocontroller.net thread "MAX7456 Sync Problem" exists ([link](https://www.mikrocontroller.net/topic/569863)) but returned HTTP 403, content not read.

## Q2. Dedicated sync separators and OSD-chip reference specs

### Takeaway
Only one dedicated separator found that natively runs from 3.3 V with a 140 mV sync minimum: TI LMH1980 (VSSOP-10, 3.3 to 5 V, 10.5 mA at 3.3 V, about 5 to 7 USD on LCSC, JLC basic/extended status unconfirmed). LM1881/EL1881 are 5 V parts (SOIC-8) and cheap but need a level shifter for the GPIO. The OSD ICs (MAX7456/AT7456E) specify 0.5 to 2.0 Vp-p for sync detection, i.e. even they assume at least 0.5 Vpp composite (about 143 mV sync).

### Cited Findings
| Part | Supply | Min input | Slice | Package | Current | LCSC |
|---|---|---|---|---|---|---|
| LMH1980 | 3.3 V -10 % to 5 V +10 % | sync 0.14 V (0.5 to 2 Vpp video), amplitude 140 mV to VCC - 0.7 V | 70 mV above 0.7 V clamp | VSSOP-10 (DGS, 3x3 mm, 0.5 mm pitch) | 10.5 mA typ / 12.5 max at 3.3 V | C189203 (LMH1980MM/NOPB), 906 in stock, 6.88 USD at 1, 5.36 at 100+ |
| LM1881 (TI) | 5 to 12 V (abs max 13.2 V) | 0.5 to 2 Vpp (max 3 Vpp at 5 V) | 70 mV (55 to 85) | SOIC-8 | 5.2 mA typ, 10 max at 5 V | C9412 TI (reference 3.04 USD at 1); C5122511 Slkor clone, 2,302 in stock, 0.67 USD at 1 |
| EL1881 (Renesas) | single +5 V | 0.5 to 2 Vpp | 70 mV | PDIP/SOIC-8 | 1.5 mA typ | not checked |
| MAX7456 / AT7456E | AVDD/DVDD 3.15 to 5.25 V | sync detection 0.5 to 2.0 Vp-p, operating 0.5 to 1.2 Vp-p | internal, not published | QFN | n/a | n/a |

- LMH1980 table values, [TI LMH1980 datasheet](https://www.ti.com/lit/ds/symlink/lmh1980.pdf) (operating ratings, electrical table, pin 8 CSOUT, note 8: "Outputs are negative-polarity logic signals"). VOH min 3.0 V at VCC = 3.3 V, VOL max 0.3 V. Recommends 75R termination, optional input RC filter with R9 about 100 ohm and C2 varied.
- LMH1980 stock/price, [LCSC C189203](https://www.lcsc.com/product-image/C189203.html). A second LCSC mirror page showed 0 stock (conflicting snapshots), see [fat.lcsc.com page](https://fat.lcsc.com/product-detail/image/LMH1980MM-NOPB_C189203.html). JLCPCB basic/extended status not shown on either; no JLCPCB part page found.
- LM1881 5 to 12 V, SOIC-8, input max level 3 Vpp at 5 V, [TI LM1881](https://www.ti.com/lit/ds/symlink/lm1881.pdf), [LCSC C9412](https://www.lcsc.com/pt/product-detail/C9412.html), [LCSC C5122511](https://fat.lcsc.com/product-image/C5122511.html)
- EL1881 +5 V only, 1.5 mA, plug-in compatible with LM1881, [Renesas EL1881](https://www.renesas.com/en/document/dst/el1881-datasheet) (pin 8 "VDD 5V")
- AT7456E (Chinese-language datasheet copy): input operating range 0.5 to 1.2 Vp-p, sync detection range 0.5 to 2.0 Vp-p, output sync tip level 0.7 V, AVDD/DVDD 3.15 to 5.25 V, specs at 5 V, video clamp settling 32 lines., [AT7456E datasheet copy](https://file01.andesource.com/dkpdf/AT7456E_001.pdf). MAX7456 numbers identical per [Maxim CN datasheet](https://www-cce.cldnet.analog.com/media/cn/technical-documentation/data-sheets/MAX7456_cn.pdf) (snippet only; English PDF could not be fetched).
- Others seen but not usable: EL4511 (3.3/5 V but QSOP-24), LMH1981 (TSSOP-14, 5 V), ISL59885 (supply not confirmed), [element14 listing](https://tw.element14.com/en-TW/c/semiconductors-ics/video-processing/video-synch-separators/prl/results). Search found no SOT-23/SC-70 class video sync separator.

### Inferences
- LMH1980 is the only fit for "3.3 V, dedicated, tolerant of low and double-terminated sync". 10.5 mA from the 3.3 V rail (35 mW) is notable but acceptable on an FPV FC with a 5 V rail; it can also run from 5 V, but then CSOUT swings to about 4.5 V and needs dividing for the RP2350 GPIO (not verified whether the pin is 5 V tolerant; do not rely on it).
- 140 mV min sync means cameras below that are out of spec for any commercial separator; with a fixed 70 mV slice a pulse of about 100 mV may still work (my estimate, untested).
- The OSD chips' 0.5 Vpp minimum means "normal" FPV OSD boards already depend on cameras with at least about 143 mV sync; the failing cameras may be below this or double-terminated. Measure first.
- LM1881 via 5 V rail is the cheap alternative (0.67 USD, SOIC-8 is large for a 20x20 board), but its 5 V supply and 4.5 V output require a divider and its min amplitude is 0.5 Vpp.

### Gaps
- JLCPCB basic vs extended classification for LMH1980, LM1881, EL1881: not determinable from search results. Check jlcpcb.com/parts.
- LMH1980 CSOUT delay/skew numbers not extracted (relevant to OSD pixel alignment).
- MAX7456 English datasheet unreachable (connection refused); AT7456E figures come from a Chinese copy.

## Q3. What do existing open-source FC / OSD designs use

### Takeaway
Nothing public documents a working discrete sync circuit with values. Betaflight's RP2350 FB_OSD firmware only requires an active-low sync on a GPIO and does width-based line counting; the only hardware hints are a "fast comparator, input extends 100 mV below GND" comment and a TBS config note.

### Cited Findings
- Firmware requirement (from a prior note, read from betaflight master d593400 on 2026-10-25): sync must be ACTIVE-LOW (sync tip = low), detection classifies low pulses: under 3.9 us ignored (equalizing 2.35 us), 3.9 to 6.6 us counted as HSYNC (nominal 4.7 us), over 6.6 us is a vsync/long pulse; needs PAL 304 to 306 or NTSC 252 to 255 hsyncs per field for 16 consecutive fields or nothing happens. PIO runs at 75 MHz., see local note `betaflight_fbosd_reference.md` in this folder; source [osd_tx.pio](https://github.com/betaflight/betaflight/blob/d593400a05a5e142c0f6f83cc45c237ef078c634/src/platform/PICO/osd/osd_tx.pio)
- Betaflight PR #14882 comment by Jaseatthepi (2026-03-03): "The comparator should be selected for a low propagation time, suggest 50ns or less to avoid shimmering. Also the input should extends 100mV or so below GND to avoid the need for additional biasing circuitry.", [PR #14882](https://github.com/betaflight/betaflight/pull/14882). The question about hysteresis/schematic in the same thread was not answered.
- TBS Lucid RPi FC config: "Discrete analogue OSD (74LVC1G3157 mux + TLV3231/TLV3541) instead of MAX7456", OSD pins wired but inactive in firmware; no values published., [config.h](https://github.com/betaflight/config/blob/master/configs/TEBS/TBS_LUCID_RPI_FC/config.h). Note: TLV3541 is an op-amp, not a comparator ([TLV3541 per search result](https://www.ti.com/cn/lit/gpn/tlv3541)); TLV3231 is a 5 V push-pull comparator with about 15 ns (50 mV overdrive) to about 22 ns (10 mV) typ delay, [TI TLV3231/3232 datasheet](https://www.ti.com/document-viewer/TLV3232/datasheet/GUID-ECDE21F6-7868-4630-AEB2-43D32CFB06C9) (via search summary; its minimum supply was not read, check before use at 3.3 V).
- LM1881 is the usual choice for MCU video overlay hobby projects, e.g. overlay64 (AVR) uses an LM1881 to detect HSYNC/VSYNC, [github.com/sgw32/overlay64](https://github.com/sgw32/overlay64)
- RP2040 composite generators (rp_cvideo, PAL overclock) generate video but do not separate sync from an input, [rp_cvideo](https://docs.rs/rp-cvideo), [Hackster PAL RP2040](https://hackster.io/news/a-heavy-overclock-pushes-pal-standard-video-from-a-raspberry-pi-rp2040-s-pio-blocks-ce895afd0d48)

### Inferences
- Because the firmware ignores pulses under 3.9 us and classifies 3.9 to 6.6 us as HSYNC, the separator must not distort widths by more than about 1 us and must reject equalizing pulses and chroma glitches. A slice near the sync tip (70 mV) with an RC chroma filter is compatible; a slice at the tip's very top would shorten pulses.
- Jaseatthepi's "extends 100 mV below GND" implies a comparator with a negative-going common-mode range and the signal clamped around ground, similar to our diode-to-GND clamp. Our TLV7031 does not specify operation below VEE, so this hint does not transfer to our part.

### Gaps
- No public schematic for Hellbender, RASPBERRY_PI_UAVFC or Lucid. No STM32/minimOSD/BlueOSD schematic with sync-slicing values found. Search for those names returned nothing relevant (only patents and generic notes).

## Q4. Recommendations for the rev change and bodge test

### Takeaway
(a) Keep the footprints, move the clamp anode to a +0.4 V bias, add a 1 Mohm bleed, and feed IN- from a matched second diode so the threshold sits about 60 to 70 mV above the tip regardless of Vf. Swap TLV7031 for a fast push-pull comparator. (b) Robust: LMH1980 (VSSOP-10) with 100 ohm + C filter, CSOUT direct to the GPIO. All component values below are my calc and need SPICE plus a scope check.

### Cited Findings (parts)
- TLV3201: 40 ns, microPower, push-pull, 2.7 to 5.5 V, VIO 1 mV typ / 5 mV max (25 C), SC70-5 (DCK) and SOT-23-5 (DBV); LCSC listing not found., [TI TLV3201](https://www.ti.com/product/TLV3201), [datasheet](https://ti.com/document-viewer/TLV3202/datasheet/GUID-8E3C36D8-37C4-45DF-AD7E-EC57D300A442)
- LMV7219: 7 ns typ at 5 V (DigiKey max 20 ns), 2.7 to 5 V, push-pull rail-to-rail, SC70 and SOT-23-5, 1.1 mA; some variants NRND; LCSC listing not found., [TI LMV7219](https://www.ti.com/document-viewer/LMV7219/datasheet)
- TLV7031 (current): see Q1; slow (3 us).
- LMH1980: see Q2 table.

### Option (a): minimal change on existing footprints (my design calc)
```
 camera -> 75R to GND (term) -> 680R -> +--- 1uF ---+--------------+---> IN+ (comparator)
                                        |           |              |
                                       470pF       D1 (Schottky)   Rb 1M to +3.3 V
                                        |           anode at Vb
                                       GND          (cathode to signal node)

 3.3V --8.2k--+-- Vb (~0.42 V, Zout ~1k) --+-- D1 anode
              |                            +-- D2 anode (same part as D1)
             1.2k                                   D2 cathode --> IN- node --Rr (68k)--> GND
              |                                                    (optional 1 nF to GND on IN-)
             GND
```
- Tip level = Vb - Vf1(Ipk). IN- = Vb - Vf2(I2). With Ipk/I2 = r, IN- sits above the tip by about 27 mV * ln(r) (n about 1.05, 25 C, my calc): r = 5 gives 44 mV, r = 10 gives 62 mV, r = 20 gives 81 mV. The threshold therefore tracks diode Vf spread and temperature, and the log makes r tolerant.
- Estimating Ipk: line duty of sync is about 7.3 % (4.7/64 us). Average Rb current with Rb = 1 Mohm and signal average about 0.7 V is about (3.3 - 0.7)/1M = 2.6 uA, so tip diode pulse current about 36 uA; choose I2 about 3.6 uA, Rr about (Vb - Vf2)/I2 about 70 k (use 68k). Picture-content changes average level, moving r by roughly 2x, i.e. about +-19 mV threshold change (my calc). Verify with SPICE using the real SDM02U30 model.
- Error budget for a 143 mV sync pulse (slice at 62 mV above the tip, 81 mV to blanking): comparator offset 8 mV max + half hysteresis up to 8.5 mV + diode mismatch (assume 10 mV) + content effect 19 mV = about 46 mV worst case, which uses most of the margin; for 286 mV sync margin is large. Below about 120 mV sync it will fail (as would LMH1980 below 140 mV spec).
- Level check: tip at about Vb - Vf = 0.42 - 0.2 = about +0.2 V (estimate), inside the comparator common-mode range (VEE to VCC+0.1 for TLV7031); blanking up to +0.2 V + 0.6 V for unterminated cameras.
- Comparator: swap to TLV3201 or LMV7219 in SC70-5/SOT-23-5. Check pinout against the TLV7031 footprint before assuming drop-in (TLV7031 has two pinout options, see Q1); if the output polarity needs to stay "high during video, low during sync", signal on IN+ and threshold on IN- keeps it. Add no extra hysteresis beyond the part's own at first; if chatter appears at the threshold, add 5 to 10 mV positive feedback (e.g. 1M from OUT to IN+ gives about 3.3 V * (Z/1M); size with the 1 k to 10 k source Z of IN+, my estimate: needs care because IN+ is the high-impedance AC node).
- Hardware cost: two resistors for Vb, Rb, Rr, one extra Schottky, same cap and filter.

### Bodge test on an existing board (order of operations)
1. Scope IN+ (AC, 100 mV/div, 5 us/div) on a working and a failing camera, with camera connected normally. Record sync amplitude, tip DC level, blanking level, and the comparator output. This confirms or refutes the hypothesis above before any rework. If sync < 150 mV or tip is at about -0.2 V with blanking about 0 V, the hypothesis holds.
2. Lift the SDM02U30 anode from GND and wire it to a divider from 3.3 V (for example 8.2k to 3.3 V and 1.2k to GND) to get Vb about 0.4 V. Add 1 Mohm from the signal node (cathode side) to 3.3 V.
3. Lift IN- (pin 4 for the North-West DCK/DBV pinout, pin 3 for South-East; check which TLV7031 is fitted) and connect it to a trimmer or divider from 3.3 V so that it can be set between tip and blanking; start at Vtip + 70 mV (about 0.25 to 0.3 V). A 100k trimmer between 3.3 V and a 4.7k to GND lets you sweep roughly 0 to 0.15 V, so pick the divider to cover 0.1 to 0.5 V: for example 3.3 V - 6.8k - IN- - 1k - GND gives 0.42 V, with a 1k trimmer in series with the lower leg for tuning (my estimate, adjust after step 1).
4. Observe the output with the scope: low during sync, high otherwise, pulse width about 4.7 us, no spikes at chroma, and equalizing pulses 2.3 us present. If the 3 us TLV7031 delay distorts, fit a TLV3201/LMV7219 in place.

### Option (b): robust
- U: LMH1980MM/NOPB (LCSC C189203, VSSOP-10 3x3 mm, 3.3 V, 10.5 mA typ).
- Input: camera -> 75R termination -> R9 100 ohm -> 0.1 uF (or 1 uF) coupling -> VIN, with C2 to GND chosen for a cutoff of about 500 kHz (for R9 = 100 ohm, C2 about 3.3 nF; my calc, the datasheet suggests keeping R9 small and varying C2). Use the datasheet application circuit (REXT = 10 kohm 1 %, bypass caps).
- Output: CSOUT (pin 8, negative-polarity composite sync) directly to the GPIO that was fed by the comparator. This already matches the firmware's active-low requirement. No external threshold tuning. Handles sync 0.14 to 0.6 V and double termination per datasheet.
- Cost/space: about 5 to 7 USD at LCSC, VSSOP-10 plus 6 passives, 35 mW. The extra board area is about 3x5 mm.
- Alternative cheaper: Slkor LM1881 (C5122511, SOIC-8, 5 V rail) with a 5 V-to-3.3 V resistor divider on CSOUT (outputs 4.0 V min at 5 V per datasheet), about 0.67 USD, but SOIC-8 and 5 V only. Use RSET 680 k per datasheet; min input 0.5 Vpp, so it will not tolerate low sync better than the current circuit unless the cameras exceed that.

### Inferences
- If the two failing cameras are low-sync or doubly terminated, (b) is the only option that is specified for it; (a) with matched-diode threshold should reach a similar level of robustness but only with your own validation.
- Recommend doing the scope step first (cheap, decisive), then bodge (a) on one board, with (b) in the rev only if (a) leaves any camera failing.

### Gaps
- JLCPCB basic/extended status for LMH1980, TLV3201, LMV7219, SDM02U30: not confirmed. Stock for TLV3201/LMV7219/TLV3231 at LCSC not found.
- TLV3231 supply minimum (3.3 V operation) not read.
- None of the component values in option (a) have been simulated or measured; the Vf of the fitted diode at 5 to 40 uA is unknown.
- No test data from the two failing cameras (sync amplitude, source impedance, termination).
