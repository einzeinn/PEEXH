# 07 — Technical Decisions

## TD-001 — Separate Frontend and Backend

**Decision:** Keep `frontend/` and `backend/` separate.

**Reasoning:**
Frontend focuses on realtime interaction and accessibility. Backend owns speech integration, interpretation, memory, confidence policy, and provider adapters.

## TD-002 — Frontend Stack

**Decision:**
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Zustand only if shared client state becomes complex enough to justify it

**Reasoning:** Familiar stack, fast iteration, strong accessibility potential, straightforward deployment.

## TD-003 — Backend Stack

**Decision:**
- FastAPI
- Python
- WebSocket support

**Reasoning:** Better fit for AI orchestration, memory experiments, evaluation scripts, and deterministic agent logic.

## TD-004 — Speech Provider

**Decision:** AssemblyAI Realtime Speech-to-Text over WebSocket.

**Reasoning:** It is the core hackathon technology and provides the realtime transcript required by PEEXH.

## TD-005 — No General Agent Framework

**Decision:** Implement a custom state machine.

Do not use LangChain/LangGraph for V1.

**Reasoning:** PEEXH has a tiny action set and requires transparent, controllable behavior.

## TD-006 — LLM Role

**Decision:** Use a fast, low-latency cloud LLM through a provider abstraction.

The LLM produces structured candidate interpretations.

The LLM does **not** make final policy decisions.

## TD-007 — Structured LLM Output

Expected conceptual output:

```json
{
  "candidates": [
    {
      "text": "I need water",
      "model_confidence": 0.89
    }
  ]
}
```

Exact schema may evolve through RFC.

## TD-008 — Deterministic Confidence Policy

**Decision:** Final PEEXH confidence is calculated outside the LLM.

Potential inputs:
- AssemblyAI transcript confidence;
- candidate agreement;
- personal-memory similarity;
- contextual relevance;
- repeat consistency.

Threshold values are configurable and must be tuned empirically.

## TD-009 — Personal Memory Store

**Decision:** Supabase PostgreSQL.

Potential vector search:
- pgvector.

Memory types:
- correction pairs;
- recurring phrase patterns;
- contextual associations;
- preferences.

## TD-010 — TTS

**Decision:** Start with browser SpeechSynthesis if sufficient.

Introduce a dedicated TTS provider only if the demo or accessibility quality requires it.

TTS is not PEEXH's main innovation.

## TD-011 — Environment-Driven Configuration

**Decision:** Secrets and deploy-time configuration live in `.env` files locally and environment variables in deployment.

Commit `.env.example`; never commit `.env`.

Python virtual environment belongs at `backend/.venv/` and is gitignored.

## TD-012 — Provider Interfaces

Core logic should target abstractions such as:

```text
SpeechTranscriber
Interpreter
MemoryStore
ConfidenceScorer
SpeechOutput
```

Provider-specific code must remain behind adapters.

## TD-013 — English-First MVP

**Decision:** PEEXH V1 is English-first.

**Reasoning:**
- easier access to appropriate speech samples;
- simpler evaluation;
- clearer hackathon demo;
- narrower personalization problem.

Multilingual support is future scope.
