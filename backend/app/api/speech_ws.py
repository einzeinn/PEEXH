"""WebSocket route for streaming audio, speech transcription, and agent decisions."""

import json
import logging
from typing import Optional
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.agent.orchestrator import InvalidStateError, PeexhAgent
from app.assemblyai.factory import get_speech_transcriber
from app.core.config import settings
from app.models.agent import (
    ConfirmProposalMessage,
    RequestRepeatMessage,
    SelectCandidateMessage,
    SubmitCorrectionMessage,
)
from app.models.speech import (
    ErrorEvent,
    SessionStartedEvent,
    SpeechStoppedEvent,
    StartSessionMessage,
    StopSessionMessage,
    TranscriptEvent,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["speech"])


@router.websocket("/ws/speech")
async def speech_websocket_endpoint(websocket: WebSocket):
    """Bidirectional WebSocket streaming endpoint for speech audio, transcription, and agent decisions."""
    await websocket.accept()
    session_id = str(uuid.uuid4())
    transcriber = None
    agent = PeexhAgent(config=settings)
    final_transcripts: list[TranscriptEvent] = []

    async def forward_transcript(event: TranscriptEvent):
        try:
            if event.is_final:
                final_transcripts.append(event)
            await websocket.send_text(event.model_dump_json())
        except Exception as exc:
            logger.error(f"Failed to forward transcript to client: {exc}")

    async def forward_error(event: ErrorEvent):
        try:
            await websocket.send_text(event.model_dump_json())
        except Exception as exc:
            logger.error(f"Failed to forward error to client: {exc}")

    try:
        while True:
            message = await websocket.receive()

            if "text" in message and message["text"]:
                try:
                    data = json.loads(message["text"])
                    msg_type = data.get("type")

                    if msg_type == "start":
                        final_transcripts.clear()
                        agent.reset()
                        start_msg = StartSessionMessage.model_validate(data)
                        transcriber = get_speech_transcriber(
                            settings=settings,
                            sample_rate=start_msg.sample_rate,
                        )
                        transcriber.on_transcript(forward_transcript)
                        transcriber.on_error(forward_error)
                        await transcriber.start()

                        provider_name = (
                            "assemblyai"
                            if settings.ASSEMBLYAI_API_KEY
                            else "mock"
                        )
                        started_event = SessionStartedEvent(
                            session_id=session_id,
                            provider=provider_name,
                        )
                        await websocket.send_text(started_event.model_dump_json())

                    elif msg_type == "stop":
                        _ = StopSessionMessage.model_validate(data)
                        if transcriber:
                            await transcriber.stop()

                        stopped_event = SpeechStoppedEvent()
                        await websocket.send_text(stopped_event.model_dump_json())

                        # Execute PEEXH agent interpretation and decision loop over accumulated session turns
                        raw_text = " ".join(
                            t.text.strip()
                            for t in final_transcripts
                            if t.text and t.text.strip()
                        )
                        confidences = [
                            t.confidence for t in final_transcripts if t.confidence > 0
                        ]
                        stt_conf = (
                            sum(confidences) / len(confidences)
                            if confidences
                            else (
                                final_transcripts[-1].confidence
                                if final_transcripts
                                else 0.0
                            )
                        )

                        decision = await agent.process_transcript(
                            transcript=raw_text,
                            stt_confidence=stt_conf,
                        )
                        await websocket.send_text(decision.model_dump_json())

                    elif msg_type == "confirm_proposal":
                        _ = ConfirmProposalMessage.model_validate(data)
                        ready_event = agent.confirm_proposal()
                        await websocket.send_text(ready_event.model_dump_json())

                    elif msg_type == "select_candidate":
                        cand_msg = SelectCandidateMessage.model_validate(data)
                        ready_event = agent.select_candidate(cand_msg.phrase)
                        await websocket.send_text(ready_event.model_dump_json())

                    elif msg_type == "submit_correction":
                        corr_msg = SubmitCorrectionMessage.model_validate(data)
                        ready_event = agent.submit_correction(corr_msg.phrase)
                        await websocket.send_text(ready_event.model_dump_json())

                    elif msg_type == "request_repeat":
                        _ = RequestRepeatMessage.model_validate(data)
                        repeat_event = agent.request_repeat()
                        await websocket.send_text(repeat_event.model_dump_json())

                    else:
                        raise ValueError(f"Unknown message type: {msg_type}")

                except InvalidStateError as state_exc:
                    logger.warning(f"Invalid state for confirmation message: {state_exc}")
                    err_event = ErrorEvent(
                        message=str(state_exc),
                        code="INVALID_AGENT_STATE",
                    )
                    await websocket.send_text(err_event.model_dump_json())

                except ValueError as parse_exc:
                    # Bad control message from the client (unknown type, bad payload, etc.)
                    logger.error(f"Error handling control message: {parse_exc}")
                    err_event = ErrorEvent(
                        message=f"Invalid message payload: {str(parse_exc)}",
                        code="INVALID_CONTROL_MESSAGE",
                    )
                    await websocket.send_text(err_event.model_dump_json())

                except Exception as parse_exc:
                    # Catch-all: avoid leaking upstream AssemblyAI failures as
                    # INVALID_CONTROL_MESSAGE — forward the raw error description.
                    logger.error(f"Unexpected error handling message: {parse_exc}")
                    err_event = ErrorEvent(
                        message=str(parse_exc),
                        code="INTERNAL_ERROR",
                    )
                    await websocket.send_text(err_event.model_dump_json())

            elif "bytes" in message and message["bytes"]:
                if transcriber:
                    await transcriber.send_audio(message["bytes"])

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from speech session {session_id}")
    except Exception as exc:
        logger.error(f"Unexpected error in speech WebSocket: {exc}")
    finally:
        agent.reset()
        if transcriber:
            try:
                await transcriber.stop()
            except Exception:
                pass
