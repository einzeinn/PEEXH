# PEEXH

**PEEXH** is a voice-first communication aid for people with dysarthria who can speak but are often difficult to understand by other people or conventional speech-recognition systems.

PEEXH listens to speech, interprets the most likely intended phrase, asks the user to confirm or correct it, and then communicates the confirmed message as readable text and/or speech.

> **LLM interprets. PEEXH decides. User controls. Memory personalises.**

---

## Core Product Loop

```text
Speak (mic or loopback audio)
  ↓
AssemblyAI Realtime STT  (PCM 16kHz WebSocket stream)
  ↓
PEEXH Interpretation     (LLM intent resolution)
  ↓
Confidence Scorer        (deterministic — outside LLM)
  ├─ HIGH   → Propose single best phrase
  ├─ MEDIUM → Show candidate options
  └─ LOW    → Request repeat safely
  ↓
User confirmation / correction
  ↓
ConfirmedMessageView     (large text + SpeechSynthesis TTS)
  ↓
Personal Speech Memory   (text corrections stored in Supabase)
                         Improves future interpretations instantly
```

---

## Try It — Demo Mode (No Microphone Needed)

Open the PEEXH frontend and click **Demo Mode — No Microphone Required** at the top of the page. Pre-set dysarthric speech samples let judges and evaluators run the full interpretation, scoring, confirmation, and memory loop without microphone access or an active AssemblyAI API key.

---

## Primary User

People with dysarthria who:
- are still able to produce speech;
- know what they intend to say;
- are frequently misunderstood by listeners or ordinary STT systems.

PEEXH V1 is **not** a diagnostic tool, speech-therapy system, medical-monitoring product, or complete AAC platform.

---

## Primary Use Case

Face-to-face everyday communication.

PEEXH may also assist in high-stakes situations, such as when a user is already on a phone call and needs help making their speech understandable. PEEXH V1 does **not** place emergency calls, detect emergencies, transmit location, or contact emergency services.

---

## Hackathon

Built for the **AssemblyAI Voice Agent Hackathon** on [lablab.ai](https://lablab.ai) using the **Realtime Speech-to-Text API** path.

Demo video target: **under 3 minutes** — see [`docs/13-DemoScript.md`](docs/13-DemoScript.md) for the full storyboard.

---

## System Architecture

```text
                         ┌────────────────────────────────────────┐
                         │           Frontend (Next.js)           │
                         │                                        │
                         │  TapToTalkButton  ─┐                  │
                         │  DemoBar          ─┤──► useSpeechStream│
                         │  SettingsPanel     │       │           │
                         │  AudioInputMeter  ─┘       │  PCM 16k  │
                         └───────────────────────────-┼───────────┘
                                                       │ WebSocket /ws/speech
                         ┌─────────────────────────────┼───────────┐
                         │           Backend (FastAPI)  │           │
                         │                             ▼           │
                         │  AssemblyAI STT ◄────► SpeechTranscriber│
                         │                             │           │
                         │  ConfidenceScorer ◄─── transcript      │
                         │       │                                 │
                         │       ▼                                 │
                         │  CloudLLMInterpreter ◄── PeexhAgent    │
                         │  (memory-aware prompt)      │           │
                         │                             ▼           │
                         │  Supabase PostgreSQL ◄── MemoryStore   │
                         │  (speech_corrections,                   │
                         │   phrase_frequencies)                   │
                         └─────────────────────────────────────────┘
```

---

## Repository Layout

```text
peexh/
├── .agent/
│   └── rules.md
├── docs/
│   ├── RFC-001.md … RFC-008.md
│   ├── 13-DemoScript.md
│   └── ...
├── frontend/          # Next.js App Router
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   │   ├── demo/        (DemoBar)
│   │   │   ├── settings/    (SettingsPanel, AudioInputMeter)
│   │   │   └── speech/      (TapToTalkButton, TranscriptView)
│   │   ├── context/
│   │   ├── hooks/
│   │   └── types/
│   └── package.json
├── backend/           # FastAPI
│   ├── app/
│   │   ├── agent/
│   │   ├── api/       (health, speech_ws, demo)
│   │   ├── llm/
│   │   ├── memory/
│   │   ├── models/
│   │   └── scoring/
│   ├── evaluation/    (RFC-006 evaluation framework)
│   ├── migrations/
│   ├── Dockerfile
│   └── requirements.txt
├── render.yaml        # One-click Render.com deployment
├── .env.example
└── README.md
```

---

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`. Backend on `http://localhost:8000`.

### Environment Variables

Copy `.env.example` to `backend/.env` and fill in:

| Variable | Description |
|---|---|
| `ASSEMBLYAI_API_KEY` | AssemblyAI Realtime STT API key (optional — falls back to mock) |
| `DATABASE_URL` | Supabase PostgreSQL connection string (optional — falls back to in-memory) |

---

## Deployment

### Backend (Render.com)

Connect the repository on [render.com](https://render.com). Render auto-detects `render.yaml` and deploys the backend from `backend/Dockerfile`. Set `ASSEMBLYAI_API_KEY` and `DATABASE_URL` as environment variables in the Render dashboard.

### Frontend (Vercel)

Connect the repository on [vercel.com](https://vercel.com). Set the root directory to `frontend`. Add `NEXT_PUBLIC_API_BASE_URL` pointing to your deployed Render backend URL.

### Database (Supabase)

Run [`backend/migrations/001_create_memory_tables.sql`](backend/migrations/001_create_memory_tables.sql) in the Supabase SQL Editor to initialise the memory tables.

---

## Documentation

See `docs/` for:

| File | Contents |
|---|---|
| `RFC-001` – `RFC-008` | Phase-by-phase technical specifications |
| `06-Architecture.md` | Full system architecture |
| `07-TechnicalDecisions.md` | Architecture decision records |
| `09-Roadmap.md` | Development phases |
| `11-Research.md` | Dysarthric speech and accessibility research |
| `12-Changelog.md` | Notable changes by phase |
| `13-DemoScript.md` | Video walkthrough storyboard |

---

## Tests

```bash
cd backend
.venv\Scripts\python.exe -m pytest tests/ -v
```

All 69 backend tests pass across RFC-001 through RFC-008.

---

## License

MIT — see `LICENSE`.
