# Betaflight RP2350 FB_OSD: reference hardware and sync expectations

Snapshot: betaflight/betaflight master `d593400a05a5e142c0f6f83cc45c237ef078c634` (read via `gh api` on 2026-10-25), betaflight/config master `4961818c`. All source quotes below are from that commit unless stated. Source dir: https://github.com/betaflight/betaflight/tree/d593400a05a5e142c0f6f83cc45c237ef078c634/src/platform/PICO/osd

## 1. Which PRs introduced/changed FB_OSD, and what do they say about required hardware?

### Takeaway
FB_OSD landed in #14882 (merged 2026), was extended in #15161 and #15749 plus a few related ones. None of the PR descriptions state sync polarity, comparator threshold or levels. The only hardware statements are two PR comments: a pin-order requirement from the author (mjs1441) and a level/comparator hint from Jaseatthepi (replying to the OpenFC author) in #14882.

### Cited Findings
- #14882 "PICO: Initial commit for framebuffer OSD displayport device (FB_OSD) with RP2350 implementation." by mjs1441, created 2026-01-15, merged. Body: "FB_OSD implementation supports overlay on PAL and NTSC composite source, and introduces some pixel defined (not character based) osd elements." No hardware text in body., [PR #14882](https://github.com/betaflight/betaflight/pull/14882)
- #15161 "PICO: FB OSD improvements and new pixel based elements (AH, compass)", created 2026-04-28, merged. Adds pixel elements (artificial horizon, compass bar, later altitude, crosshairs), small font, logo, RAM saving. No hardware/sync text., [PR #15161](https://github.com/betaflight/betaflight/pull/15161)
- #15749 "PICO: New definition OSD_FLAGS_OSD_HARDWARE_FB_OSD == 1<<2", created 2026-09-22, merged. MSP flag so the Configurator knows an FB_OSD is present; also reports the configured video system. Not a sync change. Companion Configurator PR: [betaflight-configurator #5517](https://github.com/betaflight/betaflight-configurator/pull/5517)., [PR #15749](https://github.com/betaflight/betaflight/pull/15749)
- Related merged: #15643 "[2026.6] backport: PICO fixes, ESC/serial passthrough, DShot 150/300, FB OSD elements" ([link](https://github.com/betaflight/betaflight/pull/15643)); #15789 "OSD: allow board configs to override the default displayport device and video system" (body: "From @Just4Stan's OpenDrone fork.", i.e. our fork) ([link](https://github.com/betaflight/betaflight/pull/15789)); #15601 "always compile software fallback for FB-pixel altitude/AH/sidebars" ([link](https://github.com/betaflight/betaflight/pull/15601)); #15808, #15784, #15788 (RAM/build/SD, unrelated to sync).
- Pin constraint (author, #14882): "OSD_EN_PIN must be next GPIO up from OSD_W_PIN and OSD_SYNC_PIN next up from OSD_EN_PIN" with example `OSD_W_PIN PA16, OSD_EN_PIN PA17, OSD_SYNC_PIN PA18`., [comment](https://github.com/betaflight/betaflight/pull/14882#issuecomment-3761191241). Enforced in code: `"*** OSD_SYNC_GPIO must be next pin up from OSD_EN_GPIO"`, [osd_pico.c](https://github.com/betaflight/betaflight/blob/d593400a05a5e142c0f6f83cc45c237ef078c634/src/platform/PICO/osd/osd_pico.c) (`init_gpios`). Our GPIO14/15/16 satisfies this.
- Only level/comparator guidance found (Jaseatthepi, #14882, 2026-03-03): "For generating black and white levels a simple three resistor network can be used. Connect a 3K9 to a GPIO, 12k to +3.3V and 1.4k to GND. A logic 1 on the GPIO will be attenuated to about 1.0V and a logic 0 will be about 300mV." and "The comparator should be selected for a low propagation time, suggest 50ns or less to avoid shimmering. Also the input should extends 100mV or so below GND to avoid the need for additional biasing circuitry.", [comment](https://github.com/betaflight/betaflight/pull/14882#issuecomment-3992441500)
- That reply answered a question from Just4Stan (the OpenFC author) asking for the reference schematic of the Hellbender OSD, black/white level method, and "Any gotchas with the sync detection circuit? ... Schmitt trigger comparator but I'm unsure about the right hysteresis value." The question about hysteresis and the schematic was NOT answered in the thread., [question](https://github.com/betaflight/betaflight/pull/14882#issuecomment-3979929357), [follow-up](https://github.com/betaflight/betaflight/pull/14882#issuecomment-3992492682)
- Jaseatthepi's GitHub profile has no name/company set (checked via `gh api users/Jaseatthepi`), so affiliation with Raspberry Pi is not verifiable from the profile; the nickname suggests it, treat as unconfirmed.

### Inferences
- Divider math check (my calculation from the quoted values): GPIO high -> 3.9k||12k = 2.94k to 3.3 V over 1.4k to GND -> 1.06 V; GPIO low -> 3.9k||1.4k = 1.03k vs 12k -> 0.26 V. Consistent with the quote. So the reference pixel levels are approx 0.26 V (black) and 1.06 V (white) at the mux input, driven through a 2:1 mux, so they are intended to sit on the video line at the 75 ohm-terminated level (black ~0.3 V above sync tip scale). Compare with our OSD_W divider values.
- "Input should extend 100 mV below GND" implies the reference comparator sees the composite signal with its sync tip below ground (AC-coupled/clamped signal, sync tip going negative) and the comparator threshold is near 0 V. This is similar to our approach (IN- = GND), but it is a hint, not a documented spec.

### Gaps
- No public schematic for HELLBENDER_0001 or RASPBERRY_PI_UAVFC found (searches on GitHub repos, web search, betaflight.com board page returns 404 for RASPBERRY_PI_UAVFC). No hysteresis, threshold voltage or filter values documented anywhere found.
- No betaflight docs page for FB_OSD hardware found.

## 2. What sync separator do the reference boards use?

### Takeaway
Not publicly documented. Upstream configs only list pins. The one reference-ish board with a published description is TBS Lucid Raspberry Pi FC (74LVC1G3157 mux + TLV3231/TLV3541 comparators), but its Betaflight config says the OSD is inactive in firmware. No component values or threshold voltage were found for any reference board.

### Cited Findings
- betaflight/config has `configs/RASP/RASPBERRY_PI_UAVFC` (RP2350B, ICM56686, FB OSD default on, `OSD_W_PIN PA21`, `OSD_EN_PIN PA22`, `OSD_SYNC_PIN PA23`, `ENABLE_FB_OSD 1`, `USE_OSD_SD`)., [config.h](https://github.com/betaflight/config/blob/master/configs/RASP/RASPBERRY_PI_UAVFC/config.h). Comment: "In this config file, we choose between support for LED STRIP or FB OSD (both require a PIO block)". Added by mjs1441 in [config PR #1158](https://github.com/betaflight/config/pull/1158) (checklist: "passed hardware samples testing" ticked, "passed Betaflight team's schematics review" NOT ticked). Later commits 2026-08-12, 09-01, 10-01 touch motor order, BEC pins and UART defaults only (no OSD change).
- `configs/RASP/HELLBENDER_0001`: RP2350B, uses `USE_MAX7456` (not FB_OSD). The PR #14882 author said its config.h was "similar to that for HELLBENDER_0001" for the pin example, but the committed HELLBENDER config has no OSD_SYNC_PIN (grep)., [config.h](https://github.com/betaflight/config/blob/master/configs/RASP/HELLBENDER_0001/config.h). Note this conflicts with the question to Jaseatthepi about "the HELLBENDER's OSD analog circuit": treat which Hellbender revision carries the discrete OSD as unknown.
- `configs/RASP/PICO2_2350A`: bare Pico 2 target, no OSD., [config.h](https://github.com/betaflight/config/blob/master/configs/RASP/PICO2_2350A/config.h)
- `configs/TEBS/TBS_LUCID_RPI_FC` (reference date 2026-05-01): "Discrete analogue OSD (74LVC1G3157 mux + TLV3231/TLV3541) instead of MAX7456 (no Betaflight driver -- OSD pins are wired but inactive in firmware)", pins `OSD_W PA21, OSD_EN PA22, OSD_SYNC PA23`. So a commercial board uses the same mux part (SN74LVC1G3157 family) as ours and two comparator parts, but the circuit values are not in the config., [config.h](https://github.com/betaflight/config/blob/master/configs/TEBS/TBS_LUCID_RPI_FC/config.h)
- SP Racing configs matched a code search for `OSD_SYNC` (SPRACINGH7EVO, H7RF, H7EF) but these are STM32 H7 targets using a different OSD sync (not FB_OSD PIO); not investigated further., [search hit list via GitHub code search](https://github.com/betaflight/config/blob/master/configs/SPRO/SPRACINGH7EVO/config.h)
- Searched GitHub repos for hellbender/uavfc/raspberry pi flight controller hardware: no results. Web search found no Raspberry Pi Ltd drone FC reference design page.

### Inferences
- Every known RP2350 FB_OSD board uses the same 3-consecutive-GPIO scheme (W, EN, SYNC) and same mux family as ours, so our topology is aligned; the open question is only the sync comparator conditioning (threshold, clamp, filter), which cannot be compared against a published reference.
- Our own 680R + 470pF lowpass (tau about 0.32 us) is not described anywhere upstream; whether the reference has a lowpass is unknown.

### Gaps
- No schematic/PDF/KiCad for Raspberry Pi UAVFC, Hellbender, or TBS Lucid RPi FC found. Request: ask mjs1441 / Jaseatthepi on the betaflight Discord or in PR #14882 (hysteresis and schematic questions there are still unanswered); TBS may publish a Lucid RPi schematic (the config says "Based on ... the schematic for the TBS Lucid Raspberry Pi FC"), not located.
- TLV7031 input common-mode range, hysteresis and propagation delay: TI datasheet fetch returned unreadable PDF; not verified here.

## 3. Firmware sync detection requirements (osd_tx.pio, osd_pico.c, fb_osd_pico.c)

### Takeaway
Sync is expected ACTIVE-LOW on OSD_SYNC (high = no sync; PIO `wait 0 PIN` = sync pulse start). There is no vsync counter in the detection: detection counts HSYNC pulses (low pulse of about 3.9 us to 6.6 us width) between long pulses (>6.6 us), and requires the count to land in a narrow window (PAL 304-306, NTSC 252-255) for 16 consecutive field readings. If it fails, nothing visible happens: it keeps retrying forever, printing only to a debug trace.

### Cited Findings
Program: `osd_count_sync` in [osd_tx.pio](https://github.com/betaflight/betaflight/blob/d593400a05a5e142c0f6f83cc45c237ef078c634/src/platform/PICO/osd/osd_tx.pio), "running at 75MHz" (13.33 ns per PIO clock; `div = SystemCoreClock / 75e6`, [osd_pico.c](https://github.com/betaflight/betaflight/blob/d593400a05a5e142c0f6f83cc45c237ef078c634/src/platform/PICO/osd/osd_pico.c) `osdPioStartDetection`). The sync GPIO is configured as plain input for both WAIT (`sm_config_set_in_pin_base`) and JMP PIN (`sm_config_set_jmp_pin`); the firmware sets no pull-up/pull-down on it (the `gpio_set_pulls` lines for W/EN are commented out; none for SYNC).

Code (count program, verbatim):
```
waitVSync:
    wait 1 PIN, 0
    wait 0 PIN, 0
    set x, 14
d0: jmp x--, d0       [28]
    jmp PIN, waitVSync       ; shorter than VSync pulse at ~ 15*29/75 ~ 5.8us
...
waitsync:
    wait 0 PIN, 0
    set x, 8
d1: jmp x--, d1       [28]   ; wait then test for PIN being high
    jmp PIN, waitsync        ; shorter than HSync pulse at ~ 9*29/75 ~ 3.5us
    set x, 5
d2: jmp x--, d2       [28]
    jmp PIN, hsync           ; shorter than VSync pulse at ~ 15*29/75 ~ 5.8us
```
- Polarity: `wait 1 PIN` then `wait 0 PIN` = rising edge then falling edge = start of a LOW sync pulse; `jmp PIN` branches when the pin is HIGH meaning "pulse already ended". So an active-low (sync tip = logic low) signal is required; the video-active region must read HIGH., [osd_tx.pio](https://github.com/betaflight/betaflight/blob/d593400a05a5e142c0f6f83cc45c237ef078c634/src/platform/PICO/osd/osd_tx.pio)
- Pulse width classification (my timing calc from the code, 75 MHz): after the falling edge, first JMP PIN sample about 290 cycles = 3.9 us (comment says ~3.5 us); second sample about 494 cycles = 6.6 us. Low pulse < 3.9 us: ignored (equalizing pulses 2.35 us). 3.9 us to 6.6 us: counted as HSYNC (nominal 4.7 us). > 6.6 us: treated as a long (vsync/broad) pulse. In the initial waitVSync, a pulse must still be low at about 464 cycles = 6.2 us (comment: ~5.8 us) to count as the vsync marker.
- Vsync is therefore not detected by counting serration pulses; the program waits for a long pulse, then counts normal-width hsyncs until the next long pulse after at least one hsync (`jmp x!=y, vsync`), pushes remaining counter; CPU computes `hsyncs = initLines - value`, `initLines = 1000` ([osd_pico.c](https://github.com/betaflight/betaflight/blob/d593400a05a5e142c0f6f83cc45c237ef078c634/src/platform/PICO/osd/osd_pico.c) `osdPioCountHSyncs`). Result 0 means "not ready/invalid".
- PAL/NTSC auto-detect ([fb_osd_pico.c](https://github.com/betaflight/betaflight/blob/d593400a05a5e142c0f6f83cc45c237ef078c634/src/platform/PICO/osd/fb_osd_pico.c) `inNTSCrange`, `inPALrange`, `fbOsdInit`): NTSC accepts hsyncs per field of 252..255 (`ntscHsyncsMin 253`, `Max 254`, +-1); PAL accepts 304..306 (`palHsyncs 305`, +-1). `repeatTarget = 15`; `repeatCount` only increments when the new reading is in the same range as the previous one, so about 16 consecutive consistent field counts (roughly 0.3 s) are required. Anything outside both ranges resets the counter. Then `osdPioStartPAL()` or `osdPioStartNTSC()` loads the real TX program. If `vcdProfile->video_system` is forced and disagrees with the detected system, the forced one is used with a trace warning ("*** Warning: detected NTSC sync pattern but starting as PAL due to configuration ***").
- TX program (after detect) uses different, looser sync tests: vsync = low then still low after 750 clocks (10 us) (`set y,22 [12]; d1: jmp y--,d1 [31]; jmp PIN, await_vsync`); hsync low must last past about 251 clocks (3.35 us) (`jmp PIN, loop_hsync`); line start is timed from the falling edge using hshiftA/B/C. So detection with a 3.9 us minimum is the stricter test.
- PIO instruction memory: generated header shows `osd_tx_pal_program .length = 31`, `osd_tx_ntsc_program .length = 31`, `osd_count_sync_program .length = 25`, [osd_tx.pio.h](https://github.com/betaflight/betaflight/blob/d593400a05a5e142c0f6f83cc45c237ef078c634/src/platform/PICO/osd/osd_tx.pio.h). Confirms the "31 of 32" note: the TX program leaves one free slot, and the detection program must be removed (`pio_remove_program_and_unclaim_sm`) before TX is added; the whole OSD needs its own PIO block ("both require a PIO block", UAVFC config).
- Failure behaviour: `fbOsdInit` returns `FB_OSD_INIT_INITIALISING` on every call where hSyncs is 0, out of range, or not yet repeated; `checkReady()` in [displayport_fb_osd.c](https://github.com/betaflight/betaflight/blob/d593400a05a5e142c0f6f83cc45c237ef078c634/src/main/io/displayport_fb_osd.c) re-calls `fbOsdInit` indefinitely (`if (!fbOsdDeviceDetected) ... fbOsdInit(...) != FB_OSD_INIT_OK`), with no timeout, no error flag and no OSD output. The only diagnostics are `bprintf` lines ("OSD repeat %d of %d (%s)", "neither PAL nor NTSC", "OSD seen ... (PAL)") which exist only when `PICO_TRACE`/`DEBUG_OSD_FB_PICO` is built. `fbOsdReInitIfRequired()` is a stub `return false;` so after a successful init there is no re-detection if sync later changes. `FB_OSD_INIT_NOT_CONFIGURED` is returned only when PIO start fails.
- Pixel output pins: `out PINS,2` drives OSD_W (bit0) and OSD_EN (bit1) consecutively from OSD_W GPIO, 2 bits per pixel, 10 PIO clocks per pixel (7.5 pixels/us), 368 pixels/line, 288 (PAL) or 234 (NTSC) lines. At end of each line `set PINS, 0` puts both low (EN low = camera video through, under our SN74LVC1G3157 S=OSD_EN mapping, assuming S low selects B1/video: verify against our schematic).

### Inferences
- Detection depends on ~250/305 hsync pulses per field all being seen. Any systematic widening/narrowing of the sync low time at the comparator output outside 3.9..6.6 us will cause every hsync to be misclassified (too short = ignored and the count collapses; too long = counted as vsync marker so count is about 0-1), which would give "no PAL/NTSC" and an OSD that never starts, with no user-visible error. With a 0 V threshold the low time equals the width of the part of the sync pulse below 0 V; if the clamped blanking level sits near 0 V (see below), pulse width and edges become noise-sensitive.
- Active-low semantic check for our circuit: IN+ = clamped video, IN- = GND, push-pull output. Output is HIGH when the signal is above 0 V and LOW when below. That is correct polarity for the firmware only if the sync tip is below 0 V and everything else (blanking, black, picture) is above 0 V. A Schottky clamp (cathode on signal, anode GND) pulls the most negative excursion (sync tip) to about -Vf of the diode. Sync amplitude on a 75 ohm-terminated camera is about 0.3 V (NTSC 286 mV, PAL 300 mV). Thus blanking sits at about (-Vf + 0.3 V); if Vf is about 0.3 V (typical Schottky at low current, not datasheet-verified here) blanking is about 0 V, i.e. exactly AT the comparator threshold with no margin. That is a plausible root cause of the failure that differs by camera/rev and is worth a scope check. This is analysis, not a documented finding.
- Jaseatthepi's "extends 100 mV below GND" hint suggests the reference likewise puts the sync tip slightly below GND and places the threshold near mid-sync (or at 0 V with a signal not hard-clamped to -Vf), but nothing in the source confirms the reference's threshold.
- Vsync count reported by our fork ("0 vsyncs") is not a quantity upstream measures; upstream reports hsyncs per field. If our fork counts differently, compare with `osd_count_sync` semantics above.

### Gaps
- Exact RP2350 GPIO input thresholds (VIL/VIH) and Schmitt-trigger hysteresis not checked against the RP2350 datasheet here. With a 3.3 V push-pull comparator output this should not matter, but verify the TLV7031 output actually swings full-rail at the sync rate (propagation, load).
- Whether camera sync includes broad-pulse serrations that the 3.9 us / 6.6 us windows handle differently in PIO vs on the scope: not tested.

## 4. Known issues / bug reports about FB_OSD sync, no OSD, camera-specific failures

### Takeaway
Nothing found. There are no open or closed GitHub issues in betaflight/betaflight about FB_OSD sync detection, no OSD shown, or camera-specific failures. Only a hardware-reference question (unanswered hysteresis part) and a passing author remark about black frames.

### Cited Findings
- GitHub issue and PR searches in betaflight/betaflight for "FB_OSD", "FB OSD", "OSD_SYNC", pico/rp2350 + sync/hsync/vsync returned only PRs (#14882, #15161, #15749, #15601, #15643, #15789) and unrelated issues (#14743 PICO2_2350A PWM, #14744 SDCARD SDIO RP2350). No issue about sync/no-OSD. (queries run 2026-10-25 via `gh api search/issues`)
- Author remark in #14882: "Note that the occasional completely black screen is due to loose wiring and/or camera defect." (video demo), [comment](https://github.com/betaflight/betaflight/pull/14882#issuecomment-3761163645)
- Author states task-latency requirement: "we want the task have latency significantly less than 50Hz so that the drawing / rendering can always start shortly after a VSYNC signal.", [comment](https://github.com/betaflight/betaflight/pull/14882#issuecomment-3761191241) (only relevant after detection).
- Discord summaries: not accessible from this environment; not read.

### Inferences
- Absence of public bug reports means very few people run FB_OSD hardware; the author (mjs1441) tests with a limited camera set, so camera-specific behaviour (sync amplitude, pedestal, sync-tip level, serrations) is untested upstream.

### Gaps
- Discord #pico / betaflight-dev discussions not searched (no access). Recommend asking there with the hsync-count window and the PIO classification above, and requesting the Hellbender/UAVFC OSD schematic.
- Raspberry Pi Forums / Hackaday posts for UAVFC/Hellbender not found.
