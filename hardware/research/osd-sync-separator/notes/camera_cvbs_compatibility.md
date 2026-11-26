# Analog FPV camera CVBS variation vs a discrete diode-clamp + 0 V comparator sync separator

Circuit under analysis: 75R termination, 680R + 470pF lowpass, 1uF AC coupling, Schottky clamp (SDM02U30, cathode to signal, anode to GND), TLV7031 (3.3 V) with inverting input at GND (0 V threshold).
Convention: "measured/datasheet" = number read from a primary document. "Anecdote" = forum post. "Inference" = my arithmetic or reasoning, not sourced.

## 1. What CVBS levels do FPV cameras output and how much do they vary?

### Takeaway
The standard gives sync of 286 mV (NTSC) or 300 mV (PAL) below blanking at 1 Vpp into 75R. FPV camera listings only claim "1.0 Vp-p, 75R"; I found no measured sync amplitudes for real FPV cameras. The only quantified source of variation I could document is load/termination (double termination cuts amplitude) plus a SPRacing statement that old gear and some cameras use negative or drifting sync levels. AC coupling makes camera DC offset irrelevant to this circuit.

### Cited Findings
- NTSC-M: sync -40 IRE = -285.7 mV, blanking 0 mV, peak white +714.3 mV; PAL-B/G: sync -43 IRE = -300 mV, peak white +700 mV. NTSC-M black is at 7.5 IRE setup, NTSC-J and PAL have none. (The page's table says +51.43 mV for setup, its text says 53.57 mV; irrelevant for sync.) ; source: [Wikipedia IRE (unit)](https://en.wikipedia.org/wiki/IRE_(unit))
- Composite video is specified as 1 Vpp terminated into 75 ohm. ; source: secondary summary of BT.470/BT.1700 via search of [Wikipedia IRE](https://en.wikipedia.org/wiki/IRE_(unit)); I did not read SMPTE 170M or ITU-R BT.470 themselves.
- Camera listings state "Video Output 1.0Vp-P 75 ohm" (1000TVL CMOS camera) and similar for other generic cameras. Seller specs, not measurements. ; source: [Robu 1000TVL CMOS listing](https://st.robu.in/?p=45649), [Readytosky 1000TVL](https://zbotic.in/product/readytosky-1000tvl-90-degree-coms-camera/)
- Cameras commonly select PAL/NTSC by a body switch or long press; one listing warns to power off before switching or "it may be failed". ; source: same Robu listing above and [LST-S2 AIO listing](https://thinkrobotics.com/collections/drone-cameras-online/products/lst-s2-fpv-aio-camera-with-transmitter-osd-online)
- SPRacing PixelOSD README: "Some cameras output negative sync pulse voltages." "The sync pulse voltage can change over time, e.g. as a camera warms up." "However, most modern cameras output a 0-0.3 volt stable sync-voltage." "Be aware that older video equipment uses a ~ -0.3v sync voltage, and 0v black level." Its filter does "2x + 150mv DC offset" boost; without negative-voltage handling the design is limited to cameras with sync >= 0 V. ; source: [github.com/spracing/spracingpixelosd](https://github.com/spracing/spracingpixelosd) (fetched summary, wording as returned by the fetch tool)
- Double termination: a 2018 IntoFPV reply says "The video signal expects a 75 Ohm impedance and adding two 75 Ohm loads to the signal in parallel will result in an impedance mismatch", "It all depends on the camera and the two loads as to how well this will be tolerated." Another reply: "might have no effect whatsoever" and "(Two impedances in parallel will halve the total impedance rather than add to it.)". Anecdote. ; source: [IntoFPV thread 5134](https://intofpv.com/archive/index.php/thread-5134.html)
- German forum anecdote: washed-out colours improved after adding a 75R from signal to GND at the VTX input (i.e. some VTX inputs are not terminated; cameras drive 75R source impedance). Not read in full (page returned 403 to my fetch; this comes from a search-result summary). ; source: [drohnen-forum.de](https://www.drohnen-forum.de/index.php/Thread/13976-FPV-Kamera-Abschlu%C3%9Fwiderstand/)
- A Creative Cow thread (2005) states that doubly terminating a video line roughly halves amplitude; from search snippet only, not fetched. ; source: [creativecow.net](https://creativecow.net/forums/thread/question-on-video-impedence/)
- Reference chip requirement: AT7456E (MAX7456 clone) "Input-Voltage Operating Range 0.5 to 1.2 Vp-p", "Input-Voltage Sync Detection Range 0.5 to 2.0 Vp-p", input AC-coupled with 0.1 uF and internally clamped, sync tip clamped to about 560 mV, LOS asserted after 32 consecutive lines without sync. (Chinese datasheet text: "将 VIN 的同步头钳位在约 560mV".) So commercial OSD chips themselves guarantee sync only for composite >= 0.5 Vpp, i.e. sync >= roughly 143 mV. ; source: [AT7456E datasheet, file01.andesource.com](https://file01.andesource.com/dkpdf/AT7456E_001.pdf)

### Inferences
- Double termination arithmetic (my calculation): a camera with 75R source impedance driving its rated 75R load gives 1 Vpp, i.e. open-circuit 2 Vpp. Two 75R loads in parallel (37.5R) give 2 * 37.5/112.5 = 0.667 Vpp, so sync = 191 mV (NTSC) or 200 mV (PAL). A camera that is already weak (e.g. 0.7 Vpp rated) would give about 0.47 Vpp and sync near 130 mV. If the FC termination is in parallel with a VTX termination, this is the likeliest amplitude loss.
- Cameras with a DC-coupled output or with different DC bias are not a problem here: the 1uF removes DC. The clamp re-references the sync tip.
- A camera with output impedance far above 75R or with a series cap into an unterminated input would behave differently; no source found quantifying this for FPV cameras.

### Gaps
- No measured sync amplitude (scope data) for Eachine, Caddx, Foxeer, RunCam cameras found. Only seller specs.
- No camera datasheet I found states sync amplitude or DC level separately from "1.0 Vp-p".
- SMPTE 170M and ITU-R BT.470 primary text not read (paywalled).
- The "older Eachine" camera is not identified by model, so nothing model-specific can be said.

## 2. Diode clamp + 0 V comparator behaviour: where does the sync tip sit, what margin exists

### Takeaway
With a Schottky clamp at nA-uA currents the sync tip sits roughly 50 to 150 mV below GND (my estimate), so blanking sits only (sync amplitude minus that) above the 0 V threshold. Margin to blanking is about 140 to 240 mV at nominal 286 mV sync but falls to roughly 40 to 140 mV at 191 mV sync and to zero near sync = 100 to 160 mV. The design has no safety margin for weak cameras. The TLV7031 itself is not the problem: offset (up to 8 mV) and hysteresis (up to 17 mV) are small versus this, but the non-inverting input swings below VEE, outside its specified common-mode range.

### Cited Findings
- TLV7031 (TLV703x/704x family, SLVSE13J, Nov 2024): input offset VIO typ +/-0.1 mV, max +/-8 mV (VS 1.8 V and 5 V, VCM = VS/2); hysteresis VHYS min 2, typ 7, max 17 mV (TA = 25 C, "Single" table; dual/quad tables show 3/10/25 mV); common-mode range "VEE to VCC + 0.1 V"; input bias 2 pA typ; CMRR 73 dB for VEE < VCM < VCC; propagation delay 3 us typ at 100 mV overdrive. ; source: [TI TLV7031 datasheet](https://www.ti.com/lit/ds/symlink/tlv7031.pdf) (Sections 5.7, 5.3, 5.1)
- Recommended input voltage range "VEE - 0.1 to VCC + 0.1 V" (Section 5.3). Absolute maximum for input pins "VEE - 0.3 to 7 V"; note: "Input terminals are diode-clamped to VEE. Input signals that can swing 0.3V below VEE must be current-limited to 10mA or less". ; source: same datasheet, 5.1 and 5.3
- Section 6.4.1: "The input common-mode extends from VEE to 100mV above VCC... No phase inversion of the comparator output occurs when the input pins exceed VCC and VEE." "The comparator inputs are protected from voltages below VEE by internal diodes connected to VEE. As the input voltage goes under VEE, the protection diodes become forward biased and begin to conduct causing the input bias current to increase exponentially." ; source: same datasheet
- Datasheet offset and hysteresis are specified only at VCM = VS/2 (and in plots vs VCM); no offset/CMRR is guaranteed for VCM < VEE. ; source: same datasheet (Section 5.7 test conditions)
- SDM02U30 family (checked the LP3Q automotive "advance information" datasheet, DS42738 Rev 1-2, X3-DFN0603-2): VF max 0.37 V at IF = 10 mA; a typ 0.20 V entry at IF = 10 mA, TA = +125 C; IR max 7 uA at VR = 10 V and 4 uA at VR = 30 V; VRRM 30 V. No VF number below 10 mA is tabulated; the VF vs IF curve exists as a graph that I could not read from the extracted text. ; source: [Diodes SDM02U30LP3Q datasheet](https://www.diodes.com/assets/Datasheets/SDM02U30LP3Q.pdf). Caveat: the user's non-Q SDM02U30 variant datasheet was not checked.
- Reference clamp level in a commercial OSD chip: AT7456E clamps sync tip to about 560 mV internally, i.e. it works with a clamp reference well above the threshold, not at a diode drop around 0 V. ; source: [AT7456E datasheet](https://file01.andesource.com/dkpdf/AT7456E_001.pdf)
- Hobby RP2040 OSD (Domski): a discrete threshold sync detector "works, but under specific conditions", needs the threshold readjusted when the camera is changed, and fails with an all-black screen or black parts of the picture because the sync level floats; video sync is "not really 0V, but a bit above 0.2V". LM1881 "adjusts the detection level by itself". Fetch-tool summary, wording not verified against the page. ; source: [blog.domski.pl](https://blog.domski.pl/on-screen-display-with-raspberry-pi-pico/)

### Inferences
- Lowpass: R*C = 680R * 470pF = 320 ns, f(-3dB) about 497 kHz. A 4.7 us sync pulse reaches 1-exp(-4.7/0.32) = 99.9 % of its amplitude, so the filter does not eat sync. Chroma burst (3.58 MHz NTSC, 4.43 MHz PAL) is attenuated to about 0.14 / 0.11 of its amplitude: NTSC burst 286 mV pp becomes about 40 mV pp (+/-20 mV).
- Clamp tip estimate (not in any datasheet): at steady state the diode only has to replace leakage/bias charge each line. With a few 100 nA of leakage spread over 64 us lines and a 4.7 us conduction window, peak current is order 1 uA. Using VF = 0.30 to 0.37 V at 10 mA and about 60 mV per decade, VF at 1 uA is about 0.05 to 0.15 V. So tip is about -0.05 to -0.15 V and blanking is at (sync amplitude - Vf).
- Margin table (blanking above 0 V threshold, ignoring offset/hysteresis, then minus about 12 mV worst-case for offset + half hysteresis):

| Sync amplitude at comparator | Source case | Blanking margin at Vf = 0.05 V | at Vf = 0.15 V |
|---|---|---|---|
| 300 mV | PAL, 75R loaded | 250 mV | 150 mV |
| 286 mV | NTSC, 75R loaded | 236 mV | 136 mV |
| 191 mV | NTSC, double terminated (37.5R) | 141 mV | 41 mV |
| 143 mV | 50 % camera (0.5 Vpp) | 93 mV | -7 mV (fail) |
| 100 mV | weak / non-standard | 50 mV | -50 mV (fail) |

  Threshold sits closer to the tip than to blanking, so the output flips late and pulse width shortens. Pulse width error is small compared with the 4.7 us sync, but vsync detection (serrations at half-line rate) is the first thing to fail when the margin is thin, because broad pulses in the vertical interval have very short serration gaps and the 320 ns RC plus 3 us comparator delay plus hysteresis eat that gap (inference, not tested).
- Why hsync can work while vsync fails (inference, untested): the broad vertical pulses and serrations have short gaps, and the 320 ns RC, 3 us comparator delay and hysteresis plus a thin margin eat them first. Lower sync amplitude moves blanking toward the 0 V threshold (unsafe direction); noise spikes that pull the clamp tip more negative move blanking up (safe direction).
- TLV7031 inputs: the non-inverting input is driven to -Vf (about -0.05 to -0.15 V) which is outside the specified common-mode range (VEE) but within the absolute maximum (VEE - 0.3 V) and mostly within the recommended range edge (VEE - 0.1 V). No-phase-inversion is stated, and the inverting input stays at VEE, so the differential on the tip side is correct. The internal ESD diode becomes a second, parallel clamp as the input nears -0.3 V and could set the tip lower than the Schottky at higher currents. Real risk is limited to unspecified offset when VCM < VEE; blanking-side margin is the dominant risk.
- Tip stability (inference): the clamp holds the tip against picture content, unlike the floating discrete detector Domski describes. The tip level depends on diode leakage and temperature (datasheet VF drops to 0.20 V typ at 125 C, 10 mA), so the tip, and therefore the margin, shifts with temperature; direction and size not measured.

### Gaps
- Actual SDM02U30 VF at 100 nA to 10 uA (graph not readable from the extraction); the tip estimate above is derived, not measured. A bench measurement (scope on comparator input, DC-coupled, with a known camera) is the way to close it.
- TLV7031 offset vs VCM for VCM < VEE is not specified; Fig 5-6 to 5-8 (offset vs VCM) only cover VEE to VCC.
- Whether the 3.3 V supply, input protection and hysteresis behave as above for the specific TLV7031 package variant was not checked beyond the family datasheet.

## 3. Known compatibility problems with OSD chips / camera types

### Takeaway
Documented camera/OSD problems in the public record are mostly (a) PAL/NTSC mismatch or Auto detection failing, (b) hardware faults on the FC, (c) power. I found no Betaflight/INAV GitHub issue or forum thread that attributes missing OSD to low camera sync amplitude or a specific camera brand. Absence of evidence only: search coverage was thin.

### Cited Findings
- Recommendations to set PAL or NTSC explicitly because Auto "doesn't always" detect correctly; Auto may recover better after loss of sync (anecdote). ; source: [IntoFPV archive 22325](https://intofpv.com/archive/index.php/thread-22325.html), [IntoFPV archive 9534](https://intofpv.com/archive/index.php/thread-9534.html) (found via search snippets; not individually fetched)
- Oscar Liang: video format options "Auto, PAL, NTSC, or HD"; "Auto if in doubt"; a missing startup logo may mean wrong format, wiring, or "a faulty OSD chip on the FC". A commenter says Auto moved elements, PAL fixed it. ; source: [oscarliang.com/betaflight-osd](https://oscarliang.com/betaflight-osd/)
- Matek F405 CTR user: OSD fine without camera but disappears once camera connected, "as if the camera was overlaying the OSD"; Auto, PAL, NTSC made no difference; replacing the FC did not change it; no resolution reported, camera model not given. Anecdote, unresolved. ; source: [IntoFPV: Only camera feed or OSD, not both](https://intofpv.com/t-only-camera-feed-or-osd-not-both)
- Caddx cameras showed OSD only when camera and FC were both forced to the same PAL/NTSC (search-result summary of several IntoFPV threads; anecdote). ; source: [IntoFPV thread 22082](https://intofpv.com/archive/index.php/thread-22082.html)
- AT7456E needs at least about 3.15 V; 2.4 V was blamed for a dead OSD (anecdote). ; source: [IntoFPV thread 15473-2](https://intofpv.com/archive/index.php/thread-15473-2.html)
- ArduPilot forum: MAX7456 OSD appeared only sometimes, traced to wire noise (anecdote). ; source: [discuss.ardupilot.org](https://discuss.ardupilot.org/t/osd-flight-data-disappear-when-arming/13102)
- Camera-chip cause by design: SPRacing PixelOSD documents that sync voltage differs between cameras (negative, 0 to 0.3 V, drifting when warm) and that "If a camera sync signal is present when also generating sync signals then the sync will be bad". ; source: [github.com/spracing/spracingpixelosd](https://github.com/spracing/spracingpixelosd)

### Inferences
- MAX7456/AT7456E avoid this class of problem because they AC-couple through 0.1 uF into an internal clamp that holds the tip near 560 mV and then slice relative to the tip with a sync separator specified for 0.5 to 2.0 Vpp. The FC circuit here has no such adaptive slicer: its slice level is fixed at 0 V relative to a diode drop, so it is far more amplitude-sensitive than the commercial chip.
- Therefore "works on the old board with camera X, fails with cameras Y and Z" is consistent with amplitude: camera X's sync is large enough or the old board's circuit differed (e.g. MAX7456 or a different slicer), without needing any camera to be out of spec.

### Gaps
- No GitHub issue (Betaflight, INAV, ArduPilot) found that ties OSD loss to a named camera or low sync level.
- Eachine camera-specific reports not found.
- IntoFPV thread contents other than 5134 and the "Only camera feed" thread were read via search summaries only.

## 4. RP2040/RP2350 PIO analog OSD projects and camera sync reports

### Takeaway
Very little public material exists. The one relevant project (Domski, RP2040 + LM1881) reports exactly this failure mode for a discrete threshold detector and fixed it by moving to an LM1881. No RP2350 project reports found.

### Cited Findings
- Domski "On-screen Display with Raspberry Pi Pico": first a discrete sync circuit with a manually set threshold, needing re-adjustment per camera and failing on dark scenes; replaced by LM1881 sync separator whose FRAME output resets the line counter and SYNC output counts lines; missing FRAME makes line count grow, missing SYNC causes line desync/chopped text. Hardware and firmware in separate GitHub repos (not opened). ; source: [blog.domski.pl](https://blog.domski.pl/on-screen-display-with-raspberry-pi-pico/)
- Overlay64 (ATmega, not RP2040) also uses an LM1881; a forum discussion says a microcontroller reading sync as a DC threshold jitters because AC-coupled video floats with content, suggested fix transistor sync separator or LM1881. ; source: search summary of [forums.parallax.com thread](https://forums.parallax.com/discussion/90083/showing-the-video-sync-lm1881-app), [pcbway Overlay64](https://www.pcbway.ru/project/shareproject/Overlay64_SMD_version.html); page content not retrieved
- SPRacing PixelOSD (STM32, not RP2): hardware RC filter + comparator + DAC-generated reference; pulse counting adjusts the DAC ("the comparator voltage is either two high or two low if there are two few or two many incorrect-length pulses"); dynamic sampling of sync voltage was "not found to be necessary" on production boards. Adaptive-threshold approach is therefore the proven solution in a comparator design. ; source: [github.com/spracing/spracingpixelosd](https://github.com/spracing/spracingpixelosd)
- rp_cvideo (Rust crate) generates monochrome composite on RP2040/RP235x with one PIO state machine; output only, no input/sync separation. ; source: [docs.rs/rp-cvideo](https://docs.rs/rp-cvideo)
- Raspberry Pi forum "RP2040 for analogue video effects?" ; source: theoretical discussion that processing must keep up with H/V timing; no camera sync reports. ; source: [forums.raspberrypi.com](https://forums.raspberrypi.com/viewtopic.php?t=334321)

### Inferences
- Fix options seen in the field, in order of cost: (1) LM1881 or similar sync separator IC (adaptive slicing), (2) adaptive threshold via DAC/PWM reference with pulse-width feedback (PixelOSD), (3) add DC bias/gain so threshold sits mid-sync (PixelOSD 2x + 150 mV), (4) for the existing circuit: raise the comparator reference from 0 V to a bias around 50 to 70 mV above the tip, or lower the clamp drop (e.g. use a Schottky biased with a small current), or add gain before the comparator. All of these are my suggestions, not tested.

### Gaps
- No RP2350-specific OSD sync reports found.
- Domski GitHub repos and code were not opened; the exact threshold value and which cameras failed are unknown.
- No Hackaday/Reddit RP2040 OSD thread found despite several queries.

## Method note
~25 searches/fetches. Several forum pages (drohnen-forum.de, edaboard) returned 403; MAX7456 Analog Devices PDF fetch failed, so the AT7456E clone datasheet was used for chip-level numbers (the MAX7456 and AT7456E are pin-compatible clones, but values above are the AT7456E's). Fetch-tool summaries of web pages are paraphrased by an intermediate model; quoted wording may not be verbatim.
