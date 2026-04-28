# Phase A Scratch: 5c3d6bff — Certificate-Guided Pruning for Stochastic Lipschitz Optimization

## 4f.1 Pre-result prediction
- Expert profile: a researcher familiar with X-armed bandits (Bubeck et al. 2011), StoSOO (Valko et al. 2013), and Bayesian optimization (GP-UCB)
- Predicted headline result: making the pruning mechanism explicit as a computable active set At improves interpretability and stopping-criterion utility but does not improve the sample complexity rate over zooming/StoSOO
- Predicted directionality: with the paper's framing (certificates add value; sample complexity matches state of art)
- Confidence in prediction: high

---

## 4a. Atomic claim decomposition

| Claim # | Phenomenon | Method | Setting | Result |
|---|---|---|---|---|
| 1 | Explicit pruning certificate | Confidence-adjusted Lipschitz UCB envelope + active set At | Stochastic Lipschitz optimization | Anytime valid optimality certificates; x outside At is certifiably suboptimal |
| 2 | Sample complexity | Active set shrinkage rate analysis under margin condition | Known L, noise σ | Õ(ε^{-(2+α)}) — same rate as zooming but with computable Vol(At) |
| 3 | Unknown L (CGP-Adaptive) | Doubling scheme for online L estimation | Unknown Lipschitz constant | O(log T) overhead; first certificate guarantee for unknown-L Lipschitz optimization |
| 4 | High-dim scaling (CGP-TR) | Trust region variant with local certificates | d > 50 | Scales to d=100; outperforms TuRBO by 9-12% with local certificates |
| 5 | Best-of-both-worlds (CGP-Hybrid) | Smoothness ratio ρ = Llocal/Lglobal; switch to GP when ρ < 0.5 | Mixed smooth/non-smooth functions | Wins on all 12 benchmarks; preserves CGP certificates while using GP for smooth regime |

## 4b. Closest-prior-work identification

- **Neighbor 1:** Bubeck et al. (2011) [X-armed bandits / HOO / zooming] — "Most direct predecessor. The zooming algorithm maintains an active set implicitly (as an analysis artifact); CGP makes this set a computable first-class object with measurable volume. The sample complexity Õ(ε^{-(2+α)}) is identical to HOO's near-optimality-dimension rate. The delta is the explicit certificate, not the complexity."
- **Neighbor 2:** Valko et al. (2013) [StoSOO] — "Stochastic tree-based algorithm for the same problem class. StoSOO prunes branches implicitly via UCB checks; CGP unifies this as a global active set with a computable volume shrinkage guarantee. No stopping criterion in StoSOO."
- **Neighbor 3:** Malherbe & Vayatis (2017) [LIPO] — "LIPO handles unknown Lipschitz constant via adaptive estimation but lacks certificate guarantees; CGP-Adaptive adds certificates with only O(log T) overhead, extending the LIPO approach."

## 4c. Pseudo-novelty pattern check

- **Rebrand?** No — making the active set explicit and computable is a real algorithmic addition; the certificate mechanism isn't just renaming zooming.
- **Domain transfer?** No — this is within the same problem class.
- **Composition without insight?** Partially for CGP-Hybrid (Lipschitz pruning + GP refinement), but the smoothness ratio ρ for switching is non-trivial and the certificate remains valid post-switch.
- **Resolution bump?** No — CGP-TR extends to high dimensions where prior Lipschitz methods fail entirely.

## 4d. Novel framing vs. novel science

"Certificate-Guided Pruning" as a first-class object enables principled stopping criteria (stop when Vol(At) < threshold) and anytime progress guarantees. This is scientifically useful: existing methods couldn't tell you *when* to stop. The framing enables new algorithms (TR, Hybrid) that wouldn't be well-defined without the certificate.

## 4e. Concurrent work calibration

None identified.

## 4f.2 Actual result and override

- Actual headline result: "CGP variants match or exceed strong baselines while providing principled stopping criteria via certificate volume" — sample complexity Õ(ε^{-(2+α)}), best performance on all 12 benchmarks for CGP-Hybrid
- Match assessment: matches prediction — certificates without improving the sample complexity rate; empirical performance is strong but expected for a method that combines zooming + GP
- Override clause that fires: **no override**
- Justification: result matches expert's expectation; the added value is certificates/stopping criterion, not a complexity improvement

## 4g. Positioning issues

- **"First such guarantee":** Claim "the first such guarantee for Lipschitz optimization with certificates" for the adaptive L case (§contribution 2, CGP-Adaptive) is specific and plausible. For the base CGP case, the paper is careful to say it differs from zooming by *exposing* the pruning mechanism, not by achieving new complexity.
- **Overclaim relative to evidence:** The abstract says "explicit certificates of optimality" which is accurate given the construction.
- **Missing baseline:** LIPO is compared (indirectly via related work) but no direct numerical comparison against LIPO in the tables.

## 4h. Originality score rationale

The paper's strongest novelty is on the **certificate axis**: making the active set At a computable, first-class algorithmic object with measurable volume shrinkage is genuinely new relative to zooming (Bubeck 2011) and StoSOO (Valko 2013), where pruning is an analysis artifact. The CGP-Adaptive unknown-L guarantee is the most specific novel theoretical claim. The CGP-TR and CGP-Hybrid extensions add practical value. The sample complexity rate is not improved (Õ(ε^{-(2+α)}) is known from zooming), which is honestly acknowledged. This is a solid incremental contribution that fills a real gap.

## Score & Confidence

- **Originality score: 5** (weak accept — real but moderate; certificate mechanism is the novel axis; sample complexity rate is existing; extensions add practical value)
- **Confidence: 4** (read full related work; delta vs. Bubeck 2011/Valko 2013 is clearly articulated; didn't retrieve Bubeck 2011 full text but paper's own description is sufficient)
