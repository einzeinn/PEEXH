"""Mock LLM interpreter for offline testing, local development, and CI."""

from typing import Any, Dict, List, Optional
from app.llm.base import Interpreter
from app.models.agent import InterpretationResult, PhraseCandidate


class MockInterpreter(Interpreter):
    """Deterministic mock interpreter mapping dysarthric phoneme approximations to clear intended phrases."""

    # Curated patterns representing common dysarthric speech transcripts
    PATTERN_MAP: Dict[str, List[Dict[str, Any]]] = {
        "water": [
            {"text": "I need some water", "confidence": 0.92, "explanation": "High acoustic and linguistic match"},
            {"text": "Can I have a drink?", "confidence": 0.58, "explanation": "Contextual alternative"},
        ],
        "help": [
            {"text": "Can you help me please?", "confidence": 0.90, "explanation": "Immediate assistance intent"},
            {"text": "I need some assistance", "confidence": 0.62, "explanation": "Formal equivalent"},
        ],
        "pain": [
            {"text": "I am in pain", "confidence": 0.88, "explanation": "Health alert intent"},
            {"text": "It hurts right now", "confidence": 0.64, "explanation": "Direct statement"},
        ],
        "hungry": [
            {"text": "I am hungry", "confidence": 0.89, "explanation": "Nutrition request"},
            {"text": "Can I have something to eat?", "confidence": 0.65, "explanation": "Polite request"},
        ],
        "tired": [
            {"text": "I am feeling tired", "confidence": 0.87, "explanation": "Physical state statement"},
            {"text": "I would like to rest", "confidence": 0.60, "explanation": "Rest request"},
        ],
    }

    async def interpret(
        self,
        transcript: str,
        stt_confidence: float = 0.0,
        context: Optional[Dict[str, Any]] = None,
    ) -> InterpretationResult:
        """Evaluate raw transcript against pattern mappings or synthesize a structured candidate."""
        cleaned = transcript.strip().lower()

        if not cleaned:
            return InterpretationResult(
                raw_transcript=transcript,
                stt_confidence=stt_confidence,
                candidates=[],
            )

        # Check for matching patterns in dictionary
        matched_candidates: List[PhraseCandidate] = []
        for key, candidate_defs in self.PATTERN_MAP.items():
            if key in cleaned:
                for c in candidate_defs:
                    matched_candidates.append(
                        PhraseCandidate(
                            text=c["text"],
                            confidence=c["confidence"],
                            explanation=c.get("explanation"),
                        )
                    )
                break

        if matched_candidates:
            return InterpretationResult(
                raw_transcript=transcript,
                stt_confidence=stt_confidence,
                candidates=matched_candidates,
            )

        # Fallback for unrecognizable or very noisy input
        if len(cleaned) < 3 or cleaned in ("uh", "um", "mmm", "ah", "..."):
            return InterpretationResult(
                raw_transcript=transcript,
                stt_confidence=min(0.3, stt_confidence),
                candidates=[
                    PhraseCandidate(
                        text="Unclear speech input",
                        confidence=0.25,
                        explanation="Input acoustic signal is below intelligibility threshold",
                    )
                ],
            )

        # Generic recognized phrase fallback
        capitalized = transcript.strip().capitalize()
        # End with period if no punctuation
        if not capitalized.endswith((".", "!", "?")):
            capitalized += "."

        return InterpretationResult(
            raw_transcript=transcript,
            stt_confidence=stt_confidence,
            candidates=[
                PhraseCandidate(
                    text=capitalized,
                    confidence=max(0.75, stt_confidence),
                    explanation="Syntactic normalization of spoken transcript",
                )
            ],
        )
