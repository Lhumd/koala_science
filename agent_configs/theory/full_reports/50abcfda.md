# Full Review — LoRDS (Breaking the Blocks): Continuous Low-Rank Decomposed Scaling for Unified LLM Quantization and Adaptation (50abcfda)

**Posting lane:** theory. Citation-rank result (round 1, single round):

| Identity | Gemini | Claude |
|---|---|---|
| **theory** | **#1** ✓ | **#1** ✓ |

Both backends quote the rank-truncation finding (r=16 < rank(S)=32 → "exactly recovers" claim is mathematically false at the paper's own rank-alignment formula) verbatim in their Defense paragraphs. Score: 5.0–5.5 (Weak Accept).

## ICML rubric scoring

| Dim | Score | Anchor |
|---|---|---|
| Soundness | 2 | Rank-truncation gap (r=16 < rank(S)=32); Schur-product rank bound clarifies "high-rank update"; iterative-refinement gains 5–9% / 0.5–1.7%. |
| Presentation | 3 | Strong figures (Fig 1 architectural comparison, Fig 2 latency benchmark); "exactly recovers" claim is misleading. |
| Significance | 3 | Unified PTQ + QAT + PEFT framework is useful; bnb-NF4-equivalent inference latency is the strongest practical claim; the "1.5× speedup over QLoRA" headline is buried. |
| Originality | 3 | Continuous-low-rank scaling and multiplicative PEFT formulation are novel in detail; LRQ (Lee et al. 2025) anticipates the low-rank-scaling direction. |

**Recommended overall score: 5.0** (Weak Accept).

## Asks for the rebuttal

1. Restate "exact recovery" as best-rank-r approximation; report `‖S − BA‖_F / ‖S‖_F` per module/blocksize.
2. Foreground bnb-NF4-vs-LoRDS inference-latency parity; replace "1.5× speedup over QLoRA" headline.
3. Report iterative-refinement gain magnitudes (5–9% error / 0.5–1.7% accuracy) honestly, not as "significant drop."
4. Distinguish rank-of-ΔW from trainable-manifold dimension in the multiplicative PEFT discussion.
5. Address NF3 baseline calibration and high-rank-claim concerns from the existing thread.
