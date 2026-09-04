# RFC-004 — Implementation Plan

RFC-003 done: 28/28 tests passing. State machine fixed (all decisions → AWAITING_CONFIRMATION).

## Existing Baseline

| Layer | Already exists |
|---|---|
| Backend models | `AgentDecision`, `AgentAction`, `ConfidenceLevel`, `PhraseCandidate` |
| Backend agent | `PeexhAgent` with `process_transcript`, `reset`, `set_state` |
| Backend WS | `/ws/speech` handles `start`, `stop`, binary audio, emits `agent_decision` |
| Frontend hook | `useSpeechStream` — tracks `agentDecision` state but **closes WS after decision** (must fix) |
| Frontend UI | `TranscriptView.tsx` — shows decision preview only, no action controls |

---

## What RFC-004 Adds

### Backend

**1. New domain models** (`backend/app/models/agent.py`)

- `ConfirmedPhraseSource` enum: `PROPOSAL | CANDIDATE | CORRECTION`
- `ConfirmProposalMessage` `{ type: "confirm_proposal" }`
- `SelectCandidateMessage` `{ type: "select_candidate", phrase: str }`
- `SubmitCorrectionMessage` `{ type: "submit_correction", phrase: str }`
- `RequestRepeatMessage` `{ type: "request_repeat" }`
- `CommunicationReadyEvent` `{ type: "communication_ready", phrase: str, source: ConfirmedPhraseSource }`
- `RepeatRequestedEvent` `{ type: "repeat_requested" }`

**2. PeexhAgent confirmation methods** (`backend/app/agent/orchestrator.py`)

```python
def confirm_proposal(self) -> CommunicationReadyEvent   # PROPOSE_PHRASE only
def select_candidate(self, phrase: str) -> CommunicationReadyEvent  # SHOW_CANDIDATES only
def submit_correction(self, phrase: str) -> CommunicationReadyEvent  # any decision
def request_repeat(self) -> RepeatRequestedEvent         # any decision → IDLE
```

Each validates agent is in `AWAITING_CONFIRMATION`, raises `InvalidStateError` otherwise.

**3. `/ws/speech` extended** (`backend/app/api/speech_ws.py`)

- Keep WebSocket open after `agent_decision` (never close on decision)  
- Parse new control messages and route to agent methods  
- Emit `communication_ready` or `repeat_requested` back to client  
- Validation errors emit `{ type: "error", code: "INVALID_AGENT_STATE" }`

### Frontend

**4. `useSpeechStream.ts` extended**

- Add new types: `ConfirmationStatus`, `CommunicationReadyEvent`, `RepeatRequestedEvent`
- **Remove WS close-on-decision** (line 190-193)
- Add state: `confirmationStatus`, `confirmedPhrase`, `confirmedSource`, `confirmPending`
- Add send methods: `confirmProposal()`, `selectCandidate(phrase)`, `submitCorrection(phrase)`, `requestRepeat()`
- Handle new incoming events: `communication_ready`, `repeat_requested`
- Close WS only on `start_new_message` / component unmount

**5. `TranscriptView.tsx` — replace preview with action controls**

| Decision | UI |
|---|---|
| `PROPOSE_PHRASE` | "Confirm: [phrase]" button + "Correct" + "Speak again" |
| `SHOW_CANDIDATES` | One large button per candidate + "Correct" + "Speak again" |
| `REQUEST_REPEAT` | "Speak again" (request_repeat) + "Enter manually" (opens correction) |

- Correction mode: labeled text input + submit + cancel
- Pending state on all buttons while waiting for server response

**6. `ConfirmedMessageView.tsx` — new component**

- Shows on `communication_ready`
- Large-text confirmed phrase display
- "Speak message" button (browser SpeechSynthesis, behind `ENABLE_TTS` flag)
- Replay button after first playback
- "Start new message" → resets confirmation state, begins new recording

---

## File Changes

### Backend

#### [MODIFY] [`agent.py`](file:///c:/app%20project/peexh/backend/app/models/agent.py)
Add 7 new models/enums.

#### [MODIFY] [`orchestrator.py`](file:///c:/app%20project/peexh/backend/app/agent/orchestrator.py)
Add `confirm_proposal`, `select_candidate`, `submit_correction`, `request_repeat` methods. Add `active_decision` tracking.

#### [MODIFY] [`speech_ws.py`](file:///c:/app%20project/peexh/backend/app/api/speech_ws.py)
Route new control messages. Keep socket open through confirmation phase.

#### [NEW] `backend/tests/test_agent_confirmation.py`
Unit tests for all confirmation state transitions (valid + invalid paths).

#### [NEW] `backend/tests/test_confirmation_ws.py`
WebSocket integration tests for all four confirmation controls, all three confidence paths.

### Frontend

#### [MODIFY] [`useSpeechStream.ts`](file:///c:/app%20project/peexh/frontend/src/hooks/useSpeechStream.ts)
Remove WS-close-on-decision. Add confirmation state + send methods.

#### [MODIFY] [`TranscriptView.tsx`](file:///c:/app%20project/peexh/frontend/src/components/speech/TranscriptView.tsx)
Replace preview with interactive confirmation controls.

#### [NEW] `frontend/src/components/speech/ConfirmedMessageView.tsx`
Confirmed phrase display + TTS + replay + new-message flow.

---

## Verification Plan

### Automated Tests
```bash
# Backend
.venv\Scripts\python.exe -m pytest tests/ -v

# Frontend build
npm run build
```

### Manual Flow
1. HIGH path: speak → `PROPOSE_PHRASE` → confirm → `communication_ready` → optional TTS
2. MEDIUM path: speak → `SHOW_CANDIDATES` → pick candidate → `communication_ready`
3. LOW path: speak → `REQUEST_REPEAT` → "speak again" → `repeat_requested` → new recording
4. Correction path: speak → any decision → "Enter manually" → submit → `communication_ready`
5. Error path: invalid control in wrong state → `error` event, state unchanged
