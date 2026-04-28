# Scratch: f8cfc8f8 — Elucidating the Design Space of Flow Matching for Cellular Microscopy

## Theorem inventory

- **Proposition 3.1** (p. 3): Under Assumptions 1–3, for every x ∈ X:
  d_P(p*(x), H(G(x))) ≤ ε_base + U · ||e*(x) − G(x)||
  Consequently:
  E_{x~D}[d_P(p*(x), H(G(x)))] ≤ ε_base + U · ε_G

That is the only formal theoretical statement in the paper. Proof is in-line on p. 3, ~3 lines.

## Assumption inventory

- **Assumption 1 (coverage)** (p. 3): There exists a function e*: X → E such that for all x ∈ X, Δ_model(x) := d_P(p*(x), H(e*(x))) ≤ ε_base.
- **Assumption 2 (Lipschitz generator)** (p. 3): There exists U > 0 such that for all e_1, e_2 ∈ E, d_P(H(e_1), H(e_2)) ≤ U·||e_1 − e_2||.
- **Assumption 3 (encoder learning error)** (p. 3): For x ~ D, there exists ε_G ≥ 0 such that E_{x~D}[||e*(x) − G(x)||] ≤ ε_G.

d_P is a pseudometric on the space of phenotype response distributions (footnote 1: e.g., MMD between conditional distributions).

## Load-bearing lemma list

Only the triangle inequality on d_P. No auxiliary lemmas.

## Appendix proofs cross-check

Proof of Proposition 3.1 is in-line in §3 main text:
- d_P(p*(x), H(G(x))) ≤ d_P(p*(x), H(e*(x))) + d_P(H(e*(x)), H(G(x))) [triangle ineq]
- ≤ ε_base [by A1] + U·||e*(x) − G(x)|| [by A2]
- Take expectation, apply A3: ≤ ε_base + U·ε_G ∎

No appendix variant. Verified each step lines up with the cited assumption.

## Theory score rationale

**Verification of correctness.** The bound is mathematically valid. d_P is a pseudometric so triangle inequality applies. A1 directly bounds the first triangle-summand. A2 directly bounds the second. Linearity of expectation + A3 gives the final form. No measure-theoretic gap (E is a finite-dim embedding space, ||·|| is the standard norm). The proved object (d_P(p*(x), H(G(x)))) is exactly the modelling error claimed.

**Novelty.** Triangle-inequality + Lipschitz error decompositions for compositional approximators are entirely standard in approximation theory and statistical learning (cf. Cucker-Smale-style decompositions, sieve estimation error bounds, two-stage estimator analyses in nonparametric statistics). The proposition is correctly framed for this domain but offers no new technique.

**Tightness.** Bound is loose:
- U is left as an abstract positive constant. For natural d_P choices, U can vary widely: MMD with bounded kernel ≤ 2/√n on the kernel; FID has no clean Lipschitz constant in general; KL is unbounded. The paper makes no attempt to estimate U for the MiT-XL/2 architecture or for the FID/KID metrics it actually uses.
- Without an estimate of U, the multiplicative factor on ε_G has no quantitative content — the bound says only that a smaller ε_G gives a smaller upper bound, with an unknown coefficient.

**Inferential leap.** Immediately after the proof: "The implication is that there are two tasks implicit in modelling perturbation effects... we will treat each component separately in §§4 and 5." The proposition supports "the upper bound has two additive sources" but does not support "the optimization problem decouples." Independently minimizing ε_base and ε_G is a relaxation of jointly minimizing the original objective; H affects U, so freezing H and only training G can produce a worse upper bound than co-training (H, G). This is exactly the regime the paper operates in (§5 freezes the base model and only trains an adaptor on Morgan/MolGPS embeddings).

**Score: 5** (weak but defensible). The theorem is correct (above 3), but trivial (3-line triangle inequality), uses standard machinery, leaves the key constant U unestimated, and the inferential step from the bound to the engineering plan is a non-sequitur. Not below 4 because the proof is valid and the decomposition is conceptually useful as a sketch. Not above 6 because there is no real theoretical novelty, no constant analysis, and no discussion of when independent optimization is near-optimal vs. when it loses.

**Confidence: 4.** I read the proposition, assumptions, and proof, and verified each step against its cited assumption. The proof is short enough that I am confident about correctness without cross-reference to external prior theorems. I did not cross-check that no prior published version of "additive error decomposition for compositional generative models with embedding encoder" exists, but the proposition is generic enough that novelty isn't really at stake regardless.
