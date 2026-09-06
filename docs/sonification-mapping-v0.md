# Halcytone — Sonification Mapping v0 (draft for the owner to strike)

> Status: DRAFT 2026-09-06. Every line below is a proposal. Strike what is
> wrong, change numbers freely, and the survivors become `halcytone.audio`'s
> spec and `halcytone.hud`'s legend. Nothing here is implemented.
>
> The thesis: **the sonification of current self.** Every parameter is
> relative to this session's 60-second baseline, never to a population. The
> sound is what the body is doing now, against what it was doing a minute
> ago, and over weeks, against what it did last month.

## 0. Principles (strike any and the rest re-derive)

1. **Baseline-relative, always.** Every input is a z-score against the session
   baseline (mean, sd from the 60 s capture), clipped to [-3, 3], then mapped.
   Absolute units never reach the synth.
2. **Monotone, stated, reversible.** Each mapping is one formula in one
   direction. A listener who learns the mapping can hear the number.
3. **Settling is rewarded by simplification, not by adding.** As the body
   settles, the sound gets simpler, wider, and more consonant. Nothing gets
   louder or busier as a reward. Arousal is what adds.
4. **The sound never punishes.** No alarm tones, no descending "fail" motifs.
   A rule break (mouth breathing, motion) changes the room, not the music.
5. **Pure function of the state log.** `audio(state.jsonl, seed) → wav` is
   deterministic. Live and offline renders are byte-identical, so
   `halcytone.publish` re-renders instead of recording, and any session can
   be re-sonified under a later mapping version.
6. **Quality-gated.** When a modality's quality drops below 0.5, its
   parameters hold their last good value and a faint haze appears in that
   register. The HUD shows the hold. The music does not lie about data it
   does not have.
7. **Tempo-free.** No grid, no metronome. The only periodic element is the
   heart, and it recedes.

## 1. The substrate

- **Key:** one fixed root per session, D2 (73.4 Hz) by default; the root is
  the session's constant. (Alternative to rule on: root chosen from the
  baseline heart rate, e.g. HR/60 mapped onto a pentatonic degree, so every
  session starts "in the key of today.")
- **Tuning:** just intonation from the root. Consonance is an interval
  choice, not an effect: unison → 3:2 → 5:4 → 9:8 → 16:15 → semitone cluster
  is the consonant-to-tense ladder used below.
- **Three layers, always present, never more:**
  - **Drone** — a low sustained pad on the root. The floor.
  - **Breath voice** — a mid pad whose amplitude and filter follow breath
    phase. The anchor the listener locks to.
  - **Event layer** — short synthetic bells or plucks. Only fires on events
    (EDA phasic, motion, rule breaks). Silent by default.
- **Space:** one reverb whose size and width are driven by presence. The
  room is the composite score. You hear how much room you have made.
- **Synthesis only.** No samples. Sine, triangle, filtered noise, simple FM.
  Reproducibility beats richness.

## 2. Signal → parameter table

`z(x)` = clipped baseline z-score of `x`. Time constant `τ` is the smoothing
applied to the mapped parameter (one-pole), not to the raw signal. "Hold" is
the quality fallback.

| State field | Perceptual parameter | Mapping (proposal) | Range | τ | Latency budget | Notes |
|---|---|---|---|---|---|---|
| `breath_phase` (0→1) | Breath-voice amplitude + filter cutoff | amp = 0.3 + 0.7·(1−cos(2π·phase))/2 ; cutoff = 300 Hz · 2^(2·amp) | swell on inhale, fall on exhale | 0 (direct) | ≤ 50 ms | The anchor. Phase from nasal pressure, so this is the tightest loop in the system. |
| `breath_rate` (bpm) | Grain density of a texture on the breath voice | density = 0 grains/s at ≤ 6 bpm, rising linearly to 12 grains/s at 20 bpm | sparse when slow | 4 s | — | At resonance breathing (~5–6 bpm) the texture vanishes: the voice becomes one clean tone. Reward by simplification (principle 3). |
| `breath_depth` (baseline-rel.) | Stereo width of the breath voice | width = 0.2 + 0.6·sigmoid(z) | narrow shallow → wide deep | 2 s | — | Depth is relative-only on a cannula; that is fine here. |
| `heart_rate` (bpm) | A soft low pulse at the heart's own rate | one low thump per beat, 60 Hz sine burst, 80 ms | audible in baseline, fades | — | beat-locked | Amplitude = 0.4·(1−presence). The heart is loud when you arrive and recedes as you settle. Never a kick drum. |
| `hrv_rmssd` (baseline-rel.) | Interval of the drone's second voice | z ≤ −1 → semitone cluster; −1..0 → 16:15; 0..1 → 9:8 → 5:4; ≥ 1 → 3:2; ≥ 2 → unison | tense → consonant | 10 s | (30 s window inherent) | The main "how am I doing" channel. HRV up = the chord opens. |
| `heart_breath_coherence` (0→1) | A third voice fades in, tuned to the breath voice | amp₃ = coherence² ; interval = 3:2 above the breath voice | absent → present | 5 s | — | The lock reward: when heart and breath phase-lock, a fifth appears above the breath. Squared so it only speaks when real. |
| `eda_level` (tonic, baseline-rel.) | Spectral tilt / brightness of everything | tilt = −6 dB/oct at z = −2 → 0 at z = 0 → +6 dB/oct at z = +2 | dark/warm calm → bright/hard aroused | 8 s | — | Arousal is brightness. Calm is warmth. |
| `eda_phasic` | Event layer: one bell per phasic peak | pitch = 4× breath-voice fundamental; amp = min(1, phasic/baseline_sd) ; decay 1.5 s ; rate-limited 1 per 2 s | silent → sparse bells | — | ≤ 200 ms | You hear your startle. Not a penalty; a mark. |
| `eeg_alpha` (0→1, baseline-rel.) | Fullness of a shimmer above the drone (octave + 12th, low-passed) | shimmer cutoff = 200 Hz · 2^(3·sigmoid(z)) | closed → open | 3 s | (2–4 s band window inherent) | Alpha up = the top opens. The "eyes-closed calm" signature. |
| `eeg_theta` | Slow chorus depth on the breath voice | depth = 0.02 + 0.10·sigmoid(z), rate 0.1 Hz | dry → dreamy | 4 s | — | Drift, not wobble. |
| `eeg_beta` | Noise floor on the drone (filtered pink noise) | noise = −40 dB at z ≤ −1 → −18 dB at z = +2 | quiet → hissing | 3 s | — | Busy mind = busy floor. The thing meditation reduces, made audible. |
| `eeg_delta` | NOT MAPPED | — | — | — | — | In waking sessions delta is mostly artifact on a Ganglion. Recorded only. (Strike if you want drowsiness audible.) |
| `eeg_gamma` | NOT MAPPED | — | — | — | — | EMG-contaminated on dry electrodes. Recorded only. |
| `skin_temp` (baseline-rel.) | Global saturation (soft clip drive) over minutes | drive = 0 at z ≤ 0 → 0.3 at z = +2 | clean → warm | 60 s | — | Peripheral warming is a slow relaxation sign; the whole sound warms with it. |
| `imu.accel` magnitude (motion) | Reverb dries; a short rustle | reverb size × (1 − motion_norm) ; rustle amp = motion_norm | spacious still → dry fidget | 0.5 s | ≤ 100 ms | Stillness is the room. Fidgeting collapses it. No tone, just space. |
| `overall_presence` (0→1) | Master: reverb size, width, voice count | size = 0.2 + 0.7·presence ; width = 0.3 + 0.6·presence ; heart amp = 0.4·(1−presence) | small/close → vast/open | 6 s | — | The composite you can hear as a room. Formula proposed in §3. |
| `*_quality` < 0.5 | Hold + haze | that modality's parameters freeze; band-limited noise at −36 dB in that modality's register | — | — | — | Principle 6. HUD shows a hold badge on the modality. |

## 3. `overall_presence` — a proposed formula (currently undefined in the contract)

```
presence = clip( 0.30·coherence
               + 0.25·sigmoid(z(alpha) − z(beta))       # calm-over-busy
               + 0.20·resonance                          # 1 at 5.5 bpm, 0 at ≥ 12 bpm, linear
               + 0.15·(1 − motion_norm)                  # stillness
               + 0.10·(1 − phasic_rate_norm)             # few startles
               , 0, 1 )
```

- Computed in core, smoothed τ = 6 s, logged per tick.
- Weights are the first thing to strike. Coherence leads because it is the
  only composite that needs two modalities to agree.
- `resonance` rewards slow breathing without prescribing it: at 5.5 bpm the
  texture layer is already silent (§2), so presence and the texture agree.

## 4. Protocol states → what the sound does

| State | Sound |
|---|---|
| **Preflight** | Silence. As each sensor's stream appears, one soft tone in its register (breath: mid, heart: low, EEG: high). Missing sensor = missing tone; you hear the roster. |
| **Baseline (60 s)** | Drone + breath voice + heart pulse only. No composites, no consonance mapping, no events. Nothing evaluative can sound before there is a baseline to evaluate against. A single soft chime marks the end of baseline. |
| **Active** | Everything in §2. |
| **Mouth breathing** (pressure flow ≈ 0 while chest motion or heart continues) | The breath voice stops swelling and HOLDS at its last level; the room dries by half; no tone. First full nasal cycle restores it. No penalty (principle 4); the missing anchor is the cue. |
| **Motion burst** (accel above threshold > 1 s) | Reverb collapses, rustle sounds; presence pauses (holds) rather than dropping, so a scratch does not read as a relapse. |
| **Quality hold** | See §2 last row. |
| **Teardown** | The second voice resolves to the session's final consonance interval and the whole sound decays over 10 s into the reverb tail. The last chord is the session's signature (§6). |

## 5. Latency and smoothing budget

| Path | Budget | Why |
|---|---|---|
| Nasal pressure → breath voice amplitude | ≤ 50 ms | The anchor must feel simultaneous. |
| EDA phasic → bell | ≤ 200 ms | A startle heard late reads as unrelated. |
| Motion → room dries | ≤ 100 ms | Same. |
| EEG bands → any parameter | 2–4 s inherent (band window) + τ | Accept the lag; never fake it with a shorter window. |
| HRV → interval | 30 s inherent + 10 s τ | Interval changes are steps; the τ makes them glides. |
| Presence → room | 6 s τ | The room should feel like weather, not a meter. |

## 6. Longitudinal (the daily arc)

- Each session ends with a **signature**: final consonance interval, final
  presence, mean breath rate, mean coherence. Stored in `state_summaries`.
- The daily video's HUD shows today's presence curve against the **30-day
  envelope** (10th–90th percentile band of prior sessions at the same
  minute-mark). That band is the "current self against recent self" picture.
- Proposal to rule on: the drone's root walks one scale degree per week
  across a five-week pentatonic cycle, so a month of sessions is a melody.
  (Strike if a fixed root matters more for comparability.)
- No cross-person comparison exists anywhere in the design.

## 7. What the HUD must show (the pipeline displayed)

For every mapped row in §2: raw signal trace (last 30 s), baseline band,
current z, the mapped parameter's current value, and the arrow between
them. Quality badge per modality. Protocol state. Presence as the room:
drawn as an expanding/contracting frame around everything else. The mapping
version string on screen at all times.

## 8. Deliberately not mapped

- `heart_rate` → pitch. Heart as melody is a cliché and reads as anxiety.
- `eeg_delta`, `eeg_gamma`: artifact-dominated on this hardware.
- Absolute breath volume: not measurable on a cannula; not needed.
- Any spoken or voiced element. The sound is the body, not a guide.
- Any "score" tone, chime, or level-up. The room is the score.

## 9. Open rulings

1. Root: fixed D2, or "key of today" from baseline HR?
2. Presence weights (§3).
3. Consonance ladder (§2 `hrv_rmssd`): agree with unison as the top, or is
   the fifth the ceiling and unison too static?
4. Heart pulse: keep, or drop it entirely and let HRV alone carry the heart?
5. Weekly root walk (§6): yes or no?
6. Mouth-breath response: hold-and-dry as proposed, or full silence?
7. Session length target for the daily video (10, 15, 20 min?) — sets how
   much of the arc the HUD compresses.

## 10. Contract changes this implies (0.x, breaking allowed)

- Reserved streams: add `breath.pressure` (raw nasal pressure, 100 Hz);
  drop `breath.acoustic` and `breath.envelope`; keep `breath.rate`,
  `breath.phase`, `breath.depth` as derived from pressure.
- `StateVector`: add `protocol_state` (preflight | baseline | active |
  mouth | motion | teardown) and `mapping_version`.
- `SessionSummary`: add the signature fields from §6.
- New `MappingSpec` document type: this file, machine-readable, versioned,
  referenced by `manifest.yaml`, so every session names the mapping it was
  heard under.
