# IMU Selection Investigation — OpenFC-Lite-Mini Rev 2

**Status:** open · **Started:** 2026-06-02 · **Owner:** Stan

The Rev 1 IMU (ST **LSM6DSV16XTR**) is populated for development only. The Betaflight
team considers it unflyable; bench/flight data agrees. This folder collects datasheets,
sourcing data, and conversation intelligence to pick the **Rev 2 IMU**.

Footprint is **LGA-14 (2.5×3 mm)**, pins 2/3→GND and 10/11→NC — electrically safe for
**both TDK (ICM-426xx/456xx) and ST (LSM6D\*) families**. IMU swap is a field change once
a part is chosen. See `../../CLAUDE.md` → IMU section.

```
imu-selection/
├── README.md          ← this file (single source of truth for the investigation)
├── datasheets/        ← collected datasheets, named by part
└── (add scope captures, logs, FFTs here as they come in)
```

---

## 1. Hard requirements

| # | Requirement | Why |
|---|---|---|
| R1 | **Betaflight driver on current master** | No driver = no flyable firmware. Authoritative list below. |
| R2 | **Drops into LGA-14 (2.5×3 mm), pins 2/3 GND, 10/11 NC** | Existing footprint; pin-1 orientation must match. |
| R3 | **Flyable** — low in-band gyro noise, robust to electrical + vibration noise | The whole reason DSV16X is being replaced. |
| R4 | **Sourceable at volume** (LCSC/JLC preferred, real stock) | Selling the board; rest of BOM < $5. |
| R5 | **Price target** — ideally ≤ ~$3–4 to keep the "Lite" price point | IMU currently dominates BOM cost. |
| R6 | **VDDIO works at 1.8 V analog / 3.3 V IO** | Board runs IMU off +1.8V_GYRO (U6 NCV8187) + 3.3V IO. |

A part failing R1 or R2 is out unless someone commits to adding the driver / reworking the
footprint.

---

## 2. Betaflight supported-IMU list (authoritative)

From `drivers/accgyro/accgyro.h` (`gyroHardware_e`) + `sensors/acceleration.h` on current
master. **Only these have flyable drivers today.**

- **InvenSense MPU:** MPU6000, MPU6050, MPU6500, MPU9250
- **InvenSense ICM-206xx:** ICM20601, ICM20602, ICM20608G, ICM20649, ICM20689
- **InvenSense ICM-426xx / 40609:** ICM42605, **ICM42688P**, **ICM42622P**, ICM42686P, ICM40609D
- **InvenSense IIM industrial (426xx driver):** IIM42652, IIM42653
- **InvenSense ICM-456xx:** ICM45605, **ICM45686**
- **Bosch:** BMI160, **BMI270**
- **ST:** LSM6DSO, **LSM6DSV16X**, **LSM6DSK320X**, L3GD20 (gyro-only)
- **Virtual:** SITL/HITL

**NOT on master (would need a driver):** ICM-56686 (RPi is adding it — not merged),
BMI323, BMI088, ICM-42670-P, LSM6DSV320X (the *V* high-g, ≠ the *K*).

---

## 3. Candidate matrix

Pricing/stock from LCSC paste **2026-06-02** (EUR). "BF" = on master. Footprint column
flags anything that isn't a clean drop-in.

| Part | BF | Price (qty) | LCSC stock | Footprint | Gyro noise mdps/√Hz | Verdict |
|---|---|---|---|---|---|---|
| **ICM-42688-P** | ✓ king | €12.15 / €10.49 lt | 0 (10k @7-9d other) | LGA-14 2.5×3 ✓ | **2.8** | Best-flying, too expensive + tight supply |
| **ICM-42622P** | ✓ | not in paste — source | ? | LGA-14 ✓ | ~2.8 (class) | sugar K "amazing" — **find pricing/stock** |
| **IIM-42652** | ✓ | (see paste; IIM-42653 €13.15) | 42653: 4,969 | LGA-14 ✓ | 3.8 | Industrial temp, pricey |
| **ICM-45686** | ✓ | €18.20 / €6.23 lt | 0 (353 other) | **LGA-14 3×2.5** ⚠ rotated | ~ | Newer; verify pin-1, costly |
| **ICM-45605** | ✓ | €6.35 | 0 | LGA-14 | — | budget 456xx, 0 stock |
| **ICM-42605** | ✓ | €5.60 / €4.90 lt | 10,000 ✓ | LGA-14 2.5×3 ✓ | (class) | **In stock, supported — solid fallback** |
| **BMI270** | ✓ | €3.19 / €1.36 lt | 0 (50k @6-8d other) | LGA-14 2.5×3 | 7 (perf) | **Cheap + available + only AC-PSRR spec'd** ⚠ verify Bosch pinout |
| **LSM6DSO** | ✓ | €3.70 | 6,312 ✓ | LGA-14 2.5×3 ✓ | (older) | cheap, available, older gen |
| **LSM6DSV16X** | ✓ | €4.07 | 4,350 | LGA-14 2.5×3 ✓ | 2.8 | **Current Rev 1 — unflyable, being replaced** |
| **LSM6DSK320X** | ✓ | not released | 0 | LGA-14 2.5×3 ✓ | **3.8** | BF/STM target; **not orderable**, samples gated |
| ICM-56686 | ✗ | (RPi sharing ds) | — | LGA-14 2.5×3 | 2.9 | No BF driver yet (RPi adding); 29.3kHz MEMS |
| BMI323 | ✗ | €3.28 | 2,920 | LGA-14 | — | No BF driver; Bosch filters undocumented |
| BMI088 | ✗ | €8.16 | 3,468 | **LGA-16 3×4.5** ✗ | 14 | No driver, wrong footprint, 2.4V floor — out |
| LSM6DSV320X | ✗ | €10.95 | 0 | LGA-14L | — | *V* variant, no BF driver (≠ DSK) |

---

## 4. Datasheet spec comparison

Mined from the PDFs in `datasheets/`. "n/s" = not specified in datasheet.

| Spec | ICM-42688-P | IIM-42652 | ICM-56686 | BMI270 | BMI088 | LSM6DSV16X | LSM6DSK320X |
|---|---|---|---|---|---|---|---|
| Gyro noise (mdps/√Hz) | **2.8** | 3.8 | 2.9 / 2.5(20b) | 7 / 10 | 14 | **2.8** | 3.8 |
| Accel noise (µg/√Hz) | 65/70 | 70 | 55/70 | 160 | 190 | 60/100 | 60/100/1000(hi-g) |
| Gyro FS max (dps) | 2000 | 2000 | 4000 | 2000 | 2000 | 4000 | 4000 |
| Accel FS max (g) | 16 | 16 | 32 | 16 | 24 | 16 | **320** (hi-g) |
| Max gyro ODR (kHz) | 8 | 8 | 6.4 | 6.4 | 2 | 7.68 | 7.68 |
| MEMS resonant freq | n/s | n/s | **29.3 kHz** | n/s | n/s | n/s | n/s |
| Anti-alias filter | AAF 42–3979Hz + notch | AAF 42–3979Hz | AAF+LPF | LPF | LPF 5–532Hz | analog AAF + LPF1 | analog AAF + LPF1 |
| VDD / VDDIO (V) | 1.71–3.6 / 1.71–3.6 | 1.71–3.6 / 1.71–3.6 | 1.71–3.6 / 1.08–3.6 | 1.71–3.6 / 1.2–3.6 | **2.4**–3.6 / 1.2 | 1.71–3.6 / 1.08 | 1.71–3.6 / 1.08 |
| SPI max (MHz) | 24 | 24 | 24 | 10 | 10 | 10 | 10 |
| Package | LGA-14 2.5×3 | LGA-14 2.5×3 | LGA-14 2.5×3 | LGA-14 2.5×3 | **LGA-16 3×4.5** | LGA-14 2.5×3 | LGA-14 2.5×3 |
| **PSRR / supply-noise spec** | 10mVpp tol. | 10mVpp tol. | 10mV typ/50max, to 1MHz | **AC PSRR: gyro 0.40dps/50mV, accel <8mg/50mV, 100Hz–1MHz** | DC drift only | **n/s** | **n/s** |
| CLKIN | **yes** 31–50k | **yes** | **yes** 20–40k | no | no | no | no |

### Headline findings

1. **The DSK320X is NOT a quieter gyro than the DSV16X.** On paper it's *worse* — 3.8 vs
   2.8 mdps/√Hz, identical accel noise. Neither ST datasheet documents a MEMS resonant-freq
   change or sensor-level vibration-immunity improvement. The DSK's only vibration-relevant
   edge is the **±320 g high-g channel** (clip resistance under hard impact) + quad-channel
   UI/EIS/OIS/high-g filtering — **not** a lower-noise or more supply-robust gyro core. This
   directly contradicts the framing that the DSK "fixes the noise" — the fix, if real, is in
   MEMS hardware ST does not document, or in the high-g anti-clip path.

2. **Neither ST part specs any PSRR / supply-noise rejection.** This is the standout gap
   versus the observed failure (sensitivity to *electrical* noise). You cannot design a
   supply-ripple budget against a number that doesn't exist.

3. **BMI270 is the only candidate with a frequency-resolved AC PSRR:** gyro 0.40 dps per
   50 mV ripple (100 Hz–1 MHz). InvenSense parts at least give a max-tolerable-ripple (10 mV).
   If supply-coupled noise is the real culprit, Bosch + InvenSense give you a spec; ST gives
   you nothing.

4. **Vibration-aliasing immunity:** ICM-56686 is the only part publishing a MEMS drive
   frequency (29.3 kHz — far above any propwash band, good anti-alias margin). BMI088 is the
   only one with explicit "drone/robotics vibration suppression + ±24 g anti-clip" language —
   but it's the worst on noise, wrong footprint, no driver. Out on R1/R2.

---

## 5. Intelligence log (from conversations / emails)

### Betaflight — sugar K (project lead)
- LSM6DSV16X is **unflyable**; STM agrees; "too sensitive to electrical noise." Tested on
  5+ FCs across brands, all unacceptable. **Will not approve it on 180+ brands' hardware.**
- Recommends **LSM6DSK320X** — BF working *directly with STM*; mass production **June 2026**.
  Says it's "worth waiting for," drop-in on the LSM16 design.
- **ICM-42688 "still king"** but TDK supply is hard. **ICM-42622 "amazing."**
- Doesn't trust **Bosch** (BMI270 internal filters "secret" when asked; "not great but cheap
  and works"; "pin-for-pin, swap it later"). Recommends BMI270 only as cheap interim.
- Against **clone IMUs** (HXY ICM-42688P etc.) on principle — "who knows what you're getting."
- Non-approved BF target = free; approved/full target = ~$500 (T2 cloud). Offered free
  schematic-review channel.
- ⚠ Bias to note: BF/STM have a working relationship + ST has commercial interest in DSK320X
  winning the comparison (Osiris flagged this too). Weigh accordingly.

### Betaflight-adjacent — Osiris (NL)
- DSV16X is a "dead end" gyro per BF devs; exact basis unclear to him.
- Notes our LDO is unusually good: **NCV8187 ~90 dB PSRR**, and running IMU at **1.8 V**
  means a large LDO dropout → even better rejection. Argues our board's electrical
  environment is *better* than the cheap Chinese FCs BF tested on → DSV16X failures there may
  be PCB/PDN-specific, not intrinsic to the part.
- DSK320X has **different MEMS hardware**. DSV320X is €5–6 at DigiKey (the *V* high-g).
- Suggests: ship **OpenFC Lite with BMI270** (cheap, good price point) now; premium OpenFC
  with a proper IMU later.

### Our own flight data — Krhom [BL]
- Red trace = our board (DSV16X). **Prefilter gyro shows ~20 dB more <100 Hz broadband noise**
  than an ICM reference board, on a *hover* test. "Awful," would need to detune hard.
- Comparison is apples-to-apples: both FCs MCU-down, gyro-up → noise is **not** ESC-side.
- Will try **adding a cap on 5 V** (often helps) → points at supply-coupled noise.
- ⚠ Counter-data from Stan: a 1408/3750kv/6S 3" test quad on DSV16X flew **perfectly** once an
  AOS 3.5 preset was applied — i.e. the issue may be tune/filtering, not raw sensor. Sample
  size 1. Worth resolving before committing.

### Raspberry Pi — Jason Young
- RPi adding **ICM-56686** support as an ICM-42688 alternative (TDK confirmed datasheet OK to
  share → in `datasheets/`). **No BF driver yet**; RPi timeline ~3-4 weeks for a board to test.
- RPi IMU LDO: **AP7347 (~75 dB PSRR claimed; measuring less in kHz range)** — *worse* than
  our NCV8187. Supports the "our PDN is fine" hypothesis.
- We're on RPi **beta-tester list** (early hardware access). Gordon (CTO) shared the FC video
  internally; Chris Boross (commercial) wants a chat.
- RPi confirmed our OSD PIO pin order (lowest GPIO = OSD_W) — matches our target. (OSD, not IMU.)

---

## 5b. What actually matters in FPV (not bench noise density)

FPV is not a clean environment — the gyro lives in heavy mechanical vibration (motors, props,
frame/arm resonances, often 0.5–4 kHz) plus ESC switching/EMI. **Bench noise density is nearly
the wrong figure of merit.** Proof: the DSV16X has the *best* noise density of every candidate
here (2.8 mdps/√Hz, tied with the 42688) and is still unflyable. Flyability is set by how the
part handles **out-of-band energy**, not its quiet-room floor:

1. **Vibration rectification / aliasing.** Out-of-band vibration (kHz) folds into the control
   band as a DC offset shift + low-frequency broadband — exactly the **<100 Hz broadband**
   signature on Krhom's red trace. Governed by the **MEMS drive/sense resonant frequency** and
   the **analog anti-alias filter ahead of the ADC** (not the digital LPF, which is too late).
   → ICM-56686 is the only part publishing its resonant freq (29.3 kHz, big margin). ST parts
   publish neither resonant freq nor rectification behavior.
2. **Clipping headroom under vibration.** Instantaneous rate/accel spikes that exceed FS clip,
   and clipping rectifies into DC + harmonics. This — not "more range" — is why DSK320X has a
   ±320 g accel channel and BMI088 has ±24 g. A ±16 g accel can saturate on a rough quad.
3. **Supply / EMI rejection.** ESC switching coupling into a part with unbounded PSRR. ST specs
   none; BMI270 specs AC PSRR; InvenSense specs a max tolerable ripple.

**Consequence for this investigation:** rank candidates on (1) anti-alias/resonant-freq margin,
(2) clip headroom, (3) PSRR — and above all on **empirical flight/blackbox data**, since
datasheets barely document any of the three. The noise-density column in §4 is informational,
not a selection criterion. This is why BF qualifies gyros by flying them, and why a
worse-on-paper part (DSK320X) can outfly the DSV16X.

## 5c. Prior diagnostic campaign — firmware A/B branches (Just4Stan/betaflight)

A documented DSV16X diagnostic effort already ran on the **OpenFC-ECO V0.3** sister board
(same LSM6DSV16XTR), late April 2026. Each branch = one firmware variant + hypothesis + a
blackbox test plan written in the commit body. **This is the "which log contains what" map.**
Branches carry the test plan only; results live in the blackbox logs (not in git — still to recover).

| Branch / commit | Date | Change | Hypothesis | Symptom targeted | Log: compare |
|---|---|---|---|---|---|
| `diag/lsm6dsv16x-drdy-latched` (e106c6e9) | 04-28 | DRDY PULSED→LATCHED | RP2350 @150 MHz EXTI+SPI-DMA latency exceeds the **75 µs DRDY pulse** under heavy IRQ load (PIO DSHOT/UART, SD blackbox) → missed gyro samples → sample-rate drift | **200 Hz oscillation under throttle, fine at hover** (V0.3) | gyro raw vs filtered vs baseline |
| `diag/lsm6dsv16x-no-acc-hpf` (97861fc6) | 04-28 | accel LPF2 250 Hz→~22 Hz | motor-harmonic vibration >250 Hz leaks into accel → corrupts IMU-fusion gravity vector | **"gravity-vector wandering" in ANGLE mode** | accSmooth + imuQuaternion stability vs baseline |
| `pico/sysid` (b4b85bab) | 05-07 | on-board chirp PID identifier (`USE_SYSID`) | — (tooling) | — | `sysid raw` emits versioned **FRF CSV**; cross-checked vs pichim's MATLAB |
| `flyable/phase1-chirp-osdhd` (d18ad4c0) | 04-29 | config bump "for chirp/overclock/**ICM** target updates" | — | — | (shows an ICM target variant was already being prepped) |

**Why this matters for IMU selection:** the two leading in-house hypotheses for the DSV16X
misbehaviour are **firmware/platform**, not "bad MEMS":
1. a **DRDY timing bug specific to RP2350 under load** (missed samples → the 200 Hz throttle
   oscillation), and
2. an **accel-filter config** leaking vibration into fusion (gravity wander).

Both are fixable without changing the sensor. This strongly reinforces §6 — the part may be
partly mis-integrated on RP2350, not intrinsically unflyable. Note these symptoms (200 Hz
under-throttle oscillation; gravity wander) are **distinct from Krhom's** report (<100 Hz
broadband prefilter noise at hover) — so there may be ≥2 independent problems, only one of
which the sensor swap would fix.

**Action:** recover the blackbox logs from these three diag builds + their baseline, and the
`sysid raw` FRF CSV. Those are the highest-value missing evidence (see §8). The `pico/sysid`
branch + pichim's MATLAB pipeline ([[reference_pichim]] in the BF-repo memory) is the analysis path.

## 5d. RESOLVED on the sister board — empirical (config: Just4Stan/config @ `openfc/imu-alignment`)

The firmware A/B campaign concluded the DSV16X problem is **not firmware-fixable** — it's a MEMS
hardware property. The `OPENFC_ECO_RP2350B/config.h` swap comment states it directly:

> *"LSM6DSV16XTR … found to have a **MEMS resonance vulnerability in the ~25 kRPM motor band**
> on this airframe (the chip internal gyro **saturates from acoustic/vibration energy at the
> resonator's drive frequency, producing bursts of false rotation reads up to chip full-scale
> ±2000 dps**). Swapping to **ICM-42688-P** (drop-in pin-compatible … confirmed by multiple BF
> targets that support both chips on the same pads) **eliminated the resonance issue. V0.4 PCB
> will be designed with ICM-42688-P only.**"*

Config now: `USE_GYRO_SPI_ICM42688P` / `USE_ACC_SPI_ICM42688P` on SPI0, CS=PA14, EXTI=PA13,
`DEFAULT_ALIGN_BOARD_PITCH 180` (V0.3 IMU rotated 180° about pitch).

**What this settles — and what it does NOT.**

Settled: **swapping to ICM-42688-P made the board flyable**, and ECO V0.4 standardizes on it.
That's a solid empirical result for *part selection*.

NOT settled — the **root cause**. The "MEMS resonance in the ~25 kRPM band" wording is the
integration team's *hypothesis writeup* (Claude-co-authored config comment), not a measured
result, and it does not survive scrutiny as a single cause:

- **Krhom's noise is <100 Hz broadband at HOVER** (low RPM/vibration). A high-RPM resonance
  should be throttle-dependent and absent at hover — which is what the *diag branch* describes
  ("200 Hz under throttle, fine at hover"). So there are **≥2 distinct symptoms**, not one.
- **"~25 kRPM band" is physically shaky:** 25 kRPM ≈ 417 Hz fundamental; a MEMS gyro drive
  resonance is ~20–25 **kHz** (~50× higher). 417 Hz vibration doesn't excite a 20 kHz drive
  mode directly. The plausible mechanism is **aliasing** (out-of-band energy folding in through
  an inadequate AAF) — a filtering/architecture issue, not "resonator saturation."
- **"5 V cap helps" + sugar K's "electrical noise" + ST publishing no PSRR** → an independent
  **supply/PSRR** contributor.
- **An AOS preset made one build fly perfectly** → **tune/filtering** is a large lever; a hard
  MEMS-saturation defect wouldn't yield to a preset.
- **The ICM swap is a confounded experiment:** it changed sensor + driver maturity + AAF/notch
  behavior + CLKIN jitter removal simultaneously. It does **not** isolate resonance as the cause.

**Working model: multi-causal**, at least — (1) anti-alias/filtering inadequacy → aliased
broadband; (2) supply/PSRR sensitivity; (3) RP2350 DRDY/sample-timing under load; (4) MEMS
resonance/clipping at high vibration; (5) driver/tune immaturity. The ICM-42688-P is better on
*several* of these at once, which is why it works — but the dominant factor is not isolated.

**Consequence for selection:** because the win is partly filtering/driver/PSRR (not purely a
MEMS-element property), a same-family ICM-42605 is a *strong* bet (shares AAF+notch+driver), and
the **BMI270's real AC-PSRR spec regains relevance** if supply coupling is a major contributor.
Only the actual logs/FFT (hover vs throttle, ± a supply-ripple injection test) can decompose it.

## 6. Working hypothesis

The DSV16X's in-flight noise is most plausibly **supply/electrical-coupling + tune**, not a
raw-noise-density deficit (its density spec is best-in-class, tied with the 42688). Evidence:
- 20 dB excess is **broadband <100 Hz** = classic aliased/rectified noise, not white density.
- "Adding a cap on 5 V helps" + "sensitive to electrical noise" = PDN/supply path.
- A good preset made it fly fine on our board (better PDN than the FCs BF condemned).
- ST publishes **no PSRR**, so the part's supply robustness is genuinely unknown/unbounded —
  consistent with it being fragile on noisy boards even if fine on a clean one.

This means the decision is partly **political** (BF approval / the 180-brand ecosystem rejects
DSV16X regardless of our data) and partly **technical** (what actually flies clean on *our*
PDN). Those can have different answers.

---

## 7. Decision options

**Reframed by §5d:** the failure is MEMS resonance saturation, and **ICM-42688-P is the
empirically proven fix** on the sister board. The 426xx family shares the same gyro sense-element
architecture, so a cheaper family member is the *likely* — but not yet proven — way to keep the
fix at a Lite price. A different-MEMS part (BMI270) is now a real risk, not a safe interim.

- **A — ICM-42688-P (proven). ← lowest technical risk.** The exact part that eliminated the
  resonance on OPENFC-ECO; ECO V0.4 standardizes on it. Drop-in (§4), uses wired CLKIN (GPIO15).
  **Cost is the only problem:** €10–12, 0 LCSC stock (10k other @7-9d). Kills the sub-$5 "Lite"
  price point. Right call for a *premium* OpenFC; painful for Lite.
- **B — ICM-42605 (cheap same-family bet). ← leading for Lite (2026-06-02).** Same 426xx gyro
  architecture as the 42688 → *most likely* shares the resonance immunity (same sense element,
  different binning/noise grade). BF-supported, **10,000 in LCSC stock @ €4.90–5.60**, clean
  2.5×3 footprint, uses the wired CLKIN. **Risk: the resonance immunity is not yet confirmed on
  the 42605 specifically** — verify by flying it (it shares the 42688 driver, so it's a config
  one-liner: `USE_GYRO_SPI_ICM42605`). If it holds, this is the answer for Lite.
- **C — ICM-42622P** (sugar K "amazing", same family) — but **€15 / out of stock** per Stan.
  Out on price/supply right now.
- **D — BMI270 (cheapest, now higher risk).** €1.36–3.19, 50k stock, BF-supported, footprint
  drop-in (§7b), only candidate with a real AC-PSRR spec. **But:** different Bosch MEMS — we now
  know the DSV16X failure was MEMS-resonance, and there is **no evidence BMI270 survives this
  airframe's resonance band**. Bench noise density (7) is irrelevant (§5b); the resonance
  question is not. Only choose if 42605 also fails and price dominates — and flight-test it
  against the same airframe first.
- **E — DSK320X** — BF/STM blessed, drop-in, but **not orderable** (samples gated), and per §4
  not a lower-noise gyro. Track for the premium SKU; not actionable for Rev 2 now.
- **F — Two-SKU strategy.** Premium OpenFC = ICM-42688-P (proven). Lite = ICM-42605 if it flies
  clean, else BMI270 as the cost-floor fallback. Aligns the premium board with ECO V0.4.

**Recommendation:** Lite-Mini Rev 2 → **ICM-42605** (in stock, cheap, same family as the proven
fix, wired CLKIN usable), with **ICM-42688-P** as the drop-in premium/no-compromise option on the
identical footprint. **Flight-test the 42605 against a ~25 kRPM-band airframe before committing** —
that's the one open risk, and it's cheap to close.

---

## 7b. BMI270 footprint verification (DONE 2026-06-02)

Checked BMI270 pinout vs the actual board net on U9 (netlist export of `OpenFC.kicad_sch`).
Board pins wired for the LSM6DSV16X: 1 MISO, 2 GND, 3 GND, 4 INT, 5 +3.3V, 6 GND, 7 GND,
8 +1.8V_GYRO, 9 CLKIN(GPIO15), 10 NC, 11 NC, 12 CS, 13 SCK, 14 MOSI.

**BMI270 is a drop-in, with two caveats:**
- **Pins 2/3 = ASDx/ASCx (aux/OIS), hard-grounded on our board.** Bosch documents "VDDIO or
  DNC", *not* GND. The shared 20×20 FC footprint grounds these and BMI270 ships on it across
  many BF boards (works empirically), but it is **outside Bosch's stated spec** — verify on a
  sample; worst case a DNC cut on 2/3.
- **Pin 9 = our CLKIN net (GPIO15).** On BMI270 pin 9 is INT2 (no clock input). No regression
  (ST part also has no CLKIN); just don't drive a clock on GPIO15 in firmware. Aligns with the
  Rev 2 "drop CLKIN" plan.
- All other pins (SPI 1/12/13/14, VDD 8 @1.8V, VDDIO 5 @3.3V, INT1 4, GND 6/7, NC 10/11) match 1:1.

## 8. Open verification tasks

- [x] **BMI270 LGA-14 pinout** vs our footprint → drops in; caveats on pins 2/3 (grounded aux,
      out-of-spec but field-proven) and pin 9 (CLKIN→INT2, harmless). See §7b.
- [ ] **ICM-45686 footprint** is LGA-14 **3×2.5** (rotated vs our 2.5×3) — check pin-1 / land.
- [ ] **Source ICM-42622P** — LCSC/DigiKey/Mouser pricing, stock, lead time.
- [ ] **DSK320X availability + price** — DigiKey/Mouser/STM samples; realistic date beyond "June."
- [ ] **CLKIN decision** — Rev 2 plan drops CLKIN (GPIO15); if a TDK part (42605/42688/42622/
      45686/56686) is chosen, **keep CLKIN** for jitter removal. ST/Bosch don't use it.
- [ ] **Get the actual FFT/blackbox** from Krhom (red trace) into this folder — quantify the
      20 dB, identify the noise frequency signature (aliased vs supply tone vs propwash).
- [ ] **Resolve the contradiction:** if a tune made DSV16X fly clean on our board, characterize
      *why* BF's boards failed — PDN measurement on a noisy reference FC vs ours.
- [ ] Confirm **+1.8V_GYRO rail** is fine for each finalist's VDD (all OK except BMI088's 2.4V).
- [ ] Decide whether ICM-56686 is worth waiting for RPi's driver (we're on their beta list).

---

## 8b. Log comparison — PIDtoolbox method + first run (2026-06-02)

**How PIDtoolbox (PTB) works** (Brian White / bw1129, MATLAB or compiled standalone):
decodes BF blackbox → modules: **Spectral Analyzer** (gyro/dterm PSD in dB + **Freq×Throttle
spectrogram**), **Step Response** (setpoint→gyro deconvolution), time-domain plots.
- Set **`debug_mode = GYRO_SCALED`** so unfiltered gyro is logged (PTB then shows *gyro prefilt*
  vs *gyro*, and computes filter phase latency). **Modern BF (2026.x) logs `gyroUnfilt[]`
  natively** regardless of debug_mode — our logs have it, so prefilter analysis works anyway.
- Log at **2 kHz** (spectrograms reach ~1 kHz). Fly **throttle sweeps** (idle→full over 5–10 s, ×2–3).
- **Reading Freq×Throttle:** diagonal line rising with throttle = **motor noise (tracks RPM)**;
  horizontal line at fixed Hz = **frame resonance or electrical (throttle-independent)**;
  <20 Hz = real craft movement (ignore for noise); 20–100 Hz should be quiet (propwash/tune).
- **Bad-gyro test:** one axis much noisier <200 Hz; rotate FC 90° — if the noisy axis follows, gyro suspect.

**Why prefilter (`gyroUnfilt`) is the right signal here:** it's the raw sensor before BF's filter
stack, so comparing it removes the filter-tune confound and isolates the *sensor*.

**Reproduce without MATLAB:** `analysis/compare_gyro.py LOG_A.csv LOG_B.csv labelA labelB`
(numpy/scipy/matplotlib) emits `psd_overlay.png`, `spectrogram_<label>_<axis>.png`, and a
band-RMS table. PTB GUI crashed on macOS 2026-06-02; this is the fallback + it's repo-committed.

**First run — LOG00083 vs LOG00090** (both OPENFC_ECO, BF 2026.6.0-alpha, 8 kHz loop, logged
≈1.88 kHz → 940 Hz Nyquist). **Inconclusive on sensor — the pair is not controlled:**
- LOG83 = 135 s full sweep, gyro LPF off; LOG90 = **only 6 s**, sparse throttle, dyn-LPF 250/500.
- **Which log is which sensor is unknown** (BF header doesn't name the gyro; same firmware hash
  runs either chip via autodetect). **Need Stan to map LOG#→sensor.**
- Prefilter PSD floors **nearly overlap** in the noise-dominated bands (motor hump ~200–400 Hz,
  >400 Hz). The big 0–20 Hz "RMS" differences are **flight movement, not noise** (135 s aggressive
  vs 6 s) — not a sensor signal.
- LOG83 spectrogram = **clean, healthy**: motor band tracks throttle, no fixed horizontal lines,
  no saturation bursts. LOG90 looks hotter in 200–500 Hz but is too short/sparse to trust.

**Verdict:** these two logs cannot decide DSV16X vs ICM. Need a **matched pair**: same craft,
both throttle sweeps, ≥30 s each, same filter config (or compare prefilt only), and a known
LOG#→sensor map. Then the Freq×Throttle + prefilt-PSD overlay will show whether the DSV16X has
(a) RPM-tracking diagonal excess (vibration/alias), (b) fixed-Hz lines at idle (electrical/PSRR),
or (c) saturation bursts (resonance/clipping) — decomposing §5d's multi-causal model.

## 8c. Universal drop-in verification (footprint + nets, working tree 2026-06-03)

Footprint `lib:LGA-14_L3.0-W2.5-P0.50-BR`. U9 net map (post-Bastian pull): 1 MISO · 2 GND ·
3 GND · 4 INT · 5 +3.3V(VDDIO) · 6 GND · 7 GND · 8 +1.8V_GYRO(VDD) · 9 CLKIN(GPIO15) ·
10 NC · 11 NC · 12 CS · 13 SCK · 14 MOSI. Checked against datasheet pinouts:

| Pin | Board net | ST LSM6D* (DSV16X / DSK320X / DSO) | TDK ICM-426xx / IIM-426xx | Bosch BMI270 |
|---|---|---|---|---|
| 1 | MISO | SDO ✓ | AP_SDO ✓ | SDO ✓ |
| **2** | **GND** | SDx — *"VDDIO or GND"* ✓ | RESV — *NC/GND* ✓ | ASDx (aux, unused→input) — table prefers *VDDIO/DNC*, GND benign ✓ |
| **3** | **GND** | SCx — *"VDDIO or GND"* ✓ | RESV — *NC/GND* ✓ | ASCx (aux, unused→input) — GND benign ✓ |
| 4 | INT | INT1 ✓ | INT1 ✓ | INT1 ✓ |
| 5 | +3.3V | VDDIO ✓ | VDDIO ✓ | VDDIO ✓ |
| 6 | GND | GND ✓ | GND ✓ | GNDIO ✓ |
| 7 | GND | GND ✓ | RESV→GND ✓ | GND ✓ |
| 8 | +1.8V | VDD ✓ | VDD ✓ | VDD ✓ |
| 9 | CLKIN | INT2 (idle, ok)¹ | INT2/FSYNC/**CLKIN** ✓ (uses it) | INT2 (idle, ok)¹ |
| 10 | NC | OCS_Aux NC ✓ | RESV NC ✓ | OCSB DNC ✓ |
| 11 | NC | SDO_Aux NC ✓ | RESV NC ✓ | OSDO DNC ✓ |
| 12 | CS | CS ✓ | AP_CS ✓ | CSB ✓ |
| 13 | SCK | SCL/SCLK ✓ | AP_SCLK ✓ | SCK ✓ |
| 14 | MOSI | SDA/SDI ✓ | AP_SDI ✓ | SDI ✓ |

¹ pin 9 = INT2 on ST/Bosch; harmless as long as firmware does not drive a clock on GPIO15.

### Verdict — pins 2/3 at GND are fine for all; footprint is universal
The board grounds pins 2/3. For an **unused** aux interface this is correct/benign across all families:
- **ST LSM6D\*** (DSV16X / DSK320X / DSO): datasheet sanctions pins 2/3 → "VDDIO **or GND**". ✓
- **TDK ICM-426xx/IIM and ICM-456xx/56xx-gen** (confirmed from ICM-56686 pinout: pins 2/3/10/11 =
  RESV/AUX1, pin 9 = INT2/FSYNC/CLKIN — same universal layout): RESV = "NC **or GND**". ✓
- **Bosch BMI270 — GND is safe (mechanism verified in datasheet, 2026-06-03):** aux/OIS is disabled
  by default (`PWR_CTRL.aux_en=0`; BF never enables it for a bare gyro), so ASDx/ASCx are **high-Z
  inputs** — nothing drives them, GND = no contention. The only "pull-up" is a *configurable* internal
  pull-up on ASDA (`AUX_IF_TRIM.asda_pupsel`: off/40k/10k/2k) used for the aux-I2C SDA line; inactive
  when aux is off (worst case a 40k pull → ~80 µA to GND, harmless). Bosch's "VDDIO or DNC" is
  conservative guidance for the aux-*enabled* case; it does **not** mean GND damages the part. Bosch's
  own power-off note even says interface pins "must be kept close to GNDIO potential." The *only*
  failure case is firmware enabling the aux **I2C master** (ASCx becomes a driven clock → GND short) —
  which BF does not do. **GND is the correct universal tie** (VDDIO fails TDK RESV; NC fails ST's
  "needs a level"). One firmware caveat: never enable the BMI270 aux interface.

**So the footprint is a genuine universal drop-in** for every ST LSM6D\*, every TDK ICM-426xx/IIM,
the 456xx/56xx-generation TDK parts, and the BMI270 — **no schematic change needed.**

### BUG found in IMU sheet (2026-06-03) — CS pull-up dead
R49 (10k CS pull-up) top end is on net **`+3V3`**, a **dangling single-node net** (only R49.2).
The real rail is **`+3.3V`** (45 nodes). So the CS pull-up is **not connected to any supply →
CS floats** when GPIO14 is high-Z (boot/reset). On these IMUs CS state at power-up selects the
interface (high = SPI); a floating CS risks wrong-mode bring-up or spurious selection.
**Fix (Stan, schematic): rename `+3V3` → `+3.3V` on R49.2.** [FIXED by Stan 2026-06-03.]

### CRITICAL BUG — USB data lines disconnected (2026-06-03) — [FIXED by Stan 2026-06-03; verified: D+ → R13 → USB1.A6/B6, D− → R12 → USB1.A7/B7, 0 single-node nets remain]
Netlist scan for single-node nets found two more, both USB data:
- MCU-side: `U2.67 USB_DP → Net-(U2-USB_DP) → R13(30R) → /RP2350A/D+` **(dead end)**
- Connector: `USB-C A6/B6 → /RP2350A/D+_C` **(dead end)** — never joined to `/RP2350A/D+`
- Same for D-: `R12(30R) → /RP2350A/D-` vs connector `/RP2350A/D-_C`.

**The 30R series resistor outputs never reach the USB-C connector → USB will not enumerate.**
Likely a regression from Bastian removing the USB TVS/ESD array (per his 2026-06-02 note "given
the removal of TVS… it will fit") — if that part bridged D±↔D±_C, removing it orphaned the
connector-side nets. **Fix (Stan): reconnect `/RP2350A/D+`↔`/RP2350A/D+_C` and
`/RP2350A/D-`↔`/RP2350A/D-_C`** (rename _C nets or place the replacement ESD/bridge). Run ERC.

### Open item
- **ICM-45686/45605 physical orientation:** pin *functions* match (per 56686), but LCSC lists the
  45686 as LGA-14 **3×2.5** vs our 2.5×3 → check body/pin-1 rotation against the footprint before
  committing. (Functional pinout is fine; this is purely a package-outline check.)
- **Keep pin 9 (GPIO15→CLKIN) wired** — revisit the Rev 2 "drop CLKIN" note. Harmless for ST/Bosch
  (INT2, idle), and gives TDK 426xx/456xx sample-clock jitter removal (relevant to the noise work).

## 9. Datasheet index

| File | Part | Class | BF driver |
|---|---|---|---|
| `datasheets/ICM-42688-P.pdf` | TDK ICM-42688-P | consumer flagship | ✓ |
| `datasheets/IIM-42652.pdf` | TDK IIM-42652 | industrial-temp 426xx | ✓ |
| `datasheets/ICM-56686.pdf` | TDK ICM-56686 | AR/VR-OIS (29.3kHz MEMS) | ✗ (RPi adding) |
| `datasheets/BMI270.pdf` | Bosch BMI270 | consumer/wearable | ✓ |
| `datasheets/BMI088.pdf` | Bosch BMI088 | drone/robotics high-vib | ✗ |
| `datasheets/LSM6DSV16X.pdf` | ST LSM6DSV16X | consumer/OIS (Rev 1 part) | ✓ |
| `datasheets/LSM6DSK320X_rev0.1.pdf` | ST LSM6DSK320X | high-end dual-accel | ✓ |

**Still to collect:** ICM-42622P, ICM-42605, ICM-45686, ICM-45605, LSM6DSO datasheets.
