# 06 — Architecture

## 1. Architecture Goal

PEEXH should be modular, explainable, replaceable, and small enough for one developer to understand completely.

## 2. Repository Boundary

Frontend and backend remain separate because their responsibilities differ significantly.

```text
peexh/
├── frontend/
└── backend/
```

## 3. High-Level Architecture

```text
                    ┌──────────────────────┐
                    │        USER          │
                    │  dysarthric speech   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Frontend        │
                    │ microphone + UI      │
                    └──────────┬───────────┘
                               │ audio/events
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │ HTTP / WebSocket     │
                    └──────────┬───────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │ AssemblyAI Realtime STT  │
                 └────────────┬─────────────┘
                              │ transcript
                              ▼
        ┌──────────────────────────────────────────┐
        │              PEEXH AGENT                 │
        │                                          │
        │  Context Builder                         │
        │      ↓                                   │
        │  LLM Interpreter                         │
        │      ↓                                   │
        │  Candidate Phrases                       │
        │      ↓                                   │
        │  Deterministic Scorer                    │
        │      ↓                                   │
        │  Decision Engine                         │
        └───────┬──────────────┬──────────────┬────┘
                │ HIGH         │ MEDIUM       │ LOW
                ▼              ▼              ▼
           Best phrase      Candidates       Repeat
                └──────────────┬──────────────┘
                               ▼
                        User Confirmation
                               │
                    ┌──────────┴───────────┐
                    ▼                      ▼
                Communicate             Correct
                Text / TTS                 │
                                           ▼
                                Personal Speech Memory
```

## 4. Agent Loop

```text
Observe
  ↓
Interpret
  ↓
Score
  ↓
Decide
  ↓
Ask / Propose / Repeat
  ↓
User confirms or corrects
  ↓
Communicate
  ↓
Learn
```

## 5. Agent Actions

V1 action set:

- `PROPOSE_PHRASE`
- `SHOW_CANDIDATES`
- `REQUEST_REPEAT`
- `COMMUNICATE`
- `LEARN_CORRECTION`

## 6. Backend Modules

Suggested structure:

```text
backend/
├── app/
│   ├── api/
│   ├── agent/
│   ├── assemblyai/
│   ├── memory/
│   ├── scoring/
│   ├── llm/
│   ├── models/
│   └── core/
├── tests/
└── .env.example
```

### `api/`
HTTP and WebSocket boundaries.

### `agent/`
State machine and orchestration.

### `assemblyai/`
Realtime speech transport and transcript adapter.

### `memory/`
Correction pairs, recurring phrase retrieval, contextual associations, preferences.

### `scoring/`
Deterministic confidence and ranking policy.

### `llm/`
Provider-independent interpretation interface and adapters.

### `models/`
Typed domain and API schemas.

### `core/`
Configuration, logging, shared infrastructure.

## 7. Frontend Responsibilities

- microphone interaction;
- listening/transcribing/interpreting states;
- candidate rendering;
- confirmation;
- correction;
- repeat flow;
- large-text output;
- TTS control;
- accessibility behavior.

## 8. Personal Speech Memory

```text
Correction Pairs
        │
Recurring Phrase Patterns
        │
Contextual Associations
        │
Preferences
        ▼
   Memory Retrieval
        ▼
   Context Builder
        ▼
  LLM Interpretation
```

Potential store:
- Supabase PostgreSQL;
- pgvector for similarity search where useful.

## 9. Configuration Architecture

Provider-specific settings must come from typed environment configuration.

Examples:
- AssemblyAI key;
- LLM provider/model;
- Supabase credentials;
- confidence thresholds;
- TTS selection;
- feature flags.

## 10. Deployment

Initial target:

```text
Frontend → Vercel
Backend  → Railway or Render
Database → Supabase
Speech   → AssemblyAI
```

The architecture must not depend on one hosting provider.
