"""Report generator creating Markdown and JSON evaluation summaries."""

import json
from pathlib import Path
from typing import List, Optional

from evaluation.models import (
    BaselineResult,
    EvaluationSummary,
    MemoryLoopResult,
    PeexhResult,
)


class ReportGenerator:
    """Formats evaluation results into Markdown documents and JSON artifacts."""

    def __init__(self, output_dir: Optional[str | Path] = None) -> None:
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).resolve().parent / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_markdown(
        self,
        summary: EvaluationSummary,
        baseline_results: List[BaselineResult],
        peexh_results: List[PeexhResult],
        memory_results: List[MemoryLoopResult],
        mode: str = "mock",
    ) -> str:
        """Construct full Markdown report."""
        lines = [
            "# PEEXH Evaluation Report",
            "",
            f"**Generated:** {summary.generated_at.isoformat()}  ",
            f"**Dataset:** {summary.total_samples} samples  ",
            f"**Execution Mode:** {mode}  ",
            "",
            "---",
            "",
            "## 1. Executive Summary",
            "",
            "| Metric | Baseline (Raw STT) | PEEXH Agent Stack | Relative Change / Value |",
            "|---|---|---|---|",
            f"| **Average Word Error Rate (WER)** | {summary.baseline_avg_wer * 100:.1f}% | {summary.peexh_avg_wer * 100:.1f}% | **{summary.wer_improvement_pct:+.1f}%** |",
            f"| **Intent Match Rate (IMR)** | — | {summary.intent_match_rate * 100:.1f}% | Target: ≥ 60.0% |",
            f"| **Average Pipeline Latency** | — | {summary.avg_total_latency_ms:.1f} ms | Target: < 200 ms (mock) |",
            f"| **Memory Loop Delta (Pass 1 → 2)** | — | +{summary.memory_loop_avg_delta * 100:.1f}% | Improvement on repeated utterance |",
            "",
            "---",
            "",
            "## 2. Per-Sample Detailed Benchmark",
            "",
            "| Sample ID | Raw STT Transcript | Intended Target Phrase | PEEXH Proposal | Action | Base WER | PEEXH WER | IMR | Latency |",
            "|---|---|---|---|---|---|---|---|---|",
        ]

        # Map results by sample_id
        base_map = {b.sample_id: b for b in baseline_results}

        for p in peexh_results:
            b = base_map.get(p.sample_id)
            b_wer_str = f"{b.baseline_wer * 100:.0f}%" if b else "—"
            p_wer_str = f"{p.peexh_wer * 100:.0f}%"
            imr_str = "✅" if p.intent_matched else "❌"
            proposal = p.primary_phrase or "(none)"
            lines.append(
                f"| `{p.sample_id}` | *\"{p.raw_transcript}\"* | **\"{p.intended_phrase}\"** | \"{proposal}\" | `{p.agent_action}` | {b_wer_str} | {p_wer_str} | {imr_str} | {p.latency.total_pipeline_ms:.1f}ms |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 3. Memory Loop Personalization (RFC-005 Adaptation)",
            "",
            "| Sample ID | Pass 1 WER | Pass 2 WER (Post-Correction) | WER Delta | Memory Match Activated |",
            "|---|---|---|---|---|",
        ])

        for m in memory_results:
            p1_str = f"{m.pass1_wer * 100:.0f}%"
            p2_str = f"{m.pass2_wer * 100:.0f}%"
            delta_str = f"{m.memory_delta * 100:+.0f}%"
            match_str = "✅ Yes" if m.has_memory_match_pass2 else "❌ No"
            lines.append(
                f"| `{m.sample_id}` | {p1_str} | {p2_str} | **{delta_str}** | {match_str} |"
            )

        # 4. Failure cases & observations
        failure_samples = [p for p in peexh_results if not p.intent_matched or p.peexh_wer >= 0.50]
        lines.extend([
            "",
            "---",
            "",
            "## 4. Failure Cases & Edge Condition Analysis",
            "",
        ])

        if failure_samples:
            for f in failure_samples:
                lines.append(
                    f"- **{f.sample_id}**: Raw *\"{f.raw_transcript}\"* → Intended: *\"{f.intended_phrase}\"*. Action: `{f.agent_action}`. (WER: {f.peexh_wer * 100:.0f}%). PEEXH deferred to `{f.agent_action}` preserving safety."
                )
        else:
            lines.append("No critical intent mismatch failures observed on the curated evaluation set.")

        lines.append("")
        return "\n".join(lines)

    def export_reports(
        self,
        summary: EvaluationSummary,
        baseline_results: List[BaselineResult],
        peexh_results: List[PeexhResult],
        memory_results: List[MemoryLoopResult],
        mode: str = "mock",
    ) -> tuple[Path, Path]:
        """Save both Markdown and JSON reports to disk."""
        md_content = self.generate_markdown(
            summary=summary,
            baseline_results=baseline_results,
            peexh_results=peexh_results,
            memory_results=memory_results,
            mode=mode,
        )

        md_path = self.output_dir / "evaluation_report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        json_data = {
            "summary": summary.model_dump(mode="json"),
            "baseline": [b.model_dump(mode="json") for b in baseline_results],
            "peexh": [p.model_dump(mode="json") for p in peexh_results],
            "memory_loop": [m.model_dump(mode="json") for m in memory_results],
        }

        json_path = self.output_dir / "evaluation_summary.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        return md_path, json_path
