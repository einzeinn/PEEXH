"""Memory loop evaluator verifying adaptive personalization across repeated utterances."""

from typing import List, Optional

from app.agent.orchestrator import PeexhAgent
from app.llm.base import Interpreter
from app.memory.base import MemoryStore
from app.memory.mock import MockMemoryStore
from evaluation.data.loader import EvaluationSample
from evaluation.metrics import calculate_wer
from evaluation.models import MemoryLoopResult


class MemoryLoopEvaluator:
    """Simulates multi-pass sessions to quantify memory-driven accuracy gains."""

    def __init__(
        self,
        agent: Optional[PeexhAgent] = None,
        interpreter: Optional[Interpreter] = None,
        memory_store: Optional[MemoryStore] = None,
    ) -> None:
        self.memory_store = memory_store or MockMemoryStore()
        self.agent = agent or PeexhAgent(
            interpreter=interpreter,
            memory_store=self.memory_store,
        )

    async def evaluate_sample(
        self,
        sample: EvaluationSample,
        user_id: str = "eval_user",
    ) -> MemoryLoopResult:
        """Execute two-pass evaluation with user correction injection between passes."""
        # Ensure clean state for evaluation run
        await self.memory_store.clear_memory(user_id=user_id)
        self.agent.reset()

        # --- Pass 1: Without prior memory ---
        dec1 = await self.agent.process_transcript(
            transcript=sample.raw_stt_transcript,
            stt_confidence=sample.stt_confidence,
            context={"user_id": user_id},
        )
        hyp1 = dec1.primary_phrase or sample.raw_stt_transcript
        pass1_wer = calculate_wer(reference=sample.intended_phrase, hypothesis=hyp1)

        # --- Learning Action: Record verified correction ---
        await self.memory_store.record_correction(
            raw_transcript=sample.raw_stt_transcript,
            corrected_phrase=sample.intended_phrase,
            user_id=user_id,
        )

        # --- Pass 2: Identical utterance with memory active ---
        self.agent.reset()
        dec2 = await self.agent.process_transcript(
            transcript=sample.raw_stt_transcript,
            stt_confidence=sample.stt_confidence,
            context={"user_id": user_id},
        )
        hyp2 = dec2.primary_phrase or sample.raw_stt_transcript
        pass2_wer = calculate_wer(reference=sample.intended_phrase, hypothesis=hyp2)

        memory_delta = round(pass1_wer - pass2_wer, 4)

        # Cleanup memory for this evaluation slot
        await self.memory_store.clear_memory(user_id=user_id)

        return MemoryLoopResult(
            sample_id=sample.id,
            raw_transcript=sample.raw_stt_transcript,
            intended_phrase=sample.intended_phrase,
            pass1_wer=round(pass1_wer, 4),
            pass2_wer=round(pass2_wer, 4),
            memory_delta=memory_delta,
            has_memory_match_pass2=bool(dec2.has_memory_match),
        )

    async def evaluate_all(
        self,
        samples: List[EvaluationSample],
        user_id: str = "eval_user",
    ) -> List[MemoryLoopResult]:
        """Evaluate memory loop adaptation across all samples."""
        results: List[MemoryLoopResult] = []
        for s in samples:
            res = await self.evaluate_sample(s, user_id=user_id)
            results.append(res)
        return results
