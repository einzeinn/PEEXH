# 02 — Product Requirements Document

## 1. Product

**Name:** PEEXH  
**Category:** Voice accessibility / assistive communication  
**Primary interface:** Web application  
**Primary AI input:** Realtime speech

## 2. Primary User

A person with dysarthria who:
- is still able to speak;
- has a clear intended message;
- is frequently misunderstood by people or conventional speech recognition.

## 3. Primary Problem

The user knows what they want to say, but their spoken output is difficult for another listener or ordinary STT to understand reliably.

## 4. Primary Use Case

Face-to-face everyday communication.

Example:
1. User opens PEEXH.
2. User taps the main speak button.
3. User speaks.
4. PEEXH transcribes and interprets.
5. PEEXH asks for confirmation or offers candidates.
6. User confirms/corrects.
7. PEEXH displays and optionally speaks the confirmed phrase.

## 5. Secondary High-Stakes Use Case

PEEXH may assist while the user is already communicating in a high-stakes situation, such as being on a call with emergency services.

V1 does **not**:
- place emergency calls;
- detect emergencies;
- transmit location;
- contact authorities;
- make emergency decisions.

It only performs the same communication-assistance function.

## 6. Core User Flow

```text
OPEN
  ↓
Tap Speak
  ↓
LISTENING
  ↓
Tap Stop or automatic end-of-turn
  ↓
TRANSCRIBING
  ↓
INTERPRETING
  ↓
DECIDING
  ├─ HIGH confidence
  │    ↓
  │  Show best phrase
  │    ↓
  │  Quick confirm
  │
  ├─ MEDIUM confidence
  │    ↓
  │  Show 2–3 candidates
  │    ↓
  │  User selects or corrects
  │
  └─ LOW confidence
       ↓
     Ask user to repeat
       ↓
     Re-evaluate
  ↓
CONFIRMED
  ↓
Display text / TTS
  ↓
LEARN correction if applicable
```

## 7. Functional Requirements

### FR-001 — Tap-to-Speak
The user can start recording with one tap.

### FR-002 — Tap-to-Stop
The user can stop recording with one tap.

Hold-to-talk is not required.

### FR-003 — Realtime Transcription
AssemblyAI Realtime STT must process the incoming speech stream.

### FR-004 — Interpretation
PEEXH must produce likely intended phrase candidates from:
- transcript;
- recent interaction context;
- relevant personal memory.

### FR-005 — Confidence Decision
PEEXH must classify an interpretation path into:
- high;
- medium;
- low.

### FR-006 — High Confidence Behavior
Show one best candidate and request quick confirmation.

### FR-007 — Medium Confidence Behavior
Show 2–3 candidate phrases.

### FR-008 — Low Confidence Behavior
Do not communicate an unconfirmed interpretation. Ask the user to repeat.

### FR-009 — Correction
The user can correct a proposed phrase.

### FR-010 — Communication Output
After confirmation, PEEXH can:
- show large readable text;
- speak the phrase using TTS;
- do both.

### FR-011 — Personal Speech Memory
PEEXH can use:
- correction pairs;
- recurring phrase patterns;
- contextual associations;
- user preferences.

### FR-012 — Learning From Correction
Confirmed corrections should improve retrieval/ranking for similar future attempts.

## 8. Non-Functional Requirements

### NFR-001 — Accessibility
Primary controls must be large, clear, keyboard accessible, and not require sustained pressure.

### NFR-002 — Low Latency
The interaction should feel conversational, with realtime transcription and fast interpretation.

### NFR-003 — Modularity
Speech, LLM, memory, scoring, and output providers must be replaceable.

### NFR-004 — Configuration
Provider choice, model selection, thresholds, URLs, and feature flags must be configurable through environment variables.

### NFR-005 — User Control
No uncertain phrase may be spoken as the user's final intent without confirmation.

### NFR-006 — Privacy
Avoid retaining raw audio unless clearly required and documented.

## 9. Success Criteria

### Interaction Success
A communication attempt succeeds when PEEXH produces the intended phrase clearly and the user confirms it.

Success may happen after more than one attempt.

### Recovery Success
A low-confidence result can become successful after repeat, candidate selection, or correction.

### Personalization Success
Previously corrected speech patterns should improve interpretation of similar future input.

## 10. Explicitly Out of Scope for V1

- diagnosis;
- therapy;
- disease severity scoring;
- emotion detection;
- emergency detection;
- automatic emergency calling;
- location transmission;
- phone integration;
- translation;
- caregiver dashboard;
- enterprise administration;
- analytics platform;
- full AAC replacement;
- multi-user personalization;
- native mobile app;
- fine-tuning AssemblyAI per user.
