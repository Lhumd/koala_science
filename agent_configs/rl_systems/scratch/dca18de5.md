# Phase A scratch — dca18de5 (MetaOthello: Controlled Study of Multiple World Models in Transformers)

## Headline empirical claims (load-bearing)

1. **Abstract:** *"transformers trained on mixed-game data do not partition their capacity into isolated sub-models; instead, they converge on a mostly shared board-state representation that transfers causally across variants."*
2. **Abstract:** *"Linear probes trained on one variant can intervene on another's internal state with effectiveness approaching that of matched probes."*
3. **Abstract:** *"For isomorphic games with token remapping, representations are equivalent up to a single orthogonal rotation that generalizes across layers."*
4. **Abstract:** *"When rules partially overlap, early layers maintain game-agnostic representations while a middle layer identifies game identity, and later layers specialize."*

## Construct inventory

### Construct A: shared board-state representation across variants
- Operational metric: cosine similarity between per-layer Procrustes-aligned probe weights for Classic vs variant probes (Fig 2). Reaches ~0.98 after Procrustes alignment.
- Random baseline (raw): ~0.03; random baseline (Procrustes-aligned): ~0.68. The 0.98 result exceeds Procrustes-random by ~0.30.
- 95% CIs computed across 192 probe dimensions (board tiles), NOT across training seeds.
- ✓ Construct spans claim reasonably; the +0.30 over random baseline is substantive.

### Construct B: cross-probe causal intervention efficacy
- Operational metric: prediction error after intervention via cross-probe (Fig 3). Cross-probe ≈ 0.2-0.3 vs correct-probe ≈ 0.2 vs null ≈ 1.3-2.1.
- The "approaching matched probes" framing is honest: cross is 0.2-0.3 vs correct 0.2 (50% higher in worst case for DelFlank).
- ✓ Strong supporting evidence; framing is calibrated (uses "approaching", not "matches").

### Construct C: isomorphic equivalence via single orthogonal rotation
- Operational measurement: orthogonal Procrustes Ω ∈ R^512×512 fit on Classic-Iago paired activations (training set), then applied at intervention layer ℓ' on test set (Fig 4). α-score recovery near baseline at all layers except 8.
- Random baseline: α ≈ -2.9 for "Iago moves on Classic sequences" without rotation. Post-rotation: α ≈ 0.95-0.99.
- ✓ Train/test split present; massive recovery vs the no-rotation baseline.

### Construct D: layerwise routing structure
- Operational measurement: probe accuracy on differing tiles (Fig 5a), game-ID probe accuracy (Fig 5b), causal steering ∆α (Fig 5c), DelFlank steering at different layers (Fig 6).
- Classic-NoMidFlip: Layer 5 is the critical routing layer (game-ID probe and causal steering both peak there).
- Classic-DelFlank: Layer 2-3 are the effective steering layers; Layer 5 has Δα ≈ 0 (no effect).
- **Variant-pair-dependent routing layer.** The abstract's "middle layer identifies game identity" framing is most strongly supported for Classic-NoMidFlip; for Classic-DelFlank, routing happens earlier (Layers 2-3).
- The paper does acknowledge this in Sec 5.6 ("intervention at Layer 5 ... has essentially no effect (Δα ≈ 0). Crucially, early-layer steering also improves the downstream DelFlank board representation"). So the routing layer is variant-pair-specific, not universally "middle".

## Reward / objective audit
- Models trained on next-token prediction (cross-entropy) on Othello move sequences. Standard.
- Custom α metric (Eq 1): normalized KL divergence accounting for varying move set sizes. Well-motivated.

## Counter-hypothesis list

1. **Procrustes alignment can match arbitrary 512-dim representations to some extent.** Addressed by reporting random Procrustes baselines (Fig 2). The 0.98 vs 0.68 baseline is +0.30, substantive but not enormous.

2. **Single-seed (no seed-level CIs).** The 95% CIs in Fig 2-6 are across probe dimensions or move numbers, NOT across multiple training seeds. The Tab 1 trained-model α-scores show one model per condition. Single-seed is field-norm for Othello-GPT mechanistic interpretability work (Li et al. 2024, Nanda et al. 2023) but limits the strength of the empirical claims.

3. **The "early layers game-agnostic / middle layers identify game / later layers specialize" generalization is shown for Classic-NoMidFlip but the routing layer differs for Classic-DelFlank.** The paper's own evidence (Sec 5.6) shows variant-dependent routing. The abstract's framing is most accurate for Classic-NoMidFlip.

4. **Limitations explicitly acknowledged:** Sec 7 — "8-layer (d_model = 512) architecture", "50/50 mixtures", "pairwise game mixtures", "linear probes; nonlinear structure ... may reveal additional mechanisms".

## Multi-objective trade-off audit
Not applicable for an interpretability paper.

## Framing-vs-demonstration check

- "Approaching that of matched probes" — Fig 3 cross-probe (0.2-0.3) vs correct-probe (0.2). Honest framing for the result.
- "Mostly shared board-state representation" — supported by Procrustes alignment + cross-probe intervention. Honest.
- "When rules partially overlap, early layers maintain game-agnostic representations while a middle layer identifies game identity" — strongest for Classic-NoMidFlip; for Classic-DelFlank the routing layer differs. The "middle layer" framing is variant-pair-specific. Minor framing nuance, not a Soundness concern.

## Headline-number denominator audit
- α-score is normalized vs uniform baseline; appropriate.

## Mechanism-attribution audit
- The paper carefully distinguishes representational similarity (Procrustes alignment) from causal efficacy (cross-probe intervention) and tests both independently. This is the right methodology for interpretability claims.
- Multiple triangulating experiments per claim (e.g., for "shared representation": Procrustes alignment in Fig 2, cross-probe intervention in Fig 3, residual stream alignment in Fig 4).

## Soundness score rationale

- **Strengths:**
  - Methodology carefully separates representational similarity from causal efficacy.
  - Random baselines provided for Procrustes alignment.
  - Train/test split present for the Iago global rotation experiment.
  - Limitations explicitly acknowledged in Sec 7.
  - Custom metric (α) is well-motivated and accounts for variable move-set sizes.
  - Multiple triangulating experiments per claim.
  - Framing is calibrated ("approaching", not "matches").

- **Weaknesses:**
  - Single-seed; CIs are over probe dimensions, not seeds. Field-norm for this sub-area.
  - "Middle layer identifies game identity" is variant-pair-specific (Layer 5 for NoMidFlip, Layer 2-3 for DelFlank); the abstract's general framing is loose.
  - Procrustes alignment baseline (Procrustes-random ≈ 0.68) shows the technique recovers substantial structure even from random rotations; the +0.30 above random is meaningful but not dramatic.

This is a well-executed mechanistic interpretability paper with a useful controlled framework. No score-2 trigger fires. The construct-coverage is good; the framing is calibrated; the limitations are acknowledged. The single-seed methodology is field-norm (minor flaw with offsetting strengths in methodology rigor).

- **Soundness = 5, confidence = 4.** Solid execution; one minor issue (single-seed methodology + variant-specific routing-layer framing). Full read of 10-page main paper. Verbatim quotes available.
