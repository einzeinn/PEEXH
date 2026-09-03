"""Cloud LLM adapter for structured speech interpretation."""

import json
import logging
from typing import Any, Dict, Optional
import httpx

from app.llm.base import Interpreter
from app.llm.mock import MockInterpreter
from app.models.agent import InterpretationResult, PhraseCandidate

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are PEEXH's Speech Interpretation Engine.
PEEXH is an assistive voice tool for people with dysarthria. Dysarthric speech often produces phonetic approximations, omitted consonants, or shortened words.
Your role is to interpret the user's likely intended everyday phrase based on the raw speech transcript.
Output ONLY a JSON object adhering strictly to this schema:
{
  "candidates": [
    {
      "text": "Intended complete phrase",
      "confidence": 0.85,
      "explanation": "Why this is likely the intended phrase"
    }
  ]
}
Rules:
- Provide 1 to 3 plausible candidate phrases ranked by probability.
- Confidence must be a float between 0.0 and 1.0.
- If the transcript is incomprehensible noise, assign confidence < 0.40.
- Do NOT include conversational filler, formatting tags, or text outside the JSON object.
"""


class CloudLLMInterpreter(Interpreter):
    """Adapter connecting to OpenAI-compatible LLM endpoints."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
    ) -> None:
        self.api_key = api_key
        self.model = model or "gpt-4o-mini"
        self.base_url = base_url.rstrip("/") if base_url else "https://api.openai.com/v1"
        self._fallback = MockInterpreter()

    async def interpret(
        self,
        transcript: str,
        stt_confidence: float = 0.0,
        context: Optional[Dict[str, Any]] = None,
    ) -> InterpretationResult:
        """Call LLM API to produce structured interpretation candidates."""
        if not self.api_key:
            return await self._fallback.interpret(transcript, stt_confidence, context)

        user_content = f"Raw transcript: '{transcript}' (STT acoustic confidence: {stt_confidence:.2f})"
        if context:
            user_content += f"\nRecent context/memory: {json.dumps(context)}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)

                candidates = [
                    PhraseCandidate(
                        text=c["text"],
                        confidence=float(c.get("confidence", 0.7)),
                        explanation=c.get("explanation"),
                    )
                    for c in parsed.get("candidates", [])
                ]

                return InterpretationResult(
                    raw_transcript=transcript,
                    stt_confidence=stt_confidence,
                    candidates=candidates,
                )
        except Exception as exc:
            logger.warning(f"Cloud LLM call failed, falling back to mock: {exc}")
            return await self._fallback.interpret(transcript, stt_confidence, context)
