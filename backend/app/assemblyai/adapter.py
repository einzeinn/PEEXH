"""AssemblyAI Realtime Speech-to-Text WebSocket adapter."""

import asyncio
import base64
import json
import logging
from typing import Optional
import websockets

from app.assemblyai.base import SpeechTranscriber
from app.models.speech import ErrorEvent, TranscriptEvent, TranscriptWord

logger = logging.getLogger(__name__)

ASSEMBLYAI_REALTIME_URL = "wss://api.assemblyai.com/v2/realtime/ws"


class AssemblyAITranscriber(SpeechTranscriber):
    """Realtime STT adapter connecting to AssemblyAI WebSocket service."""

    def __init__(self, api_key: str, sample_rate: int = 16000) -> None:
        super().__init__()
        self.api_key = api_key
        self.sample_rate = sample_rate
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._is_active = False

    async def start(self) -> None:
        """Connect to AssemblyAI Realtime WebSocket API."""
        if not self.api_key:
            raise ValueError("AssemblyAI API key is missing.")

        url = f"{ASSEMBLYAI_REALTIME_URL}?sample_rate={self.sample_rate}"
        headers = {"Authorization": self.api_key}

        try:
            self._ws = await websockets.connect(url, additional_headers=headers)
            self._is_active = True
            self._receive_task = asyncio.create_task(self._listen_loop())
            logger.info("Connected to AssemblyAI Realtime WebSocket")
        except Exception as exc:
            logger.error(f"Failed to connect to AssemblyAI: {exc}")
            if self._on_error:
                await self._on_error(
                    ErrorEvent(
                        message=f"AssemblyAI connection failed: {str(exc)}",
                        code="ASSEMBLYAI_CONNECTION_ERROR",
                    )
                )
            raise

    async def _listen_loop(self) -> None:
        """Background task receiving transcript messages from AssemblyAI."""
        try:
            while self._is_active and self._ws:
                msg_str = await self._ws.recv()
                data = json.loads(msg_str)
                msg_type = data.get("message_type")

                if msg_type in ("PartialTranscript", "FinalTranscript"):
                    text = data.get("text", "").strip()
                    if not text:
                        continue

                    is_final = msg_type == "FinalTranscript"
                    confidence = float(data.get("confidence", 0.0) or 0.0)
                    raw_words = data.get("words", [])
                    words = [
                        TranscriptWord(
                            text=w.get("text", ""),
                            start=w.get("start"),
                            end=w.get("end"),
                            confidence=w.get("confidence"),
                        )
                        for w in raw_words
                    ]

                    event = TranscriptEvent(
                        text=text,
                        is_final=is_final,
                        confidence=confidence,
                        words=words,
                    )

                    if self._on_transcript:
                        await self._on_transcript(event)

                elif msg_type == "SessionBegins":
                    session_id = data.get("session_id", "unknown")
                    logger.info(f"AssemblyAI session started: {session_id}")

                elif msg_type == "SessionTerminated":
                    logger.info("AssemblyAI session terminated")
                    break

        except websockets.exceptions.ConnectionClosed:
            logger.info("AssemblyAI WebSocket closed normally")
        except Exception as exc:
            logger.error(f"AssemblyAI listener loop error: {exc}")
            if self._on_error:
                await self._on_error(
                    ErrorEvent(
                        message=f"AssemblyAI streaming error: {str(exc)}",
                        code="ASSEMBLYAI_STREAM_ERROR",
                    )
                )

    async def send_audio(self, chunk: bytes) -> None:
        """Send 16-bit linear PCM audio chunk encoded as base64 JSON payload."""
        if not self._is_active or not self._ws:
            return

        try:
            b64_data = base64.b64encode(chunk).decode("utf-8")
            payload = json.dumps({"audio_data": b64_data})
            await self._ws.send(payload)
        except Exception as exc:
            logger.error(f"Failed to send audio chunk to AssemblyAI: {exc}")
            if self._on_error:
                await self._on_error(
                    ErrorEvent(
                        message=f"Failed to send audio: {str(exc)}",
                        code="AUDIO_SEND_ERROR",
                    )
                )

    async def stop(self) -> None:
        """Terminate AssemblyAI transcription session."""
        self._is_active = False

        if self._ws:
            try:
                # AssemblyAI protocol: send terminate_session JSON
                await self._ws.send(json.dumps({"terminate_session": True}))
                await asyncio.sleep(0.1)
                await self._ws.close()
            except Exception as exc:
                logger.warning(f"Error while closing AssemblyAI WebSocket: {exc}")

        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
            self._receive_task = None
