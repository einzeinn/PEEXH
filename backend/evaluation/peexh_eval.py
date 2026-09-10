"""PEEXH agent evaluator comparing interpreted communication outcomes against intended ground truth."""

import time
from typing import List, Optional

from app.agent.orchestrator import PeexhAgent
from app.agent.state import AgentState
from app.llm.base import Interpreter
from app.memory.base import MemoryStore
from evaluation.data.loader import EvaluationSample
from evaluation.metrics import LatencyBreakdown, calculate_imr, calculate_wer
from evaluation.models import PeexhResult


class PeexhEvaluator:
    """Runs evaluation samples through the full PEEXH agent pipeline and records performance."""

    def __init__(
        self,
        agent: Optional[PeexhAgent] = None,
        interpreter: Optional[Interpreter] = None,
        memory_store: Optional[MemoryStore] = None,
    ) -> None:
        self.agent = agent or PeexhAgent(
            interpreter=interpreter,
            memory_store=memory_store,
        )

    async def evaluate_sample(self, sample: EvaluationSample) -> PeexhResult:
        """Run a single sample through the agent, capturing decision, WER, IMR, and latency."""
        self.agent.reset()

        start_total = time.perf_counter()

        # 1. Memory retrieval stage
        t0 = time.perf_counter()
        memory_matches = await self.agent.memory_store.retrieve_matches(sample.raw_stt_transcript)
        t1 = time.perf_counter()
        mem_ms = (t1 - t0) * 1000.0

        ctx = {"memory_matches": memory_matches} if memory_matches else {}
        has_memory_match = bool(
            memory_matches and memory_matches[0].similarity_score >= 0.70
        )

        # 2. Interpretation stage
        self.agent.set_state(AgentState.INTERPRETING)
        t2 = time.perf_counter()
        interpretation = await self.agent.interpreter.interpret(
            transcript=sample.raw_stt_transcript,
            stt_confidence=sample.stt_confidence,
            context=ctx,
        )
        t3 = time.perf_counter()
        llm_ms = (t3 - t2) * 1000.0

        # 3. Confidence scoring stage
        self.agent.set_state(AgentState.DECIDING)
        t4 = time.perf_counter()
        decision = self.agent.scorer.score_and_decide(
            interpretation=interpretation,
            has_memory_match=has_memory_match,
        )
        decision.has_memory_match = has_memory_match
        t5 = time.perf_counter()
        scorer_ms = (t5 - t4) * 1000.0

        total_ms = (time.perf_counter() - start_total) * 1000.0

        self.agent.last_raw_transcript = sample.raw_stt_transcript
        self.agent.active_decision = decision
        self.agent.set_state(AgentState.AWAITING_CONFIRMATION)

        # WER calculation: use primary_phrase if available, otherwise raw transcript
        hypothesis = decision.primary_phrase or sample.raw_stt_transcript
        peexh_wer = calculate_wer(reference=sample.intended_phrase, hypothesis=hypothesis)

        # IMR calculation: check primary phrase or candidate list
        candidate_texts = [c.text for c in decision.candidates]
        intent_matched = calculate_imr(
            intended=sample.intended_phrase,
            primary_phrase=decision.primary_phrase,
            candidates=candidate_texts,
        )

        return PeexhResult(
            sample_id=sample.id,
            raw_transcript=sample.raw_stt_transcript,
            intended_phrase=sample.intended_phrase,
            agent_action=decision.action.value,
            primary_phrase=decision.primary_phrase,
            candidates=candidate_texts,
            peexh_wer=round(peexh_wer, 4),
            intent_matched=intent_matched,
            has_memory_match=has_memory_match,
            latency=LatencyBreakdown(
                memory_retrieval_ms=round(mem_ms, 2),
                llm_interpret_ms=round(llm_ms, 2),
                scorer_ms=round(scorer_ms, 2),
                total_pipeline_ms=round(total_ms, 2),
            ),
        )

    async def evaluate_all(self, samples: List[EvaluationSample]) -> List[PeexhResult]:
        """Evaluate a collection of samples sequentially."""
        results: List[PeexhResult] = []
        for s in samples:
            res = await self.evaluate_sample(s)
            results.append(res)
        return results
