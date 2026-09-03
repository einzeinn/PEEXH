# PEEXH Agent Rules

These rules apply to any coding or documentation agent working inside this repository.

## 1. Read Before Writing

Before changing implementation:
1. Read the relevant documents in `docs/`.
2. Read any RFC that governs the affected area.
3. Confirm that the requested work is inside the current scope.

Do not treat existing implementation as the sole source of truth when documentation defines intended behavior.

## 2. No Autonomous Scope Expansion

Do not add features simply because they appear useful.

Examples of out-of-scope additions unless explicitly approved:
- diagnosis;
- speech therapy;
- emotion detection;
- emergency detection;
- automatic emergency calling;
- translation;
- caregiver dashboards;
- enterprise analytics;
- multi-agent orchestration;
- complex authentication systems;
- unrelated platform features.

If a useful idea is outside current scope, document it as a future consideration instead of implementing it.

## 3. Documentation-First for Meaningful Changes

Before a meaningful change, determine whether documentation or a new RFC must be updated first.

Documentation is required before:
- adding or removing a major feature;
- changing agent behavior or state transitions;
- changing confidence policy;
- changing API contracts;
- changing persistence/data schema;
- introducing a major dependency or framework;
- changing architecture boundaries;
- changing the primary AI provider strategy;
- changing core accessibility behavior;
- changing privacy or safety behavior.

Trivial fixes such as typo corrections, formatting changes, lint fixes, and obviously local bug fixes do not require a new RFC.

## 4. Preserve Architecture Boundaries

Frontend responsibilities:
- accessible interaction;
- microphone/UI state;
- rendering candidates;
- confirmation/correction controls;
- readable output;
- optional TTS controls.

Backend responsibilities:
- AssemblyAI integration;
- PEEXH agent state machine;
- interpretation orchestration;
- confidence scoring;
- personal speech memory;
- persistence;
- provider integrations.

Do not move backend policy into frontend UI code for convenience.

## 5. Keep Providers Replaceable

Core logic must not depend directly on one LLM, database vendor, or TTS provider.

Prefer interfaces such as:
- `Interpreter.generate_candidates(...)`
- `MemoryStore.find_relevant_patterns(...)`
- `SpeechTranscriber.stream(...)`
- `SpeechOutput.speak(...)`

Provider-specific details belong behind adapters.

## 6. Configuration Over Hardcoding

Do not hardcode:
- API keys;
- model identifiers;
- service URLs;
- confidence thresholds;
- feature flags;
- provider selection;
- deployment-specific settings.

Use environment variables and typed configuration.

Never commit secrets.

## 7. Accessibility Is a Core Requirement

Accessibility is not optional polish.

Default expectations:
- tap-to-start / tap-to-stop interaction;
- large primary controls;
- clear state feedback;
- readable typography;
- keyboard accessibility;
- visible focus states;
- sufficient contrast;
- no hold-to-talk requirement;
- user can recover from low-confidence output without navigating complex UI.

## 8. User Intent Is Authoritative

PEEXH may suggest what the user intended.

PEEXH must not silently replace the user's meaning.

Rules:
- user confirmation overrides AI interpretation;
- user correction is authoritative;
- low-confidence interpretations must not be communicated as final intent;
- uncertain outputs require confirmation, candidate selection, or repeat;
- the system must never pretend an interpretation is certain when it is not.

## 9. LLM Interprets, PEEXH Decides

The LLM may:
- interpret transcript fragments;
- produce phrase candidates;
- use context supplied by PEEXH.

The LLM must not directly control:
- confidence policy;
- safety policy;
- final communication state;
- persistence rules;
- whether uncertain output is spoken automatically.

Decision policy should be deterministic wherever practical.

## 10. Personal Memory Must Be Bounded and Explainable

Personal Speech Memory may store:
- correction pairs;
- recurring phrase patterns;
- contextual associations;
- user preferences.

Do not introduce opaque long-term memory behavior without documentation.

Prefer storing derived, minimal, useful information over unnecessary raw data.

## 11. Tests Are Part of Non-Trivial Work

Any meaningful behavior change should include appropriate tests.

Priority:
1. state transitions;
2. confidence policy;
3. correction learning;
4. memory retrieval;
5. API contracts;
6. accessibility-critical UI behavior.

## 12. Do Not Modify Unrelated Modules

Scoped tasks should remain scoped.

If a task touches unrelated areas, stop and document why before expanding the change.

## 13. Prefer Simplicity

Do not introduce:
- LangChain;
- LangGraph;
- agent frameworks;
- message buses;
- microservices;
- distributed systems;
- Kubernetes;
- complex abstractions

unless the project genuinely needs them and a technical decision/RFC approves them.

PEEXH V1 should remain understandable by one developer reading the repository.

## 14. Respect Existing RFC Decisions

An accepted RFC remains authoritative until explicitly superseded.

Do not silently contradict prior decisions in code.

## 15. Keep the Hackathon Goal Visible

Every feature should pass this question:

> Does this make the PEEXH core communication loop clearer, safer, more useful, or more demonstrable?

If not, it is probably not V1 work.

## 16. English-Only for Code and Documentation

All code, comments, docstrings, variable names, documentation, commit messages, tests, and in-project text artifacts must be written strictly in English.

Do not use any other language inside the repository codebase or documentation.

