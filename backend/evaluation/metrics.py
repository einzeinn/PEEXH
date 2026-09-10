"""Evaluation metrics: Word Error Rate (WER), Intent Match Rate (IMR), and Latency."""

import re
from typing import List, Optional
from pydantic import BaseModel, Field


class LatencyBreakdown(BaseModel):
    """Execution timing breakdown across evaluation stages in milliseconds."""
    memory_retrieval_ms: float = 0.0
    llm_interpret_ms: float = 0.0
    scorer_ms: float = 0.0
    total_pipeline_ms: float = 0.0


def normalize_tokens(text: str) -> List[str]:
    """Normalize text into lowercase alphanumeric word tokens without punctuation."""
    if not text:
        return []
    # Replace hyphens and punctuation with spaces, keep alphanumeric
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return cleaned.split()


def calculate_wer(reference: str, hypothesis: str) -> float:
    """Calculate Word Error Rate (WER) using Levenshtein distance on word tokens.
    
    WER = (Substitutions + Deletions + Insertions) / N_reference
    """
    ref_words = normalize_tokens(reference)
    hyp_words = normalize_tokens(hypothesis)

    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    r_len = len(ref_words)
    h_len = len(hyp_words)

    # DP matrix of size (r_len + 1) x (h_len + 1)
    dp = [[0] * (h_len + 1) for _ in range(r_len + 1)]

    for i in range(r_len + 1):
        dp[i][0] = i
    for j in range(h_len + 1):
        dp[0][j] = j

    for i in range(1, r_len + 1):
        for j in range(1, h_len + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                substitution = dp[i - 1][j - 1] + 1
                insertion = dp[i][j - 1] + 1
                deletion = dp[i - 1][j] + 1
                dp[i][j] = min(substitution, insertion, deletion)

    distance = dp[r_len][h_len]
    return float(distance / r_len)


def calculate_imr(
    intended: str,
    primary_phrase: Optional[str] = None,
    candidates: Optional[List[str]] = None,
) -> bool:
    """Evaluate Intent Match Rate (IMR).
    
    Returns True if primary_phrase matches intended (normalized), or
    if intended matches any candidate in candidates.
    """
    intended_norm = " ".join(normalize_tokens(intended))
    if not intended_norm:
        return False

    if primary_phrase:
        primary_norm = " ".join(normalize_tokens(primary_phrase))
        if primary_norm == intended_norm:
            return True

    if candidates:
        for cand in candidates:
            cand_norm = " ".join(normalize_tokens(cand))
            if cand_norm == intended_norm:
                return True

    return False
