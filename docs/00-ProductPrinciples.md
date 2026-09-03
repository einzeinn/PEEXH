# 00 — Product Principles

## Core Statement

PEEXH helps a person communicate their intended message without requiring them to change how they speak.

> **The user should not have to adapt to the technology. The technology should adapt to the user.**

## Principles

### 1. User Intent Is Sacred
PEEXH may interpret, suggest, and rank possibilities, but the user's confirmed intent is the final truth.

### 2. Confidence Must Affect Behavior
PEEXH must behave differently when it is confident, uncertain, or confused.

- High confidence → one best interpretation + quick confirmation.
- Medium confidence → show 2–3 candidates.
- Low confidence → do not guess; ask the user to repeat.

### 3. Failure Must Be Recoverable
A low-confidence first attempt is not a failed interaction.

A successful interaction may be:

```text
Attempt 1 → Low confidence
Attempt 2 → Medium confidence
User selects candidate
→ Success
```

### 4. Personalization Over Generalization
PEEXH does not need to understand every speaker equally well.

Its strongest value is learning how to better understand **one user** through:
- corrections;
- recurring phrases;
- contextual associations;
- preferences.

### 5. Accessibility Is Product Logic
Accessibility is not a final design pass.

Core choices such as tap-to-talk, large controls, clear states, minimal navigation, readable results, and user-controlled output are product requirements.

### 6. Minimal Surface Area
V1 solves one problem:

> A person knows what they want to say, but their speech is difficult for another person or ordinary STT to understand.

Anything outside that problem is secondary.

### 7. No Medical Overclaiming
PEEXH is a communication accessibility tool.

It does not:
- diagnose dysarthria;
- measure disease severity;
- provide treatment;
- replace speech-language therapy;
- claim to be an emergency-response system.

### 8. Explainable Agent Behavior
The agent should have a small, understandable action set:
- `PROPOSE_PHRASE`
- `SHOW_CANDIDATES`
- `REQUEST_REPEAT`
- `COMMUNICATE`
- `LEARN_CORRECTION`

### 9. Privacy by Restraint
Store only what improves the user experience.

Avoid retaining unnecessary raw audio by default.

### 10. Demoability Matters
PEEXH is built under hackathon constraints.

A core feature should be explainable and visible inside a demo under three minutes.
