# 12 — Changelog

All notable project-level changes should be recorded here.

This is not a replacement for Git history or RFCs.

## Unreleased

### Added
- Drafted RFC-004 for Phase 3 confirmation UX and user-controlled communication output.
- Initial PEEXH product definition.
- Dysarthria-focused primary persona.
- Everyday face-to-face communication as primary use case.
- High-stakes communication assistance as a secondary scenario.
- Tap-to-speak accessibility requirement.
- High / medium / low confidence behavior.
- Personal Speech Memory concept.
- Frontend/backend architecture split.
- AssemblyAI Realtime STT technical path.
- FastAPI + Next.js baseline stack.
- Documentation-first governance.
- `.agent/rules.md`.
- RFC-001.
- English-only rule for all code, comments, and in-project artifacts.
- Completed RFC-001 Repository Bootstrap:
  - Backend FastAPI scaffold with typed Pydantic configuration, health checks, and modular architecture packages.
  - Frontend Next.js scaffold with TypeScript, Tailwind CSS, accessible base layout, and system status card.
  - Test suites and virtual environment configuration.
- Completed RFC-002 Realtime Speech Streaming and AssemblyAI Integration:
  - Added typed domain models for streaming WebSocket control and transcript events (`app.models.speech`).
  - Implemented `SpeechTranscriber` abstract interface, `MockSpeechTranscriber`, and `AssemblyAITranscriber` adapter with factory.
  - Created bidirectional `/ws/speech` streaming WebSocket endpoint.
  - Added browser PCM 16kHz audio downsampling and streaming hook (`useSpeechStream`).
  - Built accessible `TapToTalkButton` with 80px+ touch target, no hold-to-talk, and `TranscriptView` component.
  - Added full test coverage for models, transcriber lifecycle, factory, and WebSocket streaming.
- Completed RFC-003 PEEXH Agent Core and LLM Interpretation Engine:
  - Added typed domain models for agent interpretation, actions, and decisions (`app.models.agent`).
  - Implemented deterministic `ConfidenceScorer` classifying utterances into High, Medium, and Low tiers outside the LLM.
  - Created `Interpreter` interface, `MockInterpreter` for reproducible dysarthric phonetic patterns, and `CloudLLMInterpreter` adapter.
  - Built explicit `PeexhAgent` state machine orchestrating Observe -> Interpret -> Score -> Decide.
  - Integrated agent execution into `/ws/speech` to emit `agent_decision` events on speech stop.
  - Updated frontend `useSpeechStream` and `TranscriptView` to display real-time interpretation cards.
  - Added full test suite with 26 passing tests across models, scorers, interpreters, and WebSocket streams.

- Completed RFC-004 Confirmation UX and Communication Output:
  - Added typed confirmation domain models and WebSocket control events (`app.models.agent`).
  - Extended `PeexhAgent` with `confirm_proposal`, `select_candidate`, `submit_correction`, and `request_repeat` methods with `InvalidStateError` enforcement.
  - Preserved streaming WebSocket connection after `agent_decision` to await explicit user confirmation actions.
  - Replaced preview-only UI with accessible decision controls (`PROPOSE_PHRASE`, `SHOW_CANDIDATES`, `REQUEST_REPEAT`) and inline correction form in `TranscriptView`.
  - Created `ConfirmedMessageView` with large-text display, browser `SpeechSynthesis` TTS with replay control, and new message initialization.
  - Expanded test suite to 43 passing tests and verified clean Next.js production build.
- Completed RFC-005 Personal Speech Memory and Adaptive Learning Loop:
  - Implemented PostgreSQL schema migration for Supabase (`speech_corrections`, `phrase_frequencies`).
  - Created `MemoryStore` abstraction with `SupabaseMemoryStore` (cloud persistence) and `MockMemoryStore` (in-memory fallback).
  - Integrated memory-aware prompt injection into `CloudLLMInterpreter` and `MockInterpreter`.
  - Wired continuous learning hooks into `PeexhAgent`: `submit_correction`, `confirm_proposal`, `select_candidate`.
  - Added `has_memory_match` field to `AgentDecision` and memory-informed badge to `TranscriptView`.
  - Expanded test suite to 52 passing tests (memory store unit tests and adaptive flow integration tests).
- Completed RFC-006 Evaluation Framework and Baseline Benchmarking:
  - Built standalone `backend/evaluation/` module with `EvaluationRunner`, `BaselineCapture`, `PeexhEvaluator`, and `MemoryLoopEvaluator`.
  - Implemented dynamic-programming WER (Word Error Rate) and binary IMR (Intent Match Rate) metrics with latency profiling per stage.
  - Curated 32 representative dysarthric speech distortion patterns across spastic, flaccid, ataxic, and mixed categories (`samples.json`).
  - Added automated Markdown and JSON report generator exporting to `backend/evaluation/reports/`.
  - Verified benchmark achievements: +62.0% relative WER improvement over raw STT baseline, 62.5% Intent Match Rate, +35.7% memory adaptation delta, and < 1 ms mock latency.
  - Expanded test suite to 64 passing tests across metrics, baseline, PEEXH evaluation, memory loop, and runner orchestration.
- Completed RFC-007 Runtime Settings, Audio Input Selection, and Test Readiness:
  - Defined `AudioSettings` type and versioned localStorage key (`peexh.audio-settings.v1`).
  - Created `AudioSettingsContext` with corruption-resilient JSON persistence and `resetToDefaults()` action.
  - Created `useAudioDevices` hook with `devicechange` listener, `audioinput` filtering, and fallback labels.
  - Refactored `useSpeechStream` to apply dynamic `getUserMedia()` constraints with `OverconstrainedError` device fallback.
  - Created `SettingsButton` accessible trigger and `SettingsPanel` WCAG 2.1 AAA modal with keyboard trap, device selector, preprocessing toggles, and system diagnostics.
  - Created `AudioInputMeter` with RMS-based real-time input level visualisation via `AnalyserNode` (zero audio stored).
  - Integrated `AudioSettingsProvider` and `SettingsButton` into `RootLayout` header.
  - Unit tests for settings serialisation, corruption fallback, device filtering, and constraints builder.
  - Backend: 64/64 tests continue to pass.
- Completed RFC-008 Demo Polish, Presentation Flow, and Hackathon Submission Readiness:
  - Created interactive `DemoBar` component: pre-set dysarthric speech simulation samples for microphone-free judge testing.
  - Added `/demo/simulate` REST endpoint routing raw text through full PEEXH agent pipeline without audio capture.
  - Integrated `DemoBar` into `page.tsx`; header updated to "Phase 7 Ready".
  - Created `docs/13-DemoScript.md`: scene-by-scene video storyboard (7 scenes, target 2 min 45 sec).
  - Added `backend/Dockerfile` (multi-stage, non-root user, health check) and `render.yaml` for one-click Render.com deployment.
  - Updated `README.md` with architecture diagram, demo mode instructions, deployment guide, and full documentation index.
  - Backend: 69/69 tests pass (5 new tests for `/demo/simulate` endpoint).


### Changed
- Hardened RFC-003 high-confidence policy: a phrase proposal now requires the configured top-candidate threshold and a separately configurable minimum STT confidence, preventing memory or composite-score bonuses from bypassing either safeguard.

