# 13 — Demo Script & Video Walkthrough Storyboard

**Target duration:** 2 minutes 45 seconds  
**Format:** Screen recording with voiceover narration  
**Recording setup:** PEEXH running on `localhost:3000` (frontend) + `localhost:8000` (backend)  

---

## Pre-Recording Checklist

- [ ] Backend running: `uvicorn app.main:app --reload` (with `ASSEMBLYAI_API_KEY` set for live STT)
- [ ] Frontend running: `npm run dev`
- [ ] Browser: Chrome or Edge, microphone permission granted for `localhost:3000`
- [ ] Audio: External mic or headset connected and selected in PEEXH Settings
- [ ] Demo dataset prepared: practise saying sample dysarthric utterances before recording
- [ ] Screen recording software ready (OBS, Loom, or QuickTime)
- [ ] Optional: VB-CABLE or Stereo Mix configured for loopback audio testing

---

## Scene-by-Scene Script

### Scene 1 — Problem Statement (0:00–0:15)

**On-screen:** Title card over an audio waveform animation showing fragmented speech.

**Narration:**
> "For millions of people with dysarthria — a motor speech disorder affecting muscle control — everyday voice recognition fails.
> Standard models expect fluent, clearly articulated speech. Dysarthric speech is consistent, but abbreviated and phonetically distorted.
> The technology fails. The user is silenced."

**Action:** Fade to PEEXH interface loading on a clean mobile-width browser window.

---

### Scene 2 — Product Introduction (0:15–0:35)

**On-screen:** PEEXH app interface. Header visible: "peexh — assistive voice".

**Narration:**
> "Meet PEEXH: a deterministic voice communication aid that combines AssemblyAI real-time speech streaming with a personal adaptive memory layer.
> PEEXH does not try to replace the user's voice. It interprets, proposes, and lets the user control every word."

**Action:** Show the header with settings gear icon. Briefly open Settings Panel to show device selector and preprocessing toggles. Close settings.

---

### Scene 3 — Core Communication Loop (0:35–1:10)

**On-screen:** Full screen of PEEXH interface. Tap the speak button.

**Narration:**
> "Watch what happens when our user says 'i ned wtr' — a typical dysarthric abbreviation for 'I need some water'."

**Action (live):**
1. Tap **Speak** button.
2. Say (or play): *"i ned wtr"*
3. AssemblyAI raw STT appears: `"i ned wtr"` — clearly incomplete.
4. Agent card appears: **HIGH CONFIDENCE** → `"I need some water"`.
5. Tap **Confirm message**.
6. `ConfirmedMessageView` banner appears in large text. Browser TTS reads the phrase aloud.

**Narration (over confirmation):**
> "Raw STT produces a mangled fragment. But PEEXH interprets the phonetic pattern, proposes the intended phrase, and reads it aloud — in under one second."

---

### Scene 4 — Adaptive Memory Loop (1:10–1:45)

**On-screen:** Begin new utterance session.

**Narration:**
> "Dysarthric speech is uniquely consistent per individual speaker. When a user corrects an interpretation, PEEXH learns the phonetic pattern immediately and applies it from that moment forward."

**Action (live):**
1. Tap **Speak**. Say: *"wer iz pil"* (novel phrase).
2. Agent shows **MEDIUM CONFIDENCE** candidates.
3. Tap **Correct phrase**. Type *"Time for my medicine"*.
4. Tap **Confirm correction**. Message confirmed with TTS.
5. Tap **Speak** again. Say: *"wer iz pil"* a second time.
6. Agent decision now shows **HIGH CONFIDENCE** → `"Time for my medicine"` with the **"Learned from your speech"** badge.

**Narration (over second repeat):**
> "The second utterance is instantly recognised — zero additional training. Pure memory-assisted personalisation."

---

### Scene 5 — Safety Under Uncertainty (1:45–2:15)

**On-screen:** New utterance.

**Narration:**
> "What happens when the acoustic signal is too ambiguous for any reliable interpretation?"

**Action (live or via Demo Mode):**
1. Tap **Speak**. Say: *"uh ..."* (deliberately vague).
2. Agent card shows **LOW CONFIDENCE** → `REQUEST_REPEAT`.
3. Message displayed: *"PEEXH is not confident enough to guess."*
4. Options shown: **Speak again** | **Enter phrase manually**.

**Narration:**
> "PEEXH refuses to hallucinate. It does not guess when acoustic confidence is below threshold. It safely prompts the user to repeat or type — eliminating dangerous miscommunication."

---

### Scene 6 — System Architecture (2:15–2:35)

**On-screen:** Architecture diagram (`docs/architecture.png` or inline Mermaid).

**Narration:**
> "Under the hood: AssemblyAI provides real-time PCM audio streaming and STT tokens. A deterministic confidence scorer classifies each utterance into High, Medium, or Low tiers — outside the LLM, eliminating hallucination risk. The cloud LLM interprets intent. Supabase stores text corrections for persistent personal memory.
> No raw audio is ever stored."

---

### Scene 7 — Closing & Call to Action (2:35–2:50)

**On-screen:** Confirmed message — large text: *"Be understood."* — with PEEXH branding.

**Narration:**
> "PEEXH. Be understood. Built for the AssemblyAI Voice Agent Hackathon — and for every person whose voice deserves to be heard."

**Action:** Fade out with confirmed phrase visible. Show GitHub repo link.

---

## Interactive Demo Mode (No Microphone Required)

For judges reviewing without microphone access, click **Demo Mode — No Microphone Required** at the top of the PEEXH interface. Select any pre-set sample to demonstrate the full pipeline:

| Sample | Raw Input | Expected Outcome |
|---|---|---|
| Sample 1 | `"i ned wtr"` | High confidence proposal: "I need some water" |
| Sample 2 | `"wer iz pil"` | Medium confidence candidates |
| Sample 3 | `"uh ..."` | Safe low-confidence repeat request |
| Sample 4 — Memory Loop | `"wer iz pil"` (after correction) | Instant memory recall |

---

## Recording Guidelines

- **Resolution:** 1920×1080 or 1280×720 (mobile-width browser window centred)
- **Frame rate:** 30 fps minimum
- **Audio:** Record narration separately and mix in post, or use a clean lapel mic
- **Cursor:** Use a large cursor or cursor highlight tool for visibility
- **Captions:** Add closed captions to all narration for accessibility compliance
