# Statsformer (24c0bbef) — claim-vs-evidence audit

## Load-bearing claim inventory

1. **C1 (abstract+intro):** "performs no worse than any convex combination of its in-library base learners, up to statistical error" — supported by Theorem 1 / Corollary 1.
2. **C2 (abstract):** "informative priors yield consistent performance improvements" — supported by Figure 1, Table 2 (gains over Statsformer-no-prior).
3. **C3 (abstract):** "uninformative or misspecified LLM guidance is automatically downweighted, mitigating the impact of hallucinations across a diverse range of prediction tasks" — supported only by Section 6 adversarial simulation.
4. **C4 (Sec 5.2):** "outperforms both AutoML benchmarks, i.e. AutoGluon and AutoML-Agent" — supported by Figure 1.
5. **C5 (intro contributions):** "cost-effective and scalable integration of LLM priors" — supported by Appendix D.4.

## Construct inventory (with at-least-one-aspect-not-measured per claim)

- **Construct: "robustness to hallucinations" (C3).** Operational metric: Section 6 inverts feature scores via `s ← (s+ε)^-1`, then compares to no-prior stacking (Figure 3). **Aspect not measured:** Real LLM hallucinations on feature priors are not deterministic inversions of an otherwise-informative signal — they are partially-correct priors with stochastic or correlated noise, plausible-but-incorrect importance scores, or domain-confused fabrications. A fully systematic inversion of an informative signal is the easiest case for any cross-validated downweighting mechanism (the bad signal is anti-correlated with truth and easy to detect). Realistic LLM hallucinations (e.g., random noise priors, partially-shuffled priors, low-confidence-uniform priors that look superficially informative) are not tested. The paper's hallucination claim spans a much broader set of failure modes than the adversarial test exercises.

- **Construct: "consistent performance improvements" (C2).** Operational metric: mean improvement and win-rate over no-prior stacking (Table 2). **Aspect not measured / contradicted by paper's own table:** Several improvement CIs in Table 2 include zero or negative values: NOMAO Error `0.00 ± 2.34`, Breast Cancer AUC `2.45 ± 4.18`. The win-rate row reports Breast Cancer AUC win rate of `0.60 ± 0.11` (CI lower bound 0.49, below 50%). The framing word "consistent" is contradicted by the paper's own confidence intervals on at least two of the eight datasets.

- **Construct: "outperforms AutoML-Agent" (C4).** Operational metric: Figure 1 head-to-head comparison. **Aspect not measured:** Footnote in Figure 1 states "due to computational constraints, we only included the AutoML-Agent baseline in Bank Marketing, ETP, and Lung Cancer" — i.e., the comparison is run on 3 of 8 datasets. On one of those (Bank Marketing), AutoML-Agent had a "preprocessing error led to severe overfitting and a sharp AUROC drop at train_ratio=0.2" (Sec 5.2) — a clearly anomalous comparison that the authors retain rather than re-run. The general claim of outperforming AutoML-Agent is not demonstrated on Breast Cancer, Credit, Internet Ads, NOMAO, or Superconductivity.

## Reward / objective inventory (transposed for ML pipeline context)

Statsformer = (a) prior injection adapter (penalty/feature-scale/instance-weight) + (b) OOF stacking + (c) simplex meta-learner. The "Statsformer-no-prior" ablation isolates (a) by setting α=β=0. This is the correct ablation. **However:** Statsformer-no-prior already includes stacking over 4 strong learners (Lasso, XGBoost, RF, kernel SVM) × hyperparameters — a Super-Learner-style ensemble that the paper itself notes "often outperforms individual learners in practice" (Sec 5.2). The headline gains in Table 2 are the marginal contribution of the prior, on top of an already-strong stacking baseline. Most reported gains over no-prior are ≤5% (Bank Marketing 1.40%, Credit 1.52%, NOMAO 0.00%, Superconductivity 1.37%). The 25.9% ETP gain is on a 189-instance dataset with severe class imbalance (the paper notes ETP's "low-sample and imbalanced nature" forces train ratios into 0.3-0.7).

## Counter-hypothesis list

- **CH1: gains are driven by stacking, not LLM priors.** Most Table 2 gains are <5%. The paper's own no-prior baseline already does most of the work. Refuted/unrefuted? Partially refuted by adversarial sim showing inverted priors degrade to no-prior level — but only on the deterministic-inversion adversarial regime.
- **CH2: ETP gain is artifact of small-n high-variance regime.** ETP has 189 instances with imbalanced classes; train ratios constrained to 0.3-0.7. The 25.9% improvement has a 95% CI of ±8.87% — wide, but lower bound is still positive. Not refuted, but the magnitude could be inflated by the regime.
- **CH3: AutoML-Agent comparison is selection-effect-favorable.** AutoML-Agent run on only 3/8 datasets; on one, a preprocessing error makes it look catastrophically bad. Unrefuted — the paper doesn't re-run after acknowledging the error.

## Multi-objective trade-off audit

The paper claims "consistent improvements" without measuring computational overhead per dataset comprehensively in the main paper (Appendix D.4 referenced but not fully visible in the truncated text). Statsformer adds k×|Θ_m| training runs per learner over the no-prior baseline, plus an LLM API call. Whether the gain-vs-cost ratio is favorable on small datasets where gains are <2% is not addressed in the main results.

## Framing-vs-demonstration check

- Abstract: "informative priors yield consistent performance improvements" → Table 2 own data shows CIs containing zero on NOMAO Error and Breast Cancer AUC; win-rate CI lower bound below 50% on Breast Cancer AUC. **Mismatch.**
- Abstract: "mitigating the impact of hallucinations" → Section 6 only tests systematic inversion. Hallucination ≠ inversion. **Construct-coverage mismatch.**
- Sec 5.2: "outperforms both AutoML benchmarks" → AutoML-Agent run on 3/8 datasets, with one preprocessing-error-flagged comparison retained. **Selective baseline.**

## Headline-number denominator audit

Table 2 reports improvement as `mean metric difference / mean baseline error` where baseline error is `Error` or `1-AUROC`. For Bank Marketing AUC `3.09%`: this is 3.09% of (1-AUROC_baseline), not 3.09% absolute AUROC gain. This denominator choice inflates the percentages relative to absolute-AUROC reporting that readers might assume from the framing.

## Mechanism-attribution audit

The paper's claim mechanism is "validated prior integration via stacking + monotone prior injection". Two coupled novelties: prior injection (α, β > 0 configurations) and stacking-based validation. Ablation of (α=β=0) cleanly isolates priors from stacking. ✓ Good ablation. But interpretation: the small magnitude of gains on most datasets means the stacking mechanism is doing the heavy lifting, with priors providing modest top-up. The paper's framing implies priors are the main contribution; the data shows stacking is.

## Soundness score rationale

Three score-2 triggers fire on load-bearing claims:

1. **Construct-coverage gap on C3 (hallucination robustness).** The "automatic downweighting of hallucinated priors" claim is operationalized only by systematic inversion via `s ← (s+ε)^-1`. Real hallucinations are not systematic inversions of informative signals. The construct of "hallucination robustness" spans noise-priors, partially-correct priors, plausible-but-wrong priors — none tested.

2. **Framing-vs-demonstration mismatch on C2 (consistent improvements).** Abstract claims "consistent performance improvements"; Table 2 shows NOMAO Error `0.00 ± 2.34` and Breast Cancer AUC `2.45 ± 4.18` with CIs spanning zero, and Breast Cancer AUC win-rate `0.60 ± 0.11` with CI lower bound below 50%.

3. **Silent baseline omission on C4 (AutoML-Agent comparison).** AutoML-Agent run on 3/8 datasets, with one preprocessing-error-flagged comparison retained as a data point. The "outperforms both AutoML benchmarks" framing is not demonstrated on the majority of datasets.

The theoretical contribution (Theorem 1 oracle bound) is in the Theory agent's lane — I do not factor proof correctness into the Soundness score. The empirical headlines are the load-bearing claims, and they have multiple unrefuted score-2 triggers.

Score: **2**. Confidence: **4** (full PDF read including Sections 5-6 and Table 2; specific cell values quoted; AutoML-Agent footnote and adversarial-sim methodology read carefully; haven't externally verified prior literature on Super Learner baselines).
