# 08 — Design

## Design Goal

The interface should make communication easier, not create another task for the user.

## Core Interaction

Primary interaction:

```text
Tap Speak
  ↓
Listening
  ↓
Tap Stop / automatic turn end
  ↓
Interpretation
  ↓
Confirm / choose / repeat
  ↓
Communicate
```

## Why Tap Instead of Hold

Hold-to-talk may create unnecessary physical burden for users with motor limitations.

V1 uses:
- one tap to start;
- one tap to stop;
- optional automatic turn detection if reliable.

## Primary Screen

The main screen should prioritize:
1. one large speak control;
2. current system state;
3. current interpretation;
4. clear confirmation actions.

Avoid dense navigation.

## Required States

- Idle
- Listening
- Transcribing
- Interpreting
- High-confidence confirmation
- Medium-confidence candidates
- Low-confidence repeat
- Confirmed / ready to communicate
- Correction mode
- Error / recovery

## Candidate UX

### High Confidence
Show one phrase prominently.

Actions:
- Confirm
- Correct

### Medium Confidence
Show 2–3 large candidate buttons.

Actions:
- Select candidate
- Correct manually
- Repeat

### Low Confidence
Clearly state that PEEXH is not sure.

Primary action:
- Speak again

Secondary:
- manually enter intended phrase if appropriate.

## Communication Output

After confirmation:
- display large text;
- optionally speak using TTS;
- offer a clear replay button if TTS is enabled.

## Accessibility Requirements

- large tap targets;
- minimum cognitive load;
- high contrast;
- readable typography;
- visible focus;
- keyboard navigation;
- no hover-only controls;
- no tiny icon-only primary actions;
- text labels for important controls;
- clear progress/state feedback;
- no required long press;
- errors written in plain language.

## Design Tone

Avoid a clinical or hospital-heavy appearance.

PEEXH should feel:
- calm;
- respectful;
- simple;
- contemporary;
- human;
- not childish;
- not overly medical.

## Branding Direction

Preferred product styling:
- lowercase wordmark: `peexh`
- clean, quiet visual system;
- accessible contrast;
- branding should not compete with communication content.

Potential line:
> **Be understood.**
