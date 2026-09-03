"""WebSocket route for streaming audio, speech transcription, and agent decisions."""

import json
import logging
from typing import Optional
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.agent.orchestrator import PeexhAgent
from app.assemblyai.factory import get_speech_transcriber
from app.core.config import settings
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
    last_final_transcript: Optional[TranscriptEvent] = None

    async def forward_transcript(event: TranscriptEvent):
        nonlocal last_final_transcript
        try:
            if event.is_final:
                last_final_transcript = event
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
                        last_final_transcript = None
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

                        # Execute PEEXH agent interpretation and decision loop
                        raw_text = (
                            last_final_transcript.text
                            if last_final_transcript
                            else ""
                        )
                        stt_conf = (
                            last_final_transcript.confidence
                            if last_final_transcript
                            else 0.0
                        )

                        decision = await agent.process_transcript(
                            transcript=raw_text,
                            stt_confidence=stt_conf,
                        )
                        await websocket.send_text(decision.model_dump_json())

                except Exception as parse_exc:
                    logger.error(f"Error handling control message: {parse_exc}")
                    err_event = ErrorEvent(
                        message=f"Invalid message payload: {str(parse_exc)}",
                        code="INVALID_CONTROL_MESSAGE",
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
        if transcriber:
            try:
                await transcriber.stop()
            except Exception:
                pass
