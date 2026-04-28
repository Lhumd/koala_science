# Scratch: edba3ae8 — Alleviating Sparse Rewards by Modeling Step-Wise and Long-Term Goals (TP-GRPO)

## Load-Bearing Claim Inventory

**Claim 1 (abstract/intro):** "TP-GRPO makes two key innovations: (i) it replaces outcome-based rewards with step-level incremental rewards, providing a dense, step-aware learning signal that better isolates each denoising action's 'pure' effect."
- Location: Abstract, lines 26–31
- Support: Eq. 7 (incremental reward r_t = R(x_{t-1}^{ODE(t-1)}) - R(x_t^{ODE(t)})); results Table 1.

**Claim 2 (abstract/intro):** "(ii) it identifies turning points—steps that flip the local reward trend and make subsequent reward evolution consistent with the overall trajectory trend—and assigns these actions an aggregated long-term reward to capture their delayed impact."
- Location: Abstract, lines 31–36
- Support: Definition 4.1, Definition 5.1, Eq. 8 (r_t^agg = R(x_0) - R(x_t^{ODE(t)})); results Table 1 and Figure 4.

**Claim 3 (abstract):** "Turning points are detected solely via sign changes in incremental rewards, making our method efficient and hyperparameter-free."
- Location: Abstract, lines 35–38
- Support: Definitions 4.1, 5.1; no additional weight hyperparameters for detection.

**Claim 4 (intro/conclusion):** "Extensive experiments also demonstrate that TP-GRPO exploits reward signals more effectively and consistently improves generation."
- Location: Abstract lines 38–40; Conclusion line 439
- Support: Table 1, Figure 4 (training curves), Figure 8 (FLUX.1-dev), Section 6.3 ablations.

**Claim 5 (Section 6.2):** "TP-GRPO consistently outperforms Flow-GRPO across all three tasks (columns 2–4), while largely preserving generalization performance (columns 5–9)."
- Location: Section 6.2, lines 298–302
- Support: Table 1

**Claim 6 (Section 6.2):** "Our checkpoint at step ~700 attains a reward comparable to Flow-GRPO at step ~2300, demonstrating faster convergence and higher performance."
- Location: Section 6.2, lines 319–321
- Support: Figure 4(c) PickScore training curves (Human Preference Alignment task)

---

## Construct Inventory

**Construct 1: "Pure" step-level effect of a single denoising action**
- Claimed construct: isolating the incremental contribution of each SDE sampling step, free of aggregate trajectory effects.
- Operational metric: r_t = R(x_{t-1}^{ODE(t-1)}) - R(x_t^{ODE(t)}) — reward difference after one additional ODE step (Eq. 7)
- Unmeasured aspects:
  - The ODE completion from intermediate latents IS itself a stochastic approximation (the ODE uses a deterministic completion starting from a stochastic SDE latent); the intermediate latent x_t is itself a sample from one particular SDE trajectory, not a fixed state. The incremental reward therefore mixes the single-step effect with variance introduced by the particular SDE realization up to step t. This is acknowledged implicitly in Section 3.1 ("ODE sampling preserves the same marginal distribution") but the variance of r_t across different SDE realizations at the same t is never quantified.
  - Whether the incremental signal actually isolates the "pure" effect vs. merely measuring one noisy proxy of it — never ablated with multiple ODE runs from the same intermediate latent.

**Construct 2: "Implicit interaction / long-term impact" of turning points**
- Claimed construct: certain early SDE steps have disproportionately large causal impact on subsequent reward trajectory; aggregated reward r_t^agg captures this delayed effect.
- Operational metric: r_t^agg = R(x_0) - R(x_t^{ODE(t)}) (Eq. 8) — cumulative reward from the turning point to the final image.
- Unmeasured aspects:
  - The turning-point detection criterion (sign flip of s_t per Definition 5.1) identifies steps where *local* reward disagrees with *global* trend, but never demonstrates that these steps are causally responsible for subsequent reward trajectory changes vs. merely correlated with it. A randomized ablation where turning-point labels are assigned to adjacent non-turning-point steps (same frequency, random assignment) is not provided.
  - Whether identified turning points are actually the steps with highest causal influence (measured e.g. via do-calculus or ablation studies) is not tested.

**Construct 3: "Consistently improves generation" across tasks**
- Claimed construct: TP-GRPO improves image generation quality holistically across compositional accuracy, text rendering, and human preference alignment.
- Operational metrics: GenEval score, OCR accuracy, PickScore (task metrics); Aesthetic, DeQA, ImgRwd, PickScore, UniRwd (generalization metrics on DrawBench).
- Unmeasured aspects:
  - Diversity/mode coverage is not measured — a model that always generates one high-scoring image per prompt could score higher on aggregated metrics while having lower diversity. No FID, IS, or LPIPS diversity metrics reported.
  - Human evaluation is not performed — all reward metrics are automated; the "human preference" task uses PickScore (a learned proxy) not actual human raters.

---

## Reward / Objective Inventory

**TP-GRPO reward terms (per step t):**
- For non-turning-point steps: r_t = R(x_{t-1}^{ODE(t-1)}) - R(x_t^{ODE(t)}) [incremental stepwise reward, Eq. 7]
- For turning-point steps: r_t^agg = R(x_0) - R(x_t^{ODE(t)}) [aggregated long-term reward, Eq. 8]
- KL penalty: -β * D_KL(π_θ || π_ref) as in Flow-GRPO [Eq. 4/5]

**Flow-GRPO baseline reward terms (per step t):**
- Uniform assignment of terminal reward R(x_0^i) to all preceding steps (no step discrimination)
- Same KL penalty term

**Comparison:**
- Both methods use the SAME reward function R(·) (e.g., PickScore, GenEval, OCR accuracy)
- TP-GRPO does NOT introduce additional reward terms — it redistributes the same terminal reward signal across steps via incremental differences and aggregation
- The paper therefore avoids the "reward-explained" failure mode from adding new reward terms that trivially improve on measured metrics
- However, TP-GRPO introduces a balancing operation (Appendix D) — equalizing positive and negative r_t^agg counts per batch — which is an additional optimization decision that could interact with the RL dynamics and is not ablated separately

---

## Counter-Hypothesis List

**Counter-hypothesis 1: ODE-completion variance inflates apparent incremental signal**
- The incremental reward r_t requires running ODE completion twice (from t-1 and from t) for each step. Each ODE completion starts from a different SDE trajectory latent. The "increment" r_t conflates the single-step SDE change with variance from different starting points in the ODE. The paper claims ODE completion is a "statistical average" (Section 3.1, line 204), but this is at the population level; individual ODE completions from different latents still have different outcomes.
- Does the paper rule this out? Partially — the argument that ODE removes stochasticity while preserving marginals is stated. But the variance of individual r_t values (not the expectation) is never quantified. The "pure effect" framing requires low within-step variance; this is not demonstrated.

**Counter-hypothesis 2: Turning-point detection is capturing irrelevant noise rather than causal structure**
- The sign-flip criterion (Definition 5.1) flags steps where the local reward direction disagrees with the overall trajectory direction. In a noisy reward landscape, random noise can frequently flip signs. The paper shows in Figure 1 that reward evolves non-monotonically, but does not provide a null distribution of sign-flips under a random/noise baseline. How often would sign flips occur by chance in a trajectory with noise level comparable to the actual reward variance?
- Does the paper rule this out? No — there is no control condition testing whether randomly selected steps (not turning-point steps) given r_t^agg rewards would perform equally well or worse. This is the most important missing ablation for the mechanism-attribution claim.

**Counter-hypothesis 3: Performance gains come from the Balancing Operation (Appendix D), not the turning-point mechanism**
- Appendix D introduces a balancing operation that equalizes positive and negative r_t^agg samples per batch. This is an optimization regularization that could independently stabilize training by preventing reward imbalance. Whether the turning-point identification per se (versus any step-replacement strategy + balancing) explains the gains is not tested.
- Does the paper rule this out? No. The ablations in Section 6.3 compare: (a) window size variations, (b) noise level α variations. A direct comparison of "turning-point assignment" vs. "random step assignment" for r_t^agg (with the same balancing operation) is absent.

**Counter-hypothesis 4: The improvement is due to more ODE evaluations (compute advantage)**
- TP-GRPO requires running extra ODE completions for every step in the window to compute r_t. This is additional compute per training step vs. Flow-GRPO. Section 6.3 compares training time at different window sizes (Figure 6), showing smaller windows reduce cost. But a compute-matched baseline (Flow-GRPO with the same number of additional ODE evaluations used for something simpler) is not provided.
- Does the paper rule this out? Partially — Section 6.3 notes performance comparisons "over 2400 training steps with corresponding training time." But it doesn't compare against a Flow-GRPO baseline that uses the same wall-clock budget as TP-GRPO's smaller window.

---

## Multi-Objective Trade-off Audit

The paper claims "largely preserving generalization performance" (Section 6.2, Table 1 columns 5–9) for both TP-GRPO variants. Examining Table 1:

- For Compositional Image Generation: TP-GRPO (w/o constraint) scores higher on Aesthetic (5.352 vs 5.223), DeQA (3.963 vs 3.861), ImgRwd (0.9267 vs 0.8792), PickScore (22.28 vs 22.20), UniRwd (3.491 vs 3.459) — all generalization metrics improve over Flow-GRPO.
- For Visual Text Rendering: TP-GRPO (w/o constraint) shows Aesthetic 5.092 vs 5.091 (neutral), DeQA 3.251 vs 3.459 (worse), ImgRwd 0.6433 vs 0.6906 (worse), PickScore 21.93 vs 21.91 (neutral), UniRwd 3.160 vs 3.088 (slightly better).
- **Key finding: For Visual Text Rendering, DeQA drops from 3.459 (Flow-GRPO) to 3.251 (TP-GRPO w/o constraint) and ImgRwd drops from 0.6906 to 0.6433 — substantial declines on image quality metrics.** The paper does not discuss this trade-off explicitly. The claim "largely preserving generalization performance" is not precise — there is a measurable quality degradation in specific metrics on one of the three tasks.

---

## Framing-vs-Demonstration Check

**Claim in Abstract (line 36–38):** "Turning points are detected solely via sign changes in incremental rewards, making our method efficient and hyperparameter-free."
- Methodology check: This is technically accurate for the detection mechanism itself.
- However, the balancing operation in Appendix D involves a design choice (equal positive/negative split per batch) that could be considered a hyperparameter. This is not mentioned as a constraint in the abstract claim.
- Additionally, the window size N_SDE-window is a hyperparameter (explored in Figure 6) and the noise level α is a hyperparameter (Figure 7). The "hyperparameter-free" claim refers only to turning-point detection, but the overall TP-GRPO framework still introduces training hyperparameters relative to Flow-GRPO.

**Claim in Section 6.2 about "faster convergence":** "Our checkpoint at step ~700 attains a reward comparable to Flow-GRPO at step ~2300."
- This comparison is on the Human Preference Alignment task with the KL penalty removed (Section 6.3 setup: "we remove the KL penalty term in Eq. 4 during training" — lines 361–362).
- The faster convergence claim in Section 6.2 is actually from the **unconstrained** training curves shown in Figure 4. The main Table 1 results use the KL-penalized version. The convergence comparison may not transfer to the regularized setting used for the headline numbers.
- This is a mild framing issue: the convergence comparison in Figure 4 appears to use the unconstrained variant shown in section 6.3, but this is presented as a general result in section 6.2 ("the training curves" without qualifying that KL is removed).

---

## Headline-Number Denominator Audit

**Table 1 main comparison:**
- Baseline denominator: Flow-GRPO (re-implemented by the authors under "a controlled and consistent configuration on our hardware" — Section 6.1)
- This is appropriate — the paper explicitly notes results are from their own re-implementation, not from the original paper, "ensuring a fair comparison." No denominator switch issue.

**Faster convergence claim:**
- As noted above, the "step ~700 vs step ~2300" comparison is from the unconstrained (KL-removed) setting in Figure 4, which is presented in Section 6.3 but cited in Section 6.2. This is a mild framing concern but not a severe denominator switch.

---

## Mechanism-Attribution Audit (Critical)

**Two coupled innovations introduced simultaneously:**
1. Incremental step-wise reward r_t (replaces terminal reward for all steps)
2. Aggregated long-term reward r_t^agg at turning points (additional mechanism)

**Ablation coverage (Table 1, Figure 4):**
- Table 1 shows: Flow-GRPO, TP-GRPO (w/o constraint), TP-GRPO (w constraint)
- "w/o constraint" = uses Definition 4.1 for turning-point selection
- "w constraint" = uses Definition 5.1 (stricter consistency constraint)

**What is NOT ablated:**
- **Incremental reward alone without turning-point mechanism**: There is no condition in Table 1 or elsewhere that uses only r_t (step-wise incremental) without the r_t^agg turning-point replacement. In other words, we cannot determine whether the turning-point aggregation mechanism adds value beyond just switching from terminal to incremental rewards.
- **Turning-point aggregation using r_t^agg without the incremental step-wise reward for non-turning-point steps**: Similarly, a condition that keeps terminal rewards for normal steps but applies r_t^agg only at turning points is not tested.

**The comparison between TP-GRPO variants only tests which turning-point definition (4.1 vs 5.1) is better** — it does not isolate whether the incremental reward or the aggregation is the key driver of improvement over Flow-GRPO.

This is a coupled-novelty mechanism attribution failure: two components are introduced jointly, and the ablations only vary the turning-point selection criterion (4.1 vs 5.1), not the presence/absence of each component.

**Score-2 trigger assessment:** This is a clear coupled-novelty failure on a load-bearing claim. The paper's central mechanistic claim is that BOTH innovations are needed: dense step-wise rewards AND long-term aggregation at turning points. But the incremental-reward-only ablation (TP-GRPO without the turning-point aggregation mechanism, just using r_t everywhere) is missing. Without this ablation, the attribution of gains to the turning-point mechanism specifically cannot be supported.

---

## Soundness Score Rationale

**Score-2 trigger fires: Coupled-novelty mechanism attribution failure on a load-bearing claim.**

The paper's headline contributions are: (1) incremental step-wise rewards, and (2) turning-point identification with aggregated long-term rewards. These are presented as two distinct, cooperating innovations ("TP-GRPO makes two key innovations," Abstract). However, the ablation table (Table 1) compares:
- Flow-GRPO (terminal reward baseline)
- TP-GRPO w/o constraint (Definition 4.1 turning points)
- TP-GRPO w constraint (Definition 5.1 stricter turning points)

ALL TP-GRPO variants in Table 1 use BOTH the incremental step-wise reward AND the turning-point aggregation simultaneously. There is no condition with only the incremental stepwise reward (r_t for all steps, no r_t^agg). The claim that the turning-point mechanism specifically — the aggregation component — contributes to the improvement over Flow-GRPO is unsupported by the reported ablations.

This is directly analogous to the rubric's "coupled-novelty mechanism attribution failure" trigger: "Paper introduces two coupled novelties simultaneously, ablates only jointly, then attributes gains to one of them."

Additionally, **Counter-hypothesis 3 (the balancing operation in Appendix D driving gains)** is not ruled out — the balancing operation itself is an optimization design choice that could independently improve training stability without the turning-point logic.

**Offsetting strengths:**
- Clear theoretical motivation for both components
- Multiple tasks (3 main + FLUX.1-dev extension in Appendix A)
- Hyperparameter sensitivity analysis (window size, noise level α)
- Qualitative results in Appendix F
- Re-implementation claims explicitly stated to ensure fair comparison

**But per the rubric:** "A score-2 trigger fires regardless of offsetting strength." The ablation gap is on the paper's central empirical claim about which mechanism drives improvement.

**Score: 2 | Confidence: 4**

Confidence 4 rationale: I read the full paper including all appendices (A–F, pseudocode in E, theoretical proofs in C). The gap is concrete and anchored to Table 1's structure and the abstract's two-innovation framing. I did not cross-check against external benchmarks, but the ablation gap is verifiable directly from the paper's own experimental design.
