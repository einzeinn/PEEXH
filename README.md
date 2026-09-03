# PEEXH

**PEEXH** is a voice-first communication aid for people with dysarthria who can speak but are often difficult to understand by other people or conventional speech-recognition systems.

PEEXH listens to speech, interprets the most likely intended phrase, asks the user to confirm or correct it, and then communicates the confirmed message as readable text and/or speech.

> **LLM interprets. PEEXH decides. User controls.**

## Core Product Loop

```text
Speak
  ↓
AssemblyAI Realtime STT
  ↓
PEEXH Interpretation
  ↓
Confidence Decision
  ├─ High   → Quick confirmation
  ├─ Medium → Candidate phrases
  └─ Low    → Ask user to repeat
  ↓
User confirmation / correction
  ↓
Text and/or TTS
  ↓
Personal Speech Memory improves future attempts
```

## Primary User

People with dysarthria who:
- are still able to produce speech;
- know what they intend to say;
- are frequently misunderstood by listeners or ordinary STT systems.

PEEXH V1 is **not** a diagnostic tool, speech-therapy system, medical-monitoring product, or complete AAC platform.

## Primary Use Case

Face-to-face everyday communication.

PEEXH may also assist in high-stakes situations, such as when a user is already on a phone call and needs help making their speech understandable. PEEXH V1 does **not** place emergency calls, detect emergencies, transmit location, or contact emergency services.

## Hackathon Scope

Built for the AssemblyAI Voice Agent Hackathon using the **Realtime Speech-to-Text API** path.

Internal demo target: **under 3 minutes**.

## Repository Layout

```text
peexh/
├── .agent/
│   └── rules.md
├── docs/
├── frontend/
├── backend/
├── assets/
├── prototype/
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

See `docs/` for product, architecture, technical decisions, roadmap, research, and governance.
