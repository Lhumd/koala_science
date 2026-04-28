# Phase A Scratch: a3c6aa1c — 2-Step Agent

## 4f.1 Pre-result prediction
- Expert profile: computational social science / ML decision theory researcher familiar with human-AI decision support (HAI-DS)
- Predicted headline result: a formal Bayesian framework for agent-ML-DS interaction should reveal that agent priors about the ML model affect the impact of decision support; outcome depends on alignment between priors and actual model behavior
- Predicted directionality: with paper (priors matter for ML-DS effectiveness)
- Confidence in prediction: medium

---

## 4a. Atomic claim decomposition

| Claim # | Phenomenon | Method | Setting | Result |
|---|---|---|---|---|
| 1 | Agent priors affect ML-DS impact | 2-step Bayesian framework: prior update + action | ML-DS, medical domain | Different prior assumptions → opposite actions from same ML-DS output |
| 2 | Formalizing ML-DS interaction | Computational framework: Bayesian agent with ML-DS input | General ML-DS settings | Rigorous formalism for prior + ML output → action |
| 3 | Simulations | Framework instantiated on medical decision support | Healthcare context | Demonstrates qualitative and quantitative effects of different priors |

## 4b. Closest-prior-work identification

- **Neighbor 1:** van Geloven et al. (2025) — "Cited as 'this point has been argued in prior literature but not studied formally'; direct predecessor for the argument that priors matter."
- **Neighbor 2:** Predictive optimization literature (Wang et al. 2024) — "The problem setup (predictions → actions) is from predict+optimize; the 2-Step Agent adds the Bayesian prior layer."
- **Neighbor 3:** Human-AI decision support literature broadly — "Many empirical papers on how humans use AI recommendations; this paper provides a formal framework."

## 4c. Pseudo-novelty pattern check

- **Rebrand?** Partially — "2-step agent" = "Bayesian decision maker who updates on ML output"; the two-step formalization is a specific contribution but the concept is known.
- **Domain transfer?** No.
- **Composition without insight?** Partially — Bayesian agent + ML-DS = known components. The insight is that the prior layer explains contradictory behaviors from same ML recommendation.
- **Resolution bump?** No.

## 4d. Novel framing vs. novel science

The formal framework enables precise analysis of why the same ML recommendation leads to different actions in different agents — a useful analytical tool for RCT design in ML-DS settings.

## 4e. Concurrent work calibration

None identified.

## 4f.2 Actual result and override

- Actual result: framework shows priors matter; simulations demonstrate qualitative effects
- Match: matches prediction
- Override: **no override**

## 4g. Positioning issues

- **"General computational framework":** The claim of generality is plausible given the Bayesian formalism, but the empirical validation is limited to medical domain simulations.
- **Causal models excluded:** "ML-DS with causal model is left for future work" — this limits the scope of "general" claim.

## 4h. Originality score rationale

The 2-Step Agent framework provides a rigorous formalism for a known conceptual argument (priors affect ML-DS impact). The novelty is in formalization and the demonstration that contradictory responses to the same recommendation are explained by prior differences. The contribution is theoretical/methodological, with moderate empirical validation. The space (human-AI interaction, decision support) is broad but the formal Bayesian approach is uncommon.

## Score & Confidence

- **Originality score: 5** (framework contribution; novel formalism for known concept; limited empirical validation)
- **Confidence: 3** (read intro; van Geloven cited as closest prior; formal framework described)
