"""AssemblyAI Streaming Speech-to-Text WebSocket adapter (v3)."""

import asyncio
import json
import logging
from typing import Optional
import websockets

from app.assemblyai.base import SpeechTranscriber
from app.models.speech import ErrorEvent, TranscriptEvent, TranscriptWord

logger = logging.getLogger(__name__)

# v3 streaming endpoint
ASSEMBLYAI_STREAMING_URL = "wss://streaming.assemblyai.com/v3/ws"


class AssemblyAITranscriber(SpeechTranscriber):
    """Realtime STT adapter connecting to AssemblyAI v3 streaming WebSocket service."""

    def __init__(self, api_key: str, sample_rate: int = 16000) -> None:
        super().__init__()
        self.api_key = api_key
        self.sample_rate = sample_rate
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._is_active = False
        self._terminated_event: Optional[asyncio.Event] = None

    async def start(self) -> None:
        """Connect to AssemblyAI v3 Streaming WebSocket API."""
        if not self.api_key:
            raise ValueError("AssemblyAI API key is missing.")

        # v3: sample_rate + explicit model as query params; auth via header
        url = (
            f"{ASSEMBLYAI_STREAMING_URL}"
            f"?sample_rate={self.sample_rate}"
            f"&speech_model=universal-3-5-pro"
        )
        headers = {"Authorization": self.api_key}

        try:
            self._ws = await websockets.connect(url, additional_headers=headers)
            self._is_active = True
            self._terminated_event = asyncio.Event()
            self._receive_task = asyncio.create_task(self._listen_loop())
            logger.info("Connected to AssemblyAI v3 Streaming WebSocket")
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
        """Background task receiving transcript messages from AssemblyAI v3."""
        try:
            while self._ws:
                msg_str = await self._ws.recv()
                data = json.loads(msg_str)
                msg_type = data.get("type")

                if msg_type == "Turn":
                    # v3 transcript event: carries transcript + end_of_turn flag
                    transcript = data.get("transcript", "")
                    text = transcript.strip() if transcript else ""
                    is_final = bool(data.get("end_of_turn", False))

                    if not text:
                        continue

                    # v3 does not expose per-word confidence; use 0.0 as default
                    words_raw = data.get("words", [])
                    words = [
                        TranscriptWord(
                            text=w.get("text", ""),
                            start=w.get("start"),
                            end=w.get("end"),
                            confidence=w.get("confidence"),
                        )
                        for w in words_raw
                    ]

                    event = TranscriptEvent(
                        text=text,
                        is_final=is_final,
                        confidence=float(data.get("confidence", 0.0) or 0.0),
                        words=words,
                    )

                    if self._on_transcript:
                        await self._on_transcript(event)

                elif msg_type == "Begin":
                    # v3 session started event (was SessionBegins in v2)
                    session_id = data.get("id", "unknown")
                    logger.info(f"AssemblyAI v3 session started: {session_id}")

                elif msg_type == "Termination":
                    # v3 session ended event (was SessionTerminated in v2)
                    logger.info("AssemblyAI v3 session terminated")
                    if self._terminated_event:
                        self._terminated_event.set()
                    break

                elif msg_type == "Error":
                    # v3 surfaces upstream errors as a typed Error message
                    error_msg = data.get("error", "Unknown AssemblyAI error")
                    logger.error(f"AssemblyAI upstream error: {error_msg}")
                    if self._on_error:
                        await self._on_error(
                            ErrorEvent(
                                message=f"AssemblyAI error: {error_msg}",
                                code="ASSEMBLYAI_UPSTREAM_ERROR",
                            )
                        )
                    if self._terminated_event:
                        self._terminated_event.set()
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
        finally:
            if self._terminated_event:
                self._terminated_event.set()

    async def send_audio(self, chunk: bytes) -> None:
        """Send raw binary PCM16 audio chunk directly to AssemblyAI v3."""
        if not self._is_active or not self._ws:
            return

        try:
            # v3: raw binary frames — no base64 JSON wrapper
            await self._ws.send(chunk)
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
        """Terminate AssemblyAI v3 transcription session gracefully."""
        if not self._is_active and self._receive_task is None:
            return

        self._is_active = False

        if self._ws:
            try:
                # v3 terminate message (was {"terminate_session": true} in v2)
                await self._ws.send(json.dumps({"type": "Terminate"}))
                if self._terminated_event:
                    try:
                        await asyncio.wait_for(self._terminated_event.wait(), timeout=3.0)
                    except asyncio.TimeoutError:
                        logger.warning("Timed out waiting for AssemblyAI Termination event")
            except Exception as exc:
                logger.warning(f"Error while stopping AssemblyAI WebSocket: {exc}")
            finally:
                try:
                    await self._ws.close()
                except Exception:
                    pass
                self._ws = None

        if self._receive_task:
            if not self._receive_task.done():
                self._receive_task.cancel()
                try:
                    await self._receive_task
                except asyncio.CancelledError:
                    pass
            self._receive_task = None
