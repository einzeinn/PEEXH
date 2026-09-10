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
        "wtr": [
            {"text": "I need some water", "confidence": 0.91, "explanation": "Phonetic reduction of water"},
            {"text": "Can I have a drink?", "confidence": 0.58, "explanation": "Contextual alternative"},
        ],
        "help": [
            {"text": "Can you help me please?", "confidence": 0.90, "explanation": "Immediate assistance intent"},
            {"text": "I need some assistance", "confidence": 0.62, "explanation": "Formal equivalent"},
        ],
        "hel": [
            {"text": "Can you help me please?", "confidence": 0.89, "explanation": "Plosive omission on help"},
            {"text": "I need some assistance", "confidence": 0.60, "explanation": "Formal equivalent"},
        ],
        "hlp": [
            {"text": "Can you help me please?", "confidence": 0.89, "explanation": "Vowel reduction on help"},
            {"text": "I need some assistance", "confidence": 0.60, "explanation": "Formal equivalent"},
        ],
        "pain": [
            {"text": "I am in pain", "confidence": 0.88, "explanation": "Health alert intent"},
            {"text": "It hurts right now", "confidence": 0.64, "explanation": "Direct statement"},
        ],
        "pan": [
            {"text": "I am in pain", "confidence": 0.87, "explanation": "Vowel distortion on pain"},
            {"text": "It hurts right now", "confidence": 0.63, "explanation": "Direct statement"},
        ],
        "hurts": [
            {"text": "I am in pain", "confidence": 0.88, "explanation": "Synonym expression of pain"},
            {"text": "It hurts right now", "confidence": 0.70, "explanation": "Direct statement"},
        ],
        "hungry": [
            {"text": "I am hungry", "confidence": 0.89, "explanation": "Nutrition request"},
            {"text": "Can I have something to eat?", "confidence": 0.65, "explanation": "Polite request"},
        ],
        "hungri": [
            {"text": "I am hungry", "confidence": 0.89, "explanation": "Velar softening on hungry"},
            {"text": "Can I have something to eat?", "confidence": 0.65, "explanation": "Polite request"},
        ],
        "tired": [
            {"text": "I am feeling tired", "confidence": 0.87, "explanation": "Physical state statement"},
            {"text": "I would like to rest", "confidence": 0.60, "explanation": "Rest request"},
        ],
        "tyrd": [
            {"text": "I am feeling tired", "confidence": 0.87, "explanation": "Diphthong reduction on tired"},
            {"text": "I would like to rest", "confidence": 0.60, "explanation": "Rest request"},
        ],
        "rest": [
            {"text": "I am feeling tired", "confidence": 0.86, "explanation": "Fatigue expression"},
            {"text": "I would like to rest", "confidence": 0.75, "explanation": "Rest request"},
        ],
        "bathrm": [
            {"text": "I need the bathroom", "confidence": 0.90, "explanation": "Apostrophe/interdental omission on bathroom"},
            {"text": "Can you assist me to the restroom?", "confidence": 0.62, "explanation": "Polite request"},
        ],
        "medsn": [
            {"text": "Time for my medicine", "confidence": 0.89, "explanation": "Syncope on medicine"},
            {"text": "I need my medication", "confidence": 0.68, "explanation": "Medication request"},
        ],
        "kold": [
            {"text": "I am feeling cold", "confidence": 0.88, "explanation": "Cluster reduction on cold"},
            {"text": "Can I have a blanket please?", "confidence": 0.65, "explanation": "Contextual request"},
        ],
        "hot": [
            {"text": "It is too hot here", "confidence": 0.88, "explanation": "Temperature discomfort"},
            {"text": "Could we turn on the fan?", "confidence": 0.65, "explanation": "Action request"},
        ],
        "thnk": [
            {"text": "Yes thank you", "confidence": 0.91, "explanation": "Interdental fronting on thank"},
            {"text": "Thank you so much", "confidence": 0.68, "explanation": "Polite gratitude"},
        ],
        "nt now": [
            {"text": "No not right now", "confidence": 0.89, "explanation": "Nasal emphasis on not now"},
            {"text": "I would rather wait", "confidence": 0.60, "explanation": "Alternative"},
        ],
        "doc-tr": [
            {"text": "Please call the doctor", "confidence": 0.90, "explanation": "Prolonged syllable on doctor"},
            {"text": "I need to see the physician", "confidence": 0.64, "explanation": "Formal equivalent"},
        ],
        "morn-in": [
            {"text": "Good morning", "confidence": 0.92, "explanation": "Velar nasal replacement on morning"},
            {"text": "Hello there", "confidence": 0.55, "explanation": "Greeting alternative"},
        ],
        "nyt": [
            {"text": "Good night", "confidence": 0.91, "explanation": "Unreleased stop on night"},
            {"text": "I am going to sleep", "confidence": 0.60, "explanation": "Greeting alternative"},
        ],
        "lie down": [
            {"text": "I want to lie down", "confidence": 0.90, "explanation": "Resting posture request"},
            {"text": "Can I go back to bed?", "confidence": 0.64, "explanation": "Alternative"},
        ],
        "o-kay": [
            {"text": "I am feeling okay", "confidence": 0.91, "explanation": "Reassurance statement with glottal stop"},
            {"text": "Everything is fine", "confidence": 0.65, "explanation": "Alternative"},
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

        # 0. Check for personal speech memory matches (RFC-005)
        if context and "memory_matches" in context:
            mem_list = context.get("memory_matches") or []
            if mem_list:
                top_mem = mem_list[0]
                matched_phrase = (
                    getattr(top_mem, "matched_phrase", None)
                    or (top_mem.get("matched_phrase") if isinstance(top_mem, dict) else None)
                )
                sim = (
                    getattr(top_mem, "similarity_score", 0.0)
                    or (top_mem.get("similarity_score", 0.0) if isinstance(top_mem, dict) else 0.0)
                )
                if matched_phrase and sim >= 0.70:
                    return InterpretationResult(
                        raw_transcript=transcript,
                        stt_confidence=stt_confidence,
                        candidates=[
                            PhraseCandidate(
                                text=matched_phrase,
                                confidence=0.92,
                                explanation="Matched verified personal speech memory",
                            )
                        ],
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
