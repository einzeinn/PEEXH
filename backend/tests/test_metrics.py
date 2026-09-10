"""Unit tests for evaluation metrics (WER, IMR, Latency)."""

import pytest
from evaluation.metrics import calculate_imr, calculate_wer, normalize_tokens


def test_normalize_tokens():
    """Verify punctuation removal, lowercasing, and whitespace tokenization."""
    text = "Hello, World! I'm here... -- testing."
    tokens = normalize_tokens(text)
    assert tokens == ["hello", "world", "i", "m", "here", "testing"]

    assert normalize_tokens("") == []
    assert normalize_tokens(None) == []


def test_calculate_wer_identical():
    """Identical reference and hypothesis must yield 0.0 WER."""
    assert calculate_wer("I need water", "I need water") == 0.0
    assert calculate_wer("I NEED WATER!", "i need water.") == 0.0


def test_calculate_wer_empty():
    """Handling empty inputs."""
    assert calculate_wer("", "") == 0.0
    assert calculate_wer("water", "") == 1.0
    assert calculate_wer("", "water") == 1.0


def test_calculate_wer_substitutions():
    """One substitution in a 4-word reference should be 0.25 WER."""
    ref = "I need some water"
    hyp = "I need more water"
    assert calculate_wer(ref, hyp) == 0.25


def test_calculate_wer_deletions_insertions():
    """Test deletion and insertion counting."""
    ref = "I need some water"
    # Deletion: "I need water" (dropped "some") -> 1 deletion / 4 words = 0.25
    assert calculate_wer(ref, "I need water") == 0.25

    # Insertion: "I need some cold water" (added "cold") -> 1 insertion / 4 words = 0.25
    assert calculate_wer(ref, "I need some cold water") == 0.25


def test_calculate_imr_primary_match():
    """Verify IMR matches primary proposed phrase."""
    intended = "I need some water"
    assert calculate_imr(intended, primary_phrase="I need some water.") is True
    assert calculate_imr(intended, primary_phrase="i need some water") is True
    assert calculate_imr(intended, primary_phrase="I need food") is False


def test_calculate_imr_candidate_match():
    """Verify IMR falls back to candidate list match."""
    intended = "Can I have a drink?"
    assert calculate_imr(
        intended,
        primary_phrase="I need some water",
        candidates=["Can I have a drink?", "Please help"],
    ) is True

    assert calculate_imr(
        intended,
        primary_phrase="I need some water",
        candidates=["No thank you", "Please help"],
    ) is False
