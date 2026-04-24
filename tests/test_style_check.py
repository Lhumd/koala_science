import pytest

from tools.style_check import (
    StyleCheckResult,
    check_uniqueness,
    jaccard_similarity,
    tokenize,
)


def test_tokenize_basic() -> None:
    tokens = tokenize("The authors' claim rests on Figure 3 ablations.")
    assert "claim" in tokens
    assert "authors" in tokens
    assert "figure" in tokens or "fig" in tokens


def test_tokenize_lowercases_and_strips_punctuation() -> None:
    tokens = tokenize("Great Paper!!! Loved it.")
    assert "great" in tokens
    assert "!" not in " ".join(tokens)


def test_tokenize_drops_stopwords() -> None:
    tokens = tokenize("the a an of in on at to")
    assert len(tokens) == 0


def test_jaccard_identical() -> None:
    a = "This paper has novel contributions to reinforcement learning."
    assert jaccard_similarity(a, a) == pytest.approx(1.0)


def test_jaccard_disjoint() -> None:
    a = "reinforcement learning policy gradient"
    b = "bayesian inference variational mcmc"
    assert jaccard_similarity(a, b) == pytest.approx(0.0)


def test_jaccard_partial_overlap() -> None:
    a = "reinforcement learning policy gradient"
    b = "reinforcement learning value function"
    sim = jaccard_similarity(a, b)
    assert 0.2 < sim < 0.6


def test_check_uniqueness_allows_first_comment() -> None:
    result = check_uniqueness("First insightful comment about the ablation.", [])
    assert result.is_unique
    assert result.max_similarity == 0.0


def test_check_uniqueness_rejects_near_duplicate() -> None:
    prior = ["This paper's ablations are underpowered relative to the claims made."]
    new = "This paper's ablations are underpowered relative to the claims made."
    result = check_uniqueness(new, prior)
    assert not result.is_unique
    assert result.max_similarity > 0.9


def test_check_uniqueness_rejects_near_template() -> None:
    prior = [
        "Key contributions as I read them include X and Y. One concern is Z."
    ]
    new = "Key contributions as I read them include A and B. One concern is C."
    result = check_uniqueness(new, prior, threshold=0.5)
    assert not result.is_unique


def test_check_uniqueness_allows_substantively_different() -> None:
    prior = [
        "The Lipschitz constant bound in Theorem 2 requires a stronger assumption.",
    ]
    new = "Figure 4's sim-to-real gap is concerning; real-robot demos would strengthen this."
    result = check_uniqueness(new, prior, threshold=0.6)
    assert result.is_unique


def test_check_uniqueness_finds_max_over_multiple_priors() -> None:
    prior = [
        "Unrelated comment about a different paper.",
        "This paper's novelty claim is weak versus [prior work from 2023].",
    ]
    new = "This paper's novelty claim is weak versus [prior work from 2024]."
    result = check_uniqueness(new, prior, threshold=0.6)
    assert not result.is_unique
    assert result.most_similar_index == 1
