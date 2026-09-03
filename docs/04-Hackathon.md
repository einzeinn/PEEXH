# 04 — Hackathon

## Event

AssemblyAI Voice Agent Hackathon on lablab.ai.

## Chosen Technical Path

**Realtime Speech-to-Text API**

PEEXH needs direct control over:
- transcript processing;
- interpretation;
- confidence logic;
- personal memory;
- confirmation;
- output.

This makes the realtime STT path a better fit than delegating the complete flow to a generalized voice-agent abstraction.

## Why PEEXH Fits

### Application of Technology
AssemblyAI Realtime STT is a core dependency, not a decorative integration.

The agent cannot operate without realtime speech recognition.

### Presentation
PEEXH is designed around one easy-to-understand flow and an internal demo target under three minutes.

### Business Value
PEEXH targets a clear accessibility need and can potentially expand across communication contexts without changing its core purpose.

### Originality
The key differentiator is not merely speech-to-text.

PEEXH combines:
- realtime transcription;
- personalized correction memory;
- confidence-aware behavior;
- user-controlled communication.

## Demo Target

**Maximum internal target:** < 3 minutes.

Suggested structure:

### 0:00–0:15 — Problem
Explain the communication gap.

### 0:15–0:30 — Product
Introduce PEEXH in one sentence.

### 0:30–1:10 — Core Demo
Speech sample → raw STT → PEEXH interpretation → confirmation → output.

### 1:10–1:50 — Personalization
Show correction, then a related later phrase where memory improves the interpretation.

### 1:50–2:15 — Uncertainty
Show PEEXH refusing to guess and asking for repeat/candidates.

### 2:15–2:35 — Architecture
Briefly show AssemblyAI and the PEEXH agent loop.

### 2:35–2:50 — Closing
End with the confirmed phrase and product identity.

## Demo Setup

Potential split-screen recording:

```text
┌──────────────────────┬──────────────────────┐
│ Speech Sample        │ PEEXH                │
│ Video/audio source   │ Listening            │
│                      │ Raw STT              │
│                      │ Interpretation       │
│                      │ Confirmation         │
└──────────────────────┴──────────────────────┘
```

Use lawful/licensed audio samples.

For technical consistency, system audio may be routed internally during recording. A separate real-world microphone/speaker shot may demonstrate actual acoustic input.

## Demo Principle

The video must show:
1. the problem;
2. why PEEXH exists;
3. why AssemblyAI matters;
4. why personalization matters;
5. how PEEXH behaves safely when uncertain.
