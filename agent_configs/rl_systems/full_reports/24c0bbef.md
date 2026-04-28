# Statsformer (24c0bbef) — Phase B full report

## Headline empirical claims

- **C1 (theoretical, abstract+intro):** Statsformer "performs no worse than any convex combination of its in-library base learners, up to statistical error" (Theorem 1, Corollary 1).
- **C2 (abstract):** "informative priors yield consistent performance improvements" — supported by Figure 1, Figure 2, Table 2 (gains over the no-prior STATSFORMER ablation).
- **C3 (abstract):** "uninformative or misspecified LLM guidance is automatically downweighted, mitigating the impact of hallucinations across a diverse range of prediction tasks" — supported only by Section 6 adversarial simulation (deterministic feature-score inversion).
- **C4 (Section 5.2):** Statsformer "outperforms both AutoML benchmarks, i.e. AutoGluon and AutoML-Agent" — supported by Figure 1.
- **C5 (intro contributions):** "cost-effective and scalable integration of LLM priors" — supported by Appendix D.1–D.4 cost analysis.

## Construct-validity audit

### C3 — "robustness to hallucinations"
- **Construct claimed:** Statsformer "automatically downweights" "uninformative or misspecified LLM guidance," "mitigating the impact of hallucinations." The framing covers the broad family of LLM hallucination failure modes that real applications encounter.
- **Operational metric (Section 6):** Adversarial priors are constructed via the deterministic transformation `s ← (s+ε)^{-1}`, applied to an *otherwise-informative* score vector. Performance is then compared to no-prior stacking (Figure 3).
- **Aspect not measured:** A fully systematic inversion of an informative signal is the *easiest* possible adversarial regime for any cross-validated downweighting mechanism — the corrupted score is anti-correlated with truth and is trivially detectable in OOF risk space (the corresponding non-zero α configurations underperform the α=0 anchor by a wide margin, so the simplex meta-learner concentrates on the prior-free configurations). Real LLM hallucinations on feature priors do not look like deterministic inversions; they manifest as (i) noise priors with no information content, (ii) partially-correct priors with stochastic or correlated noise, (iii) plausible-but-incorrect importance scores ("domain-confused fabrications"), or (iv) low-confidence-uniform priors that look superficially informative. None of (i)–(iv) are tested. The construct of "hallucination robustness" claimed in the abstract spans a substantially broader failure-mode set than the adversarial simulation exercises.

### C2 — "consistent performance improvements"
- **Construct claimed:** "Informative priors yield consistent performance improvements." The framing word "consistent" is load-bearing because the comparison is against an already-strong stacking baseline (STATSFORMER-NO-PRIOR is itself a Super-Learner-style ensemble of Lasso + XGBoost + RF + kernel SVM).
- **Operational metric (Table 2):** Mean improvement (mean metric difference / mean baseline error) and split-level win-rate over the no-prior baseline, across 8 datasets, with 95% CIs.
- **Aspect not measured / contradicted by the table itself:** Table 2's own confidence intervals contain zero or fall below the 50% line on multiple datasets:
  - NOMAO Error improvement: `0.00 ± 2.34` (CI = [−2.34, +2.34]).
  - Breast Cancer AUC improvement: `2.45 ± 4.18` (CI = [−1.73, +6.63]).
  - Breast Cancer AUC win rate: `0.60 ± 0.11` (CI lower bound = 0.49, below 50%).
  - NOMAO AUC improvement: `3.52 ± 2.64` (CI lower bound just above zero at 0.88).
  The qualifier "consistent" as stated in the abstract is not supported on at least two of eight datasets by the paper's own data.

### C4 — "outperforms both AutoML benchmarks"
- **Construct claimed:** Statsformer "outperforms both AutoML benchmarks, i.e. AutoGluon and AutoML-Agent."
- **Operational metric (Figure 1):** Head-to-head comparison across train ratios.
- **Aspect not measured:** Figure 1's own footnote states "due to computational constraints, we only included the AutoML-Agent baseline in Bank Marketing, ETP, and Lung Cancer." The general claim is therefore demonstrated on only 3 of 8 datasets, with no AutoML-Agent comparison reported on Breast Cancer, Credit, Internet Ads, NOMAO, or Superconductivity. Worse, on Bank Marketing the paper acknowledges "a preprocessing error led to severe overfitting and a sharp AUROC drop at `train_ratio=0.2`" — an explicitly anomalous comparison that the authors keep in the figure rather than flag as invalid or re-run.

## Reward / objective audit (transposed for ML pipeline context)

The "proposed reward" here is the prior-augmented Statsformer training objective. The "baseline reward" is STATSFORMER-NO-PRIOR (only configurations with α=β=0). Term-by-term:

| Component | Statsformer (proposed) | Statsformer-no-prior (baseline) |
|---|---|---|
| Base learners | Lasso, XGBoost, RF, kernel SVM (each at α∈{0,1,2}, β∈{0.75,1}) | Lasso, XGBoost, RF, kernel SVM (only α=β=0) |
| Adapter (penalty/feature-scale/instance-weight) | Active for α>0 or β<1 configurations | Inactive |
| OOF stacking | Yes | Yes |
| Simplex meta-learner | Yes | Yes |
| LLM prior elicitation | Yes (one-shot, o3) | No |

- **Set-relationship.** Baseline ⊂ proposed: the proposed dictionary strictly extends the no-prior one by adding (α, β) ≠ (0,0) configurations. This is the *correct* ablation structure — the prior-free anchor is always available to the meta-learner. ✓
- **Sign-of-dropped-terms.** Nothing is dropped; the proposed method is an additive extension. No protective penalty is removed. ✓
- **Mechanism-attribution.** Because the simplex constraint π ∈ Δ^{L−1} can place all weight on the prior-free columns, the meta-learner *can* in principle ignore the prior entirely. The empirical question is therefore: how much of the headline gain over no-prior in Table 2 comes from the LLM-derived priors specifically, vs. from the additional dictionary diversity (more learner configurations to choose from regardless of whether the priors are informative)?

The Section 6 adversarial sim is the paper's answer: when priors are inverted, performance collapses to the no-prior level, indicating the gain on real-LLM priors is not a free dictionary-size effect. This is a *useful* control, but it leaves the score-2 trigger on C3 intact — the inversion regime is the easiest adversarial regime, not a representative one.

## Counter-hypothesis attempts

### CH1 (on C2): "consistent gains" are driven by stacking dictionary expansion, not LLM priors per se
- **Hypothesis:** Adding (α=1, α=2, β=0.75) configurations to a Super-Learner-style ensemble could improve OOF risk on average even if the LLM priors are uninformative, because the meta-learner has more learner-flavors to combine and downweight.
- **Paper's evidence ruling it in/out:** Section 6 adversarial sim partially refutes this on the deterministic-inversion regime. **Unrefuted on the random-noise regime** (no random-prior control reported). Most reported gains over no-prior are ≤5% (Bank Marketing 1.40%, Credit 1.52%, NOMAO 0.00%, Superconductivity 1.37%), so even modest dictionary-effect contamination would be material.
- **Verdict:** Partially refuted, partially unrefuted. Score-3-tier concern, not score-2.

### CH2 (on C2): the ETP gain is an artifact of small-n high-variance regime
- **Hypothesis:** ETP has 189 instances with imbalanced classes and is restricted to train ratios 0.3–0.7. The 25.9% improvement has 95% CI = [+17.0%, +34.8%] — the lower bound is positive, so it cannot be explained purely by zero-mean noise.
- **Paper's evidence ruling it in/out:** Strict CI bound positive → not explained away by noise. The magnitude could be inflated by the regime, but the sign of the effect is real.
- **Verdict:** Refuted (the gain is real, even if magnitude is regime-amplified). Not a citable concern.

### CH3 (on C4): the AutoML-Agent comparison is selection-effect favorable
- **Hypothesis:** AutoML-Agent is run on only 3/8 datasets; on one of those (Bank Marketing), its preprocessing-error result is retained as a data point even after the authors acknowledge it is anomalous. If the comparison were re-run cleanly across all 8 datasets, AutoML-Agent might match or exceed Statsformer on some.
- **Paper's evidence ruling it in/out:** No re-run after acknowledging the preprocessing error. No coverage on Breast Cancer, Credit, Internet Ads, NOMAO, Superconductivity. The "computational constraints" justification is plausible but is exactly the structure of a silent-baseline-omission failure mode.
- **Verdict:** Unrefuted. Score-2 silent-baseline-omission trigger fires on C4.

### CH4 (on C3): "downweighting hallucinated priors" works only on systematic inversions, not on noise priors
- **Hypothesis:** Random-noise priors (s_j ~ Uniform(0,1) i.i.d.) might fail to be downweighted as cleanly as inverted-informative priors, because all prior-injected configurations would have similar OOF risk to each other (no differential signal for the meta-learner to exploit). Plausible-but-uniform priors might even be assigned positive weight despite being uninformative.
- **Paper's evidence ruling it in/out:** No random-noise control reported. No partially-correct or shuffled-prior control.
- **Verdict:** Unrefuted. Score-2 construct-coverage trigger fires on C3.

### CH5 (on C3): hallucinations in real LLM outputs are correlated, not independent — the OOF-risk-based downweighting may not catch correlated errors
- **Hypothesis:** Real LLM hallucinations on feature relevance are often correlated — e.g., the LLM systematically over-weights features whose names sound clinically important regardless of actual predictive utility. A correlated noise structure could partially survive OOF validation if the correlation pattern aligns with sample-level structure (e.g., features that *look* important across many tasks).
- **Paper's evidence ruling it in/out:** Not tested. The Section 6 simulation is i.i.d. inversion, not correlated.
- **Verdict:** Unrefuted. Reinforces the C3 score-2 finding.

## Multi-objective trade-off audit

The paper claims "consistent improvements" but does not measure prior-injection's marginal effect on:

- **Computational overhead per dataset.** Appendix D.4 references aggregate cost analysis; the gain-vs-cost ratio on small-improvement datasets (NOMAO 0.00%, Bank Marketing 1.40%, Credit 1.52%, Superconductivity 1.37%) is not addressed quantitatively in the main paper. For a 0–1.5% gain at the cost of ~3× more model fits per fold + an LLM API call, the practical case is unclear.
- **LLM API cost / latency.** The paper notes "Statsformer uses an LLM only once to elicit priors" (a strength), but does not report per-dataset token costs, and the prompt-batching strategy (√p batches) means token cost grows with feature dimensionality.

These are not score-2 triggers (cost claims are not the central contribution; the Section D analysis exists at appendix level), but they are score-3-tier omissions on the "cost-effective" branding (C5).

## Framing-vs-demonstration audit

| Framing (verbatim) | Demonstration (verbatim) | Mismatch type |
|---|---|---|
| Abstract: "informative priors yield **consistent** performance improvements" | Table 2: NOMAO Error `0.00 ± 2.34`, Breast Cancer AUC `2.45 ± 4.18` (CIs span zero); Breast Cancer AUC win-rate `0.60 ± 0.11` (lower bound 0.49 < 50%) | "Consistent" softer than the data warrants |
| Abstract: "mitigating the impact of **hallucinations**" | Section 6: only deterministic inversion `s ← (s+ε)^{-1}` of informative priors tested | Construct-coverage gap |
| Section 5.2: "outperforms both AutoML benchmarks" | Figure 1 footnote: "we only included the AutoML-Agent baseline in Bank Marketing, ETP, and Lung Cancer" (3 of 8 datasets) | Silent baseline omission |
| Section 5.2: AutoML-Agent comparison on Bank Marketing | "a preprocessing error led to severe overfitting and a sharp AUROC drop at `train_ratio=0.2`" — retained in figure | Anomalous data point not flagged or excluded |

## All weaknesses found

| Weakness | Severity |
|---|---|
| C3 hallucination-robustness construct-coverage gap (only deterministic inversion tested; no noise / partial / correlated prior controls) | **High** (score-2 trigger) |
| C4 silent baseline omission (AutoML-Agent on 3/8 datasets; one comparison retained despite acknowledged preprocessing error) | **High** (score-2 trigger) |
| C2 framing-vs-demonstration mismatch on "consistent" (CIs span zero on NOMAO Error, Breast Cancer AUC) | **Medium-High** (score-2 trigger on a load-bearing claim) |
| Modest absolute gain magnitudes on most datasets relative to a strong stacking baseline (≤5% on 4 of 8) | Medium (frames the "consistent gains" claim as marginal even where positive) |
| CH1 dictionary-expansion confound not directly tested with a random-noise prior control | Medium |
| Cost-effectiveness branding (C5) not quantitatively defended on per-dataset gain-vs-cost basis | Low-Medium |

(Theorem 1 / Corollary 1 / refit gap analysis: out of Soundness scope. Theory agent's lane.)

## Defense paragraph

If challenged on the score-2 verdict for the hallucination-robustness claim, I cite Section 6 verbatim: the only adversarial simulation reported is `s ← (s+ε)^{-1}`, which inverts an *otherwise-informative* score vector. The abstract's framing ("uninformative or misspecified LLM guidance is automatically downweighted, mitigating the impact of hallucinations across a diverse range of prediction tasks") asserts robustness across the broad family of hallucination modes — which by the paper's own taxonomy in the related-work section ("noisy or inconsistent" priors, citing Yao et al. 2024) is not exhausted by deterministic inversion. The paper offers no random-noise control, no partial-shuffle control, no plausible-but-uninformative control. On the consistency claim (C2), Table 2's own NOMAO Error `0.00 ± 2.34`, Breast Cancer AUC `2.45 ± 4.18`, and Breast Cancer AUC win-rate `0.60 ± 0.11` are verbatim from the paper. On the AutoML-Agent claim (C4), the silent omission on 5/8 datasets and the retained preprocessing-error comparison are verbatim from Figure 1's own footnote and Section 5.2 prose. Each anchor is in the paper's own load-bearing tables/sections.
