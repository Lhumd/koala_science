# Phase B Full Report — StiefAttention (cdf27fa7)

**Paper:** Don't be so Stief! Learning KV Cache low-rank approximation over the Stiefel manifold
**Soundness score:** 2 / **Confidence:** 4
**Primary trigger:** Cost / wall-clock claim without measurement on a memory-and-bandwidth contribution
**Secondary trigger:** Silent baseline omission on the load-bearing "outperforms SVD-style methods" comparison (only EigenAttention compared)

---

## Headline empirical claims

1. **C1 (abstract + intro + conclusion):** "on Llama3-8B under the same conditions, StiefAttention outperforms EigenAttention by 11.9 points on C4 perplexity and 5.4% on 0-shot MMLU accuracy at iso-compression, yielding lower relative error and higher cosine similarity with respect to the original decoder-layer outputs." Supported by Table 1, Figs 2-3, Fig 6.
2. **C2 (intro):** "long-context inference is often bottlenecked by memory capacity and bandwidth … To mitigate the memory-occupancy issues, high data-transfer latency, and energy consumption associated with KV caching" — paper framed as addressing HBM capacity, bandwidth, latency, energy.
3. **C3 (Sec 4.4 + abstract):** "directly minimizing decoder-layer output error" yields "+3.3% cosine similarity and 5.2% lower layer-output error" vs SVD-style methods, and the cosine-similarity gap drives end-to-end gains. Supported by Fig 6.
4. **C4 (Sec 4.2):** "we re-run EigenAttention in our setup, matching calibration data, sequence length, and evaluation protocol" — fair-comparison framing.
5. **C5 (Sec 3.5 + Sec 4.2):** "Importantly, the MLPs gθ of Fig. 1 are only employed offline … Thus, at inference time, StiefAttention incurs per-layer FLOP count and runtime data movement overheads identical to those of EigenAttention at iso-rank." **Asserted, not measured.**

---

## Construct-validity audit

| Claim | Construct claimed | Operational metric | Unmeasured aspect |
|---|---|---|---|
| C2 | "Memory capacity and bandwidth", "data-transfer latency", "energy" | Per-token KV cache ratio CR = (rK+rV)/(2dh) reported as "KV cache (rel.)" in Table 1 / Figs 2-3 | (a) absolute GB at any sequence length / batch; (b) wall-clock decode latency or throughput (tokens/sec); (c) HBM bandwidth utilization; (d) prefill or TTFT; (e) energy or power; (f) projection-matrix storage overhead (per-head, per-layer dh×rV value bases — paper notes head-sharing for K but per-head for V, never quantifies the resulting parameter overhead in MB); (g) reconstruction-step FLOPs at attention time. |
| C1 | End-to-end quality at iso-compression vs the SVD-style baseline family | Comparison against EigenAttention only | KQ-SVD (Lesens et al. 2025), MatryoshkaKV (Lin et al. 2025), Palu (Chang et al. 2025), ASVD (Yuan et al. 2023), ECKVH (Yu et al. 2024), TALE (Lee et al. 2025), ZDC (Zhang & Shen 2025), FDC — all enumerated in §5 as direct competitors but absent from results. EigenAttention is one point in a populated solution space; "outperforms EigenAttention" does not establish "outperforms SVD-style baselines." |
| C3 | "Directly minimizing decoder-layer output error" causally improves end-to-end quality, validated via 5.2% lower layer-output error and +3.3% cosine similarity | Fig 6 — relative Frobenius error and mean token-wise cosine similarity at (rK,rV)=(512,512), 64 WikiText-2 sequences, 2048 tokens | (a) variance / CIs across sequences (only mean reported); (b) layer-0 outlier dominance — Fig 6 middle panel shows a dramatic spike at layer 0 visually dominating the average; the cited 5.2% improvement may collapse if layer 0 is removed; (c) per-rank profile reported only at (512,512) "and observe similar trends across other ranks" without showing data; (d) multi-seed reproducibility of the cosine gap. |

---

## Reward / objective audit (post-training calibration objectives)

This is supervised calibration, not RL. The relevant analogue is each method's optimization target:

| Method | Calibration objective | Predictor |
|---|---|---|
| K-SVD | ‖K − K̃‖_F² | Closed-form truncated SVD |
| EigenAttention | ‖[K;Q] − [K;Q]̃‖_F² (keys), ‖V − Ṽ‖_F² (values) | Closed-form truncated SVD |
| KQ-SVD | ‖QKᵀ − (Q P_Q)(K P_K)ᵀ‖_F² | Closed-form |
| StiefAttention | Decoder-layer output error Δℓ | 3-hidden-layer MLP, 50 epochs, AdamW, cosine schedule |

The methods produce orthonormal projection bases consumed identically at inference; the differentiator is (a) the training objective AND (b) the predictor capacity (closed-form SVD vs learned MLP). The paper claims (a) is the cause of gains; the empirical attribution is not isolated from (b) — see Counter-hypothesis 2.

---

## Counter-hypothesis attempts

1. **CH1 — Calibration-distribution effect, not objective effect.** Calibration data = 512 WikiText-2 sequences. Evaluation = WikiText-2 + C4 + downstream. The paper observes "broader-domain modeling is more sensitive" — C4 degrades more than WikiText. This is consistent with calibration-distribution overfit (StiefAttention's MLP gθ learns bases tuned to WikiText activation statistics; EigenAttention's truncated SVD is less data-dependent given enough samples to span the space). The 11.9 C4 perplexity advantage of StiefAttention may shrink or invert if calibrated on a more diverse mixture. **No calibration-set ablation reported. Unrefuted.**
2. **CH2 — MLP capacity advantage, not objective advantage.** StiefAttention parameterizes a 3-layer MLP on (μ, σ²) statistics → matrix A → QR → orthonormal basis. EigenAttention is a closed-form truncated SVD on [K;Q]. The capacity gap between (a) a learned MLP optimized for 50 epochs against a chosen objective vs. (b) a closed-form SVD is conflated with the choice of objective. The paper's causal attribution (objective drives gains) would need an EigenAttention-style closed-form SVD against the **same** decoder-layer-output objective, OR an MLP-based predictor against the **same** [K;Q] reconstruction objective. **Neither ablation is run.**
3. **CH3 — Layer-0 outlier driving the 5.2% layer-output error gain.** Fig 6 middle panel shows a single layer-0 spike substantially larger than all other layers. If 5.2% is computed as ratio of mean errors, layer 0 may carry the result. **No per-layer numerics provided. Unrefuted.**

---

## Mechanism-attribution audit

The paper makes a specific causal claim (C3): the cause of end-to-end gains is "directly optimizing decoder-layer outputs" rather than the choice of orthonormal-projection-basis space.

Two confounders for this causal claim, neither isolated:

1. **Predictor capacity.** EigenAttention uses closed-form truncated SVD. StiefAttention uses a 3-layer MLP trained for 50 epochs. The capacity of the basis-prediction step differs.
2. **Calibration-objective coupling.** The decoder-layer output error is computed on the calibration set (WikiText-2). Improvement over EigenAttention on WikiText perplexity is therefore in-distribution; the asymmetry between WikiText (~2-4 pp gap) and C4 (~10-15 pp gap) does not isolate calibration-distribution effect from objective effect.

This is a coupled-novelty pattern: novelty A = decoder-output objective; novelty B = MLP-based learned predictor. Ablation isolating A from B would require the cross-product 2×2 of {objective × predictor}.

---

## Multi-objective trade-off audit

The paper claims comparable / improved quality at iso-compression. Axes that load-bear for the C2 framing but are not reported for either method:
- Wall-clock latency at any context length.
- Memory in absolute GB (paper computes 16 GB for FP16 KV cache at n=32768, batch=4 in the intro, but never reports what StiefAttention achieves in absolute GB).
- Reconstruction-step FLOPs at attention time (since K̃ = K↓ P_Kᵀ must be materialized whenever K is used).
- Prefill cost at long context.

The "KV cache (rel.)" ratio captures only the cache footprint, not the inference-time overhead the abstract foregrounds.

---

## Framing-vs-demonstration audit

- **Abstract verbatim:** "becomes a dominant bottleneck in High Bandwidth Memory (HBM) capacity and bandwidth." **Demonstration:** zero HBM-bandwidth measurement.
- **Intro l.47:** "high data-transfer latency, and energy consumption associated with KV caching." **Demonstration:** no latency or energy measurement.
- **§3.5 / §4.2:** "StiefAttention incurs per-layer FLOP count and runtime data movement overheads identical to those of EigenAttention at iso-rank." **Demonstration:** asserted by argument (head-sharing, projection folding), never measured. Both methods' inference cost is uncharacterized.
- **Abstract:** "outperforms EigenAttention" sold as the SVD-baseline comparison. **Demonstration:** only EigenAttention compared; KQ-SVD, MatryoshkaKV, Palu, ASVD enumerated in §5 as direct competitors but absent.

**Headline-number denominator audit.** "−11.9 C4 perplexity": baseline = EigenAttention re-run by authors. At KV ratio ~0.7 in Fig 3, StiefAttention is ~33-40 perplexity vs EigenAttention's spike. The "11.9 better than EigenAttention" framing obscures that StiefAttention's best non-trivial point (KV ratio 0.85) is 24.58 vs FP16 baseline 18.05 — a 36% relative degradation. "+5.4% MMLU" similarly: StiefAttention 0.47 vs EigenAttention ~0.42 at iso-compression vs FP16 0.62 — both severely degraded vs FP16. The framing implies a strong win; the operating point is one where the method is barely useful in absolute terms.

---

## Weaknesses (severity)

- **[Major]** Cost claim without measurement: contribution framed as memory/bandwidth/latency/energy; experimental section reports zero wall-clock, zero absolute-GB, zero bandwidth, zero energy.
- **[Major]** Silent baseline omission: KQ-SVD, MatryoshkaKV, Palu, ASVD, ECKVH, TALE, ZDC, FDC enumerated in §5 as direct competitors; only EigenAttention appears in Table 1 / Figs 2-3.
- **[Moderate]** Coupled-novelty: objective change (decoder-layer-output error) confounded with predictor change (MLP vs closed-form SVD). 2×2 ablation missing.
- **[Moderate]** Calibration-distribution overfit risk: only WikiText-2 used for calibration; differential degradation on C4 unaddressed by calibration-set ablation.
- **[Minor]** Layer-0 outlier may drive Fig 6 5.2% claim; no per-layer numerics.
- **[Minor]** No variance / CI on Fig 6 mean estimates.

---

## Defense paragraph

If challenged on the cost-claim trigger: the abstract verbatim frames "memory capacity and bandwidth" as the bottleneck and intro l.47 explicitly cites "data-transfer latency" and "energy"; §4 reports only KV cache ratios — no wall-clock, no absolute GB, no bandwidth utilization, no energy. The §3.5 assertion that "StiefAttention incurs per-layer FLOP count and runtime data movement overheads identical to those of EigenAttention" is argument, not measurement. If challenged on the silent-baseline trigger: §5 enumerates KQ-SVD (cited 2025, the most direct competitor since it also targets the attention-interaction objective), MatryoshkaKV (2025, the closest method that learns orthogonal projections), Palu, ASVD, ECKVH, TALE, ZDC, FDC by name; Table 1 / Figs 2-3 contain exactly two methods (StiefAttention + EigenAttention). The "outperforms SVD-style methods" framing rests on n=1.

The well-executed Pareto rank-allocation analysis (§4.3), the layer-output diagnostic (§4.4), and the clean problem formulation are caveats, not score-rescuers per the calibration principle.
