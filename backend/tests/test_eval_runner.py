"""Integration tests for EvaluationRunner orchestrating the full benchmark."""

import pytest
from evaluation.runner import EvaluationRunner


@pytest.mark.anyio
async def test_evaluation_runner_run_all(tmp_path):
    """Verify EvaluationRunner executes all passes and exports valid reports."""
    runner = EvaluationRunner(
        use_mock_interpreter=True,
        use_mock_memory=True,
        output_dir=tmp_path,
    )

    summary, md_path, json_path = await runner.run_and_export()

    assert summary.total_samples == len(runner.samples)
    assert summary.baseline_avg_wer > 0.0
    # Meets RFC-006 Acceptance Criteria:
    # 1. Baseline vs PEEXH improvement >= 10%
    assert summary.wer_improvement_pct >= 10.0
    # 2. Intent match rate >= 60%
    assert summary.intent_match_rate >= 0.60
    # 3. Memory loop delta > 0
    assert summary.memory_loop_avg_delta > 0.0
    # 4. Latency < 200 ms (mock)
    assert summary.avg_total_latency_ms < 200.0

    # Verify report files were generated and non-empty
    assert md_path.exists()
    assert md_path.stat().st_size > 500
    assert json_path.exists()
    assert json_path.stat().st_size > 500
