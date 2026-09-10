# 09 — Roadmap

## Phase 0 — Product Lock

Status: complete / near-complete.

- product name;
- target persona;
- use case;
- agent behavior;
- confidence policy;
- memory definition;
- MVP boundaries;
- demo concept;
- architecture;
- tech stack.

## Phase 1 — Speech Foundation

Goal: live audio reaches AssemblyAI and returns realtime transcript.

Deliverables:
- frontend microphone interaction;
- backend WebSocket path;
- AssemblyAI adapter;
- transcript events;
- basic connection/error handling.

## Phase 2 — Agent MVP

Goal: transcript becomes candidate intent.

Deliverables:
- state machine;
- interpreter abstraction;
- structured LLM candidate output;
- deterministic confidence policy;
- high/medium/low flows.

## Phase 3 — Confirmation UX

Goal: user retains control over final message.

Deliverables:
- high-confidence confirmation;
- candidate selection;
- repeat flow;
- correction;
- large-text communication;
- TTS output.

## Phase 4 — Personal Speech Memory

Goal: corrections affect future interpretation.

Deliverables:
- correction-pair storage;
- recurring phrase tracking;
- context associations;
- preferences;
- retrieval;
- similarity matching;
- memory-aware interpretation.

## Phase 5 — Evaluation

Goal: prove PEEXH works beyond one hand-crafted happy path.

Deliverables:
- licensed/public speech samples;
- baseline raw-STT capture;
- PEEXH interpretation comparison;
- repeated-attempt tests;
- personalization tests;
- latency notes;
- failure examples.

## Phase 6 — Runtime Settings & Test Readiness

Goal: Give users and developers explicit control over browser audio input and audio preprocessing so PEEXH can be tested reliably across microphones, loopback devices, Stereo Mix, virtual audio cables, and other browser-visible input devices.

Deliverables:
- audio input device selection;
- browser-visible microphone enumeration;
- persistent local audio settings;
- echo cancellation toggle;
- noise suppression toggle;
- auto gain control toggle;
- microphone permission state;
- audio input diagnostics;
- selected-device diagnostics;
- actual AudioContext sample rate;
- PEEXH target sample rate display;
- backend connectivity diagnostic;
- active speech provider diagnostic when available;
- accessible settings UI;
- graceful fallback when browser APIs are unavailable;
- tests and production build verification.

## Phase 7 — Demo Polish

Status: complete.

Goal: sub-3-minute clear submission.

Deliverables:
- stable public deployment (Dockerfile + render.yaml);
- interactive demo mode (DemoBar — no microphone required);
- /demo/simulate REST endpoint for microphone-free backend testing;
- demo dataset (4 pre-set dysarthric speech samples);
- architecture visual in README;
- 13-DemoScript.md scene-by-scene storyboard;
- final UI integration and header update;
- submission assets and deployment documentation.

## Future Scope

Not V1:
- multilingual support;
- native mobile;
- phone-call integration;
- on-device inference;
- broader AAC functions;
- clinician/caregiver features;
- deeper acoustic personalization.
