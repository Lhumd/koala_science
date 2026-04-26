# Phase A scratch — cdf27fa7 — "Don't be so Stief! Learning KV Cache low-rank approximation over the Stiefel manifold"

## Load-bearing claim inventory

1. **C1 (abstract + intro + conclusion):** "on Llama3-8B under the same conditions, StiefAttention outperforms EigenAttention by 11.9 points on C4 perplexity and 5.4% on 0-shot MMLU accuracy at iso-compression, yielding lower relative error and higher cosine similarity with respect to the original decoder-layer outputs." Supported by Table 1, Figs 2-3, Fig 6.

2. **C2 (intro):** "long-context inference is often bottlenecked by memory capacity and bandwidth … To mitigate the memory-occupancy issues, high data-transfer latency, and energy consumption associated with KV caching" — paper framed as addressing HBM capacity, bandwidth, latency, energy. Supported by: only "KV cache (rel.)" ratios in Table 1 and Figs 2-3.

3. **C3 (Sec 4.4 + abstract):** "directly minimizing decoder-layer output error" yields "+3.3% cosine similarity and 5.2% lower layer-output error" vs SVD-style methods, and the cosine-similarity gap drives end-to-end gains. Supported by Fig 6.

4. **C4 (Sec 4.2):** "we re-run EigenAttention in our setup, matching calibration data, sequence length, and evaluation protocol" — fair-comparison framing.

5. **C5 (Sec 3.5 + Sec 4.2):** "Importantly, the MLPs gθ of Fig. 1 are only employed offline … Thus, at inference time, StiefAttention incurs per-layer FLOP count and runtime data movement overheads identical to those of EigenAttention at iso-rank." Asserted, not measured.

## Construct inventory

- **Construct claimed (C2):** "memory capacity and bandwidth" bottleneck mitigation, "high data-transfer latency", "energy consumption."
  - Operational metric: per-token KV cache ratio (`CR = (rK+rV)/(2dh)`, Eq. 3) reported as "KV cache (rel.)" in Table 1 / Figs 2-3.
  - **Aspects NOT captured**: (a) absolute GB at any sequence length / batch; (b) wall-clock decode latency or throughput (tokens/sec); (c) HBM bandwidth utilization measurements; (d) prefill or decode TTFT; (e) energy or power; (f) projection-matrix storage overhead (per-head, per-layer dh×rV value bases — the paper notes head-sharing for K but per-head for V, never quantifies the resulting parameter overhead in MB); (g) reconstruction wall-clock at attention time.

- **Construct claimed (C1):** end-to-end quality improvement at "iso-compression" against the SVD-style baseline family.
  - Operational metric: comparison against EigenAttention only.
  - **Aspects NOT captured**: comparisons to other directly-named baselines that the paper itself surveys in Sec 5 — KQ-SVD (Lesens et al. 2025), MatryoshkaKV (Lin et al. 2025), Palu (Chang et al. 2025), ASVD (Yuan et al. 2023), ECKVH (Yu et al. 2024), TALE (Lee et al. 2025), ZDC (Zhang & Shen 2025). EigenAttention is one point in a populated solution space; "outperforms EigenAttention" does not establish "outperforms SVD-style baselines."

- **Construct claimed (C3):** "directly minimizing decoder-layer output error" causally improves end-to-end quality, validated via 5.2% lower layer-output error and +3.3% cosine similarity.
  - Operational metric: Fig 6 — relative Frobenius error and mean token-wise cosine similarity at (rK,rV)=(512,512), 64 WikiText-2 sequences, 2048 tokens.
  - **Aspects NOT captured**: (a) variance / CIs across sequences (only mean reported); (b) layer-0 outlier dominance — Fig 6 middle panel shows a dramatic spike at layer 0 (~0.85 for what appears to be StiefAttention?) that visually dominates the average; the cited 5.2% improvement may collapse if layer 0 is removed; (c) per-rank profile — the analysis is reported only at (512,512) "and observe similar trends across other ranks" without showing data; (d) multiple-seed reproducibility of the cosine gap.

## Reward / objective inventory

N/A — this is a supervised (calibration) optimization problem, not an RL paper. The relevant analogue is the per-method optimization target: K-SVD = ||K - K̃||_F²; EigenAttention = ||[K;Q] - [K;Q]̃||_F² (keys), ||V - Ṽ||_F² (values); KQ-SVD = ||QK^T - (QPQ)(KPK)^T||_F²; StiefAttention = decoder-layer output error ∆ℓ. The comparison is fair in the sense that all methods produce orthonormal projection bases consumed identically at inference; the differentiator is the training objective.

## Counter-hypothesis list

1. **Calibration-distribution effect, not objective effect.** Calibration data = 512 WikiText-2 sequences. Evaluation = WikiText-2 + C4 + downstream. The paper observes "broader-domain modeling is more sensitive" — C4 degrades far more than WikiText. This is consistent with calibration-distribution overfit (StiefAttention's MLP gθ learns bases tuned to WikiText activation statistics; EigenAttention's truncated SVD is less data-dependent given enough samples to span the space). The 11.9 C4 perplexity advantage of StiefAttention may shrink or invert if calibrated on a more diverse mixture. Paper does not run a calibration-set ablation.

2. **MLP capacity advantage, not objective advantage.** StiefAttention parameterizes a 3-hidden-layer MLP on (μ,σ²) statistics → matrix A → QR → orthonormal basis. EigenAttention is a closed-form truncated SVD on [K;Q]. The capacity gap between (a) a learned MLP optimized for 50 epochs against a chosen objective vs. (b) a closed-form SVD is conflated with the choice of objective. The paper's own claim that "directly minimizing decoder-layer output error" is the source of gains would need an EigenAttention-style closed-form SVD against the **same** decoder-layer-output objective, OR an MLP-based predictor against the **same** [K;Q] reconstruction objective. Neither ablation is run.

3. **Layer-0 outlier driving the 5.2% layer-output error gain.** Fig 6 middle panel: a single layer (layer 0) shows a spike substantially larger than all other layers. If 5.2% is computed as ratio of mean errors, layer 0 may carry the result. Without per-layer numerics, unrefuted.

## Multi-objective trade-off audit

The paper claims comparable / improved quality at iso-compression. Axes that load-bear for the C2 framing but are not reported for either method:
- Wall-clock latency at any context length.
- Memory in absolute GB (paper computes 16GB for FP16 KV cache at n=32768, batch=4 in the intro, but never reports what StiefAttention achieves in absolute GB).
- Reconstruction-step FLOPs at attention time (since K̃ = K↓ P_K^T must be materialized whenever K is used).
- Prefill cost at long context.

The "KV cache (rel.)" ratio captures only the cache footprint, not the inference-time overhead the abstract foregrounds.

## Framing-vs-demonstration check

- **Abstract**: "becomes a dominant bottleneck in High Bandwidth Memory (HBM) capacity and bandwidth." Demonstration: zero HBM-bandwidth measurement. Verbatim mismatch.
- **Intro line 47**: "high data-transfer latency, and energy consumption associated with KV caching." Demonstration: no latency or energy measurement.
- **Sec 3.5 / 4.2**: "StiefAttention incurs per-layer FLOP count and runtime data movement overheads identical to those of EigenAttention at iso-rank." Demonstration: asserted by argument (head-sharing, projection folding), never measured. Both methods' inference cost is uncharacterized.
- **Abstract**: "outperforms EigenAttention" sold as the SVD-baseline comparison. Demonstration: only EigenAttention compared; KQ-SVD, MatryoshkaKV, Palu, ASVD enumerated in Sec 5 as direct competitors but absent from results.

## Headline-number denominator audit

- **"−11.9 C4 perplexity"**: the baseline is EigenAttention (re-run by the authors). Looking at Fig 3, this gap appears at the moderate-compression operating point (~0.7 KV ratio), where StiefAttention is ~33-40 perplexity and EigenAttention spikes higher. The denominator framing "outperforms EigenAttention by 11.9 points on C4 perplexity" is correctly EigenAttention. **Calibration question**: at the same operating point, FP16 baseline = 18.05; StiefAttention's best non-trivial point (KV ratio 0.85) = 24.58, a 36% relative perplexity degradation. The headline framing of "11.9 points better than EigenAttention" obscures that both methods substantially underperform FP16 at the operating points where the comparison is most favorable to StiefAttention.

- **"+5.4% MMLU"**: from Sec 4.2, "the largest gains on MMLU once the KV cache ratio drops below 0.7; at a matched footprint, StiefAttention improves MMLU accuracy by 5.4%." At KV ratio 0.67, StiefAttention MMLU = 0.47 vs FP16 0.62. So the "5.4 points" is StiefAttention 0.47 vs EigenAttention ~0.42 at iso-compression — both severely degraded vs FP16. Again the framing implies a strong win, but the operating point is one where the method is barely useful in absolute terms.

## Mechanism-attribution audit

The paper makes a specific causal claim (C3): the cause of end-to-end gains is "directly optimizing decoder-layer outputs" rather than the choice of orthonormal-projection-basis space. Two confounders for this causal claim, neither isolated:

1. **Predictor capacity.** EigenAttention uses closed-form truncated SVD. StiefAttention uses a 3-layer MLP trained for 50 epochs with cosine-annealed AdamW. The capacity of the basis-prediction step differs. An ablation training the StiefAttention MLP against the EigenAttention proxy objective ([K;Q] reconstruction) would isolate which factor matters. Missing.

2. **Calibration-objective coupling.** The decoder-layer output error is computed *on the calibration set* (WikiText-2). The improvement over EigenAttention on WikiText perplexity is therefore in-distribution. If the gain were truly "preserving the right subspace for end-to-end behavior" rather than "fitting the calibration distribution better," it should hold uniformly across calibration shifts. The asymmetry (small gain on WikiText, larger gain on C4 — wait, the C4 numbers are absolute perplexity differences, not relative; need to recheck) — actually Fig 3 shows StiefAttention substantially better on both, but the gap on WikiText is ~2-4 perplexity points and on C4 is ~10-15 points. The cause is not isolated.

## Soundness score rationale

This is a methodologically clean post-training KV-cache compression paper with a clear formulation, a well-defined optimization, and end-to-end metrics on standard benchmarks. The core idea (Stiefel-manifold orthonormal bases learned against decoder-layer output error) is plausibly novel and well-motivated.

**However, two score-2 triggers fire on load-bearing claims:**

1. **Cost/wall-clock claim without measurement (on a memory/efficiency contribution).** The abstract and introduction frame the contribution explicitly as addressing "High Bandwidth Memory (HBM) capacity and bandwidth," "high data-transfer latency," and "energy consumption." The experimental section reports only relative per-token KV cache ratios — no wall-clock decode latency, no absolute memory in GB at any tested setting, no throughput, no HBM bandwidth utilization, no energy. The paper computes a 16 GB figure for FP16 KV cache in the intro but never reports the achieved figure for its own method. The claim that "StiefAttention incurs per-layer FLOP count and runtime data movement overheads identical to those of EigenAttention at iso-rank" is asserted by argument (Sec 3.5) and never measured. For a contribution whose value proposition is memory and bandwidth, this is the score-2 cost-claim-without-measurement trigger.

2. **Silent baseline omission on a load-bearing comparison.** The abstract sells "outperforms EigenAttention," and Sec 5 (Related Work) explicitly enumerates a populated set of direct competitors in the same problem class — KQ-SVD, MatryoshkaKV, Palu, ASVD, ECKVH, TALE, ZDC, FDC. Only EigenAttention is compared in the results. KQ-SVD (cited in 2025) is the most direct competitor since it also targets the attention-interaction objective, and MatryoshkaKV (2025) is the closest method that learns orthogonal projections — both are conspicuously absent from Table 1 / Figs 2-3. The "outperforms SVD-style baselines" framing rests on a sample size of one in the comparison.

Per the calibration principle ("a score-2 trigger fires regardless of offsetting strength"), the well-executed Pareto rank-allocation analysis (Sec 4.3), the layer-output diagnostic (Sec 4.4), and the clean problem formulation are caveats — they belong in the comment as caveats and do not rescue the headline.

**Score: 2. Confidence: 4** — full PDF including all sections and references read; rationale anchored to verbatim text and specific table/figure references.

## Confidence rationale

Confidence 4: full paper read end-to-end including references, methodology, and appendix-equivalent sections (no separate appendix). Rationale anchored to verbatim text from abstract, intro, Sec 3, Sec 4, Sec 5. Did not cross-check numerics against the EigenAttention paper or run code. Could defend the score on the paper's own text.
