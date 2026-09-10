"""Evaluation runner orchestrating baseline capture, PEEXH evaluation, and memory loop testing."""

import argparse
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from app.core.config import settings
from app.llm.adapter import CloudLLMInterpreter
from app.llm.mock import MockInterpreter
from app.memory.mock import MockMemoryStore
from evaluation.baseline import BaselineCapture
from evaluation.data.loader import EvaluationSample, load_samples
from evaluation.memory_loop import MemoryLoopEvaluator
from evaluation.models import (
    BaselineResult,
    EvaluationSummary,
    MemoryLoopResult,
    PeexhResult,
)
from evaluation.peexh_eval import PeexhEvaluator
from evaluation.report import ReportGenerator


class EvaluationRunner:
    """Top-level orchestrator executing the full RFC-006 evaluation suite."""

    def __init__(
        self,
        dataset_path: Optional[str | Path] = None,
        use_mock_interpreter: bool = True,
        use_mock_memory: bool = True,
        output_dir: Optional[str | Path] = None,
    ) -> None:
        self.samples: List[EvaluationSample] = load_samples(dataset_path)
        self.use_mock_interpreter = use_mock_interpreter
        self.use_mock_memory = use_mock_memory
        self.report_generator = ReportGenerator(output_dir=output_dir)

        # Initialize components
        interpreter = (
            MockInterpreter()
            if use_mock_interpreter
            else CloudLLMInterpreter(api_key=settings.LLM_API_KEY, model=settings.LLM_MODEL)
        )
        memory_store = MockMemoryStore()  # Isolation for evaluation

        self.baseline_runner = BaselineCapture()
        self.peexh_runner = PeexhEvaluator(interpreter=interpreter, memory_store=memory_store)
        self.memory_loop_runner = MemoryLoopEvaluator(interpreter=interpreter, memory_store=memory_store)

    async def run_baseline(self) -> List[BaselineResult]:
        """Run baseline STT evaluation."""
        return self.baseline_runner.evaluate_all(self.samples)

    async def run_peexh(self) -> List[PeexhResult]:
        """Run full PEEXH agent pipeline evaluation."""
        return await self.peexh_runner.evaluate_all(self.samples)

    async def run_memory_loop(self) -> List[MemoryLoopResult]:
        """Run two-pass adaptive learning evaluation."""
        return await self.memory_loop_runner.evaluate_all(self.samples)

    async def run_all(
        self,
    ) -> Tuple[EvaluationSummary, List[BaselineResult], List[PeexhResult], List[MemoryLoopResult]]:
        """Execute all evaluation passes and aggregate metrics into EvaluationSummary."""
        baseline_results = await self.run_baseline()
        peexh_results = await self.run_peexh()
        memory_results = await self.run_memory_loop()

        total = len(self.samples)
        if total == 0:
            raise ValueError("No evaluation samples provided.")

        baseline_avg_wer = sum(b.baseline_wer for b in baseline_results) / total
        peexh_avg_wer = sum(p.peexh_wer for p in peexh_results) / total

        # Relative WER improvement: (baseline - peexh) / baseline
        if baseline_avg_wer > 0:
            wer_improvement = ((baseline_avg_wer - peexh_avg_wer) / baseline_avg_wer) * 100.0
        else:
            wer_improvement = 0.0

        matched_count = sum(1 for p in peexh_results if p.intent_matched)
        imr = matched_count / total

        avg_latency = sum(p.latency.total_pipeline_ms for p in peexh_results) / total
        avg_mem_delta = sum(m.memory_delta for m in memory_results) / total

        summary = EvaluationSummary(
            total_samples=total,
            baseline_avg_wer=round(baseline_avg_wer, 4),
            peexh_avg_wer=round(peexh_avg_wer, 4),
            wer_improvement_pct=round(wer_improvement, 2),
            intent_match_rate=round(imr, 4),
            avg_total_latency_ms=round(avg_latency, 2),
            memory_loop_avg_delta=round(avg_mem_delta, 4),
            generated_at=datetime.now(timezone.utc),
        )

        return summary, baseline_results, peexh_results, memory_results

    async def run_and_export(self) -> Tuple[EvaluationSummary, Path, Path]:
        """Execute full evaluation and export reports to disk."""
        summary, b_res, p_res, m_res = await self.run_all()
        mode_str = "mock" if self.use_mock_interpreter else "cloud"
        md_path, json_path = self.report_generator.export_reports(
            summary=summary,
            baseline_results=b_res,
            peexh_results=p_res,
            memory_results=m_res,
            mode=mode_str,
        )
        return summary, md_path, json_path


def main() -> None:
    """CLI entrypoint to run PEEXH benchmark."""
    parser = argparse.ArgumentParser(description="PEEXH Phase 5 Evaluation Runner")
    parser.add_argument("--use-cloud", action="store_true", help="Use Cloud LLM instead of MockInterpreter")
    parser.add_argument("--dataset", type=str, default=None, help="Custom samples.json path")
    parser.add_argument("--output-dir", type=str, default=None, help="Directory to store evaluation reports")
    args = parser.parse_args()

    runner = EvaluationRunner(
        dataset_path=args.dataset,
        use_mock_interpreter=not args.use_cloud,
        output_dir=args.output_dir,
    )

    print("\n" + "=" * 60)
    print("  PEEXH Evaluation Framework (Phase 5 - RFC-006)")
    print("=" * 60)
    print(f"Samples count: {len(runner.samples)}")
    print(f"Interpreter mode: {'MockInterpreter' if not args.use_cloud else 'CloudLLM'}")

    summary, md_path, json_path = asyncio.run(runner.run_and_export())

    print("\n" + "-" * 60)
    print("  EVALUATION SUMMARY")
    print("-" * 60)
    print(f"Total Samples Evaluated:    {summary.total_samples}")
    print(f"Baseline Avg WER (Raw STT): {summary.baseline_avg_wer * 100:.1f}%")
    print(f"PEEXH Avg WER:              {summary.peexh_avg_wer * 100:.1f}%")
    print(f"WER Improvement:            {summary.wer_improvement_pct:+.1f}%")
    print(f"Intent Match Rate (IMR):    {summary.intent_match_rate * 100:.1f}%")
    print(f"Avg Pipeline Latency:       {summary.avg_total_latency_ms:.1f} ms")
    print(f"Memory Loop Avg Delta:      +{summary.memory_loop_avg_delta * 100:.1f}%")
    print("-" * 60)
    print(f"Reports saved to:")
    print(f"  Markdown: {md_path}")
    print(f"  JSON:     {json_path}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
