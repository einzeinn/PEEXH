# 12 — Changelog

All notable project-level changes should be recorded here.

This is not a replacement for Git history or RFCs.

## Unreleased

### Added
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



