# PEEXH Evaluation Report

**Generated:** 2026-09-10T17:52:16.515823+00:00  
**Dataset:** 32 samples  
**Execution Mode:** mock  

---

## 1. Executive Summary

| Metric | Baseline (Raw STT) | PEEXH Agent Stack | Relative Change / Value |
|---|---|---|---|
| **Average Word Error Rate (WER)** | 93.8% | 35.7% | **+62.0%** |
| **Intent Match Rate (IMR)** | — | 62.5% | Target: ≥ 60.0% |
| **Average Pipeline Latency** | — | 0.0 ms | Target: < 200 ms (mock) |
| **Memory Loop Delta (Pass 1 → 2)** | — | +35.7% | Improvement on repeated utterance |

---

## 2. Per-Sample Detailed Benchmark

| Sample ID | Raw STT Transcript | Intended Target Phrase | PEEXH Proposal | Action | Base WER | PEEXH WER | IMR | Latency |
|---|---|---|---|---|---|---|---|---|
| `SAMPLE-001` | *"i ned wtr"* | **"I need some water"** | "I need some water" | `PROPOSE_PHRASE` | 75% | 0% | ✅ | 0.1ms |
| `SAMPLE-002` | *"wtr plez"* | **"I need some water"** | "I need some water" | `PROPOSE_PHRASE` | 100% | 0% | ✅ | 0.0ms |
| `SAMPLE-003` | *"ple cal hel"* | **"Can you help me please?"** | "Can you help me please?" | `PROPOSE_PHRASE` | 100% | 0% | ✅ | 0.0ms |
| `SAMPLE-004` | *"hlp me"* | **"Can you help me please?"** | "Can you help me please?" | `PROPOSE_PHRASE` | 80% | 0% | ✅ | 0.0ms |
| `SAMPLE-005` | *"lot ov pan"* | **"I am in pain"** | "I am in pain" | `PROPOSE_PHRASE` | 100% | 0% | ✅ | 0.0ms |
| `SAMPLE-006` | *"hurts so bad"* | **"I am in pain"** | "I am in pain" | `PROPOSE_PHRASE` | 100% | 0% | ✅ | 0.0ms |
| `SAMPLE-007` | *"am hungri"* | **"I am hungry"** | "I am hungry" | `PROPOSE_PHRASE` | 67% | 0% | ✅ | 0.0ms |
| `SAMPLE-008` | *"wan sum fud"* | **"I am hungry"** | "Wan sum fud." | `SHOW_CANDIDATES` | 100% | 100% | ❌ | 0.0ms |
| `SAMPLE-009` | *"so tyrd"* | **"I am feeling tired"** | "I am feeling tired" | `PROPOSE_PHRASE` | 100% | 0% | ✅ | 0.0ms |
| `SAMPLE-010` | *"wan rest now"* | **"I am feeling tired"** | "I am feeling tired" | `SHOW_CANDIDATES` | 100% | 0% | ✅ | 0.0ms |
| `SAMPLE-011` | *"ned bathrm"* | **"I need the bathroom"** | "I need the bathroom" | `PROPOSE_PHRASE` | 100% | 0% | ✅ | 0.0ms |
| `SAMPLE-012` | *"go to toylt"* | **"I need the bathroom"** | "Go to toylt." | `SHOW_CANDIDATES` | 100% | 100% | ❌ | 0.0ms |
| `SAMPLE-013` | *"tak medsn"* | **"Time for my medicine"** | "Time for my medicine" | `PROPOSE_PHRASE` | 100% | 0% | ✅ | 0.0ms |
| `SAMPLE-014` | *"wer iz pil"* | **"Time for my medicine"** | "Wer iz pil." | `SHOW_CANDIDATES` | 100% | 100% | ❌ | 0.0ms |
| `SAMPLE-015` | *"feelin ver kold"* | **"I am feeling cold"** | "I am feeling cold" | `PROPOSE_PHRASE` | 100% | 0% | ✅ | 0.0ms |
| `SAMPLE-016` | *"blan-kit plez"* | **"I am feeling cold"** | "Blan-kit plez." | `SHOW_CANDIDATES` | 100% | 100% | ❌ | 0.0ms |
| `SAMPLE-017` | *"tu hot her"* | **"It is too hot here"** | "It is too hot here" | `PROPOSE_PHRASE` | 80% | 0% | ✅ | 0.0ms |
| `SAMPLE-018` | *"turn of fan"* | **"It is too hot here"** | "Turn of fan." | `SHOW_CANDIDATES` | 100% | 100% | ❌ | 0.0ms |
| `SAMPLE-019` | *"ye thnk yu"* | **"Yes thank you"** | "Yes thank you" | `PROPOSE_PHRASE` | 100% | 0% | ✅ | 0.0ms |
| `SAMPLE-020` | *"no nt now"* | **"No not right now"** | "No not right now" | `PROPOSE_PHRASE` | 50% | 0% | ✅ | 0.0ms |
| `SAMPLE-021` | *"cal doc-tr"* | **"Please call the doctor"** | "Please call the doctor" | `PROPOSE_PHRASE` | 100% | 0% | ✅ | 0.0ms |
| `SAMPLE-022` | *"ned doctur"* | **"Please call the doctor"** | "Ned doctur." | `SHOW_CANDIDATES` | 100% | 100% | ❌ | 0.0ms |
| `SAMPLE-023` | *"gud morn-in"* | **"Good morning"** | "Good morning" | `PROPOSE_PHRASE` | 150% | 0% | ✅ | 0.0ms |
| `SAMPLE-024` | *"gud nyt"* | **"Good night"** | "Good night" | `PROPOSE_PHRASE` | 100% | 0% | ✅ | 0.0ms |
| `SAMPLE-025` | *"opn win-do"* | **"Please open the window"** | "Opn win-do." | `SHOW_CANDIDATES` | 100% | 100% | ❌ | 0.0ms |
| `SAMPLE-026` | *"clos dor ple"* | **"Please close the door"** | "Clos dor ple." | `SHOW_CANDIDATES` | 100% | 100% | ❌ | 0.0ms |
| `SAMPLE-027` | *"cant breath wel"* | **"I am having trouble breathing"** | "Cant breath wel." | `SHOW_CANDIDATES` | 100% | 100% | ❌ | 0.0ms |
| `SAMPLE-028` | *"sit up plez"* | **"I want to sit up please"** | "Sit up plez." | `SHOW_CANDIDATES` | 67% | 67% | ❌ | 0.0ms |
| `SAMPLE-029` | *"lie down"* | **"I want to lie down"** | "I want to lie down" | `PROPOSE_PHRASE` | 60% | 0% | ✅ | 0.0ms |
| `SAMPLE-030` | *"wer my glasz"* | **"Where are my glasses?"** | "Wer my glasz." | `SHOW_CANDIDATES` | 75% | 75% | ❌ | 0.0ms |
| `SAMPLE-031` | *"lov yu al"* | **"I love you all"** | "Lov yu al." | `SHOW_CANDIDATES` | 100% | 100% | ❌ | 0.0ms |
| `SAMPLE-032` | *"im o-kay"* | **"I am feeling okay"** | "I am feeling okay" | `PROPOSE_PHRASE` | 100% | 0% | ✅ | 0.0ms |

---

## 3. Memory Loop Personalization (RFC-005 Adaptation)

| Sample ID | Pass 1 WER | Pass 2 WER (Post-Correction) | WER Delta | Memory Match Activated |
|---|---|---|---|---|
| `SAMPLE-001` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-002` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-003` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-004` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-005` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-006` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-007` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-008` | 100% | 0% | **+100%** | ✅ Yes |
| `SAMPLE-009` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-010` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-011` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-012` | 100% | 0% | **+100%** | ✅ Yes |
| `SAMPLE-013` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-014` | 100% | 0% | **+100%** | ✅ Yes |
| `SAMPLE-015` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-016` | 100% | 0% | **+100%** | ✅ Yes |
| `SAMPLE-017` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-018` | 100% | 0% | **+100%** | ✅ Yes |
| `SAMPLE-019` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-020` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-021` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-022` | 100% | 0% | **+100%** | ✅ Yes |
| `SAMPLE-023` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-024` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-025` | 100% | 0% | **+100%** | ✅ Yes |
| `SAMPLE-026` | 100% | 0% | **+100%** | ✅ Yes |
| `SAMPLE-027` | 100% | 0% | **+100%** | ✅ Yes |
| `SAMPLE-028` | 67% | 0% | **+67%** | ✅ Yes |
| `SAMPLE-029` | 0% | 0% | **+0%** | ✅ Yes |
| `SAMPLE-030` | 75% | 0% | **+75%** | ✅ Yes |
| `SAMPLE-031` | 100% | 0% | **+100%** | ✅ Yes |
| `SAMPLE-032` | 0% | 0% | **+0%** | ✅ Yes |

---

## 4. Failure Cases & Edge Condition Analysis

- **SAMPLE-008**: Raw *"wan sum fud"* → Intended: *"I am hungry"*. Action: `SHOW_CANDIDATES`. (WER: 100%). PEEXH deferred to `SHOW_CANDIDATES` preserving safety.
- **SAMPLE-012**: Raw *"go to toylt"* → Intended: *"I need the bathroom"*. Action: `SHOW_CANDIDATES`. (WER: 100%). PEEXH deferred to `SHOW_CANDIDATES` preserving safety.
- **SAMPLE-014**: Raw *"wer iz pil"* → Intended: *"Time for my medicine"*. Action: `SHOW_CANDIDATES`. (WER: 100%). PEEXH deferred to `SHOW_CANDIDATES` preserving safety.
- **SAMPLE-016**: Raw *"blan-kit plez"* → Intended: *"I am feeling cold"*. Action: `SHOW_CANDIDATES`. (WER: 100%). PEEXH deferred to `SHOW_CANDIDATES` preserving safety.
- **SAMPLE-018**: Raw *"turn of fan"* → Intended: *"It is too hot here"*. Action: `SHOW_CANDIDATES`. (WER: 100%). PEEXH deferred to `SHOW_CANDIDATES` preserving safety.
- **SAMPLE-022**: Raw *"ned doctur"* → Intended: *"Please call the doctor"*. Action: `SHOW_CANDIDATES`. (WER: 100%). PEEXH deferred to `SHOW_CANDIDATES` preserving safety.
- **SAMPLE-025**: Raw *"opn win-do"* → Intended: *"Please open the window"*. Action: `SHOW_CANDIDATES`. (WER: 100%). PEEXH deferred to `SHOW_CANDIDATES` preserving safety.
- **SAMPLE-026**: Raw *"clos dor ple"* → Intended: *"Please close the door"*. Action: `SHOW_CANDIDATES`. (WER: 100%). PEEXH deferred to `SHOW_CANDIDATES` preserving safety.
- **SAMPLE-027**: Raw *"cant breath wel"* → Intended: *"I am having trouble breathing"*. Action: `SHOW_CANDIDATES`. (WER: 100%). PEEXH deferred to `SHOW_CANDIDATES` preserving safety.
- **SAMPLE-028**: Raw *"sit up plez"* → Intended: *"I want to sit up please"*. Action: `SHOW_CANDIDATES`. (WER: 67%). PEEXH deferred to `SHOW_CANDIDATES` preserving safety.
- **SAMPLE-030**: Raw *"wer my glasz"* → Intended: *"Where are my glasses?"*. Action: `SHOW_CANDIDATES`. (WER: 75%). PEEXH deferred to `SHOW_CANDIDATES` preserving safety.
- **SAMPLE-031**: Raw *"lov yu al"* → Intended: *"I love you all"*. Action: `SHOW_CANDIDATES`. (WER: 100%). PEEXH deferred to `SHOW_CANDIDATES` preserving safety.
