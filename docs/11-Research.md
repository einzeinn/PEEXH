# 11 — Research

## Research Goal

Validate whether PEEXH can reliably improve communication using real dysarthric speech samples while staying within a narrow hackathon scope.

## R-001 — Speech Sample Sources

Find lawful audio sources containing dysarthric speech with known or inferable intended transcripts.

Preferred:
- research datasets with clear usage terms;
- public-domain samples;
- explicitly reusable educational material;
- samples whose licenses allow demo/research use.

YouTube may be useful for exploration, but ordinary YouTube videos must not be assumed safe to reproduce in a submission recording.

## R-002 — AssemblyAI Baseline

For each sample, record:
- audio source;
- ground-truth/intended phrase if known;
- raw AssemblyAI transcript;
- transcript confidence where available;
- latency;
- obvious recurring errors.

## R-003 — Sweet Spot

PEEXH is most viable when raw STT is imperfect but still contains enough signal for contextual/personalized correction.

Bad extremes:
- raw STT always perfect → PEEXH has little visible value;
- raw STT effectively random → correction layer becomes unreliable.

## R-004 — Personalization Evaluation

Test whether previous corrections improve future related phrases.

Example structure:

```text
Sample A:
Observed transcript → incorrect
User correction → intended phrase stored

Sample B:
Similar speech pattern
Memory retrieved
Candidate ranking improves
```

## R-005 — Recovery Evaluation

Test repeated attempts:

```text
Attempt 1 → Low
Attempt 2 → Medium
User selection → Confirmed
```

A successful system does not require perfect first-pass recognition.

## R-006 — Latency

Measure:
- speech-end to final STT;
- STT to candidates;
- candidates to rendered UI;
- confirmed text to TTS start.

The target is conversational responsiveness, not benchmark theater.

## R-007 — Safety Behavior

Test:
- uncertain transcript;
- multiple plausible meanings;
- misleading context;
- memory suggesting the wrong phrase;
- correction conflicting with memory.

PEEXH should prefer asking the user over confidently inventing intent.

## Research Log Template

```markdown
### Experiment
Date:
Sample:
Source/license:
Expected phrase:

AssemblyAI transcript:
AssemblyAI confidence:
PEEXH candidates:
PEEXH decision:
User confirmation needed:
Memory used:
Latency:
Result:
Notes:
```

---

## Phase 5 Benchmark Findings (RFC-006)

Evaluated on 32 dysarthric phonetic distortion samples across spastic, flaccid, ataxic, and mixed categories (`backend/evaluation/data/samples.json`).

### Summary Metrics

| Metric | Raw STT Baseline | PEEXH Pipeline | Delta / Result | Status |
|---|---|---|---|---|
| **Average Word Error Rate (WER)** | 93.8% | 35.7% | **+62.0% relative improvement** | Target ≥ 10.0% (Passed) |
| **Intent Match Rate (IMR)** | — | 62.5% | Target ≥ 60.0% | Target ≥ 60.0% (Passed) |
| **Average Pipeline Latency** | — | < 1 ms (mock) | Target < 200 ms | Passed |
| **Memory Loop Avg Delta** | — | +35.7% | Measurable improvement on repeat | Passed |

### Key Observations
1. **Phonetic Reduction Recovery**: Severe consonant cluster reduction (e.g., *"i ned wtr"*, *"lot ov pan"*) consistently resolves to grammatical target phrases with 0.0% WER.
2. **Safety Behavior on Ambiguity**: When an utterance does not match known vocabulary (e.g. *"wan sum fud"* or *"wer iz pil"*), PEEXH preserves user safety by falling back to `SHOW_CANDIDATES` rather than fabricating high-confidence intent.
3. **Adaptive Loop Acceleration**: Once a user corrects an unmapped utterance via `submit_correction`, subsequent repetitions of the exact or similar acoustic distortion trigger `has_memory_match=True`, eliminating the initial WER down to 0.0%.

