# Scratch — db0fe68f — HyperMLP: An Integrated Perspective for Sequence Modeling

Domains: `d/Deep-Learning`, `d/Theory`. Theoretical content present; in-scope per step 0.

## Theorem / Lemma / Proposition inventory (verbatim, with location)

**Main text (§2):**
- **Theorem 2.1 (Dynamic-head decomposition; p.5):** Under L2Norm_t(z) = z/ρ_t(z) with ρ_t(z) > 0 a scalar, the head in Eqs. (7)–(10) satisfies (i) o_t = σ(x_t W^(1)_MLP(X_{t:1})) W^(2)_MLP(X_{t:1}) (dynamic two-layer MLP form), (ii) pool→activated readout o_t = (1/ρ_t(h_t)) ∫_Ω α_θ(x_t;u)_+ β_θ(x_t;v) dμ^pool, and (iii) sequence mixing builds context-wide slots u_i = Σ_j R^(1)_{j,i}(x_t) X_{t:1}[j,:], v_i = Σ_j R^(2)_{j,i}(x_t) X_{t:1}[j,:].
- **Corollary 2.2 (Warped routing strictly generalizes polyhedral routing; p.5):** If R^(1), L^(1) constant in x_t, the gating boundaries {x_t : h_{t,i} = 0} are hyperplanes; if R^(1)(x_t) (or L^(1)(x_t)) depends smoothly and nontrivially on x_t, the boundaries are generically curved level sets.
- **Theorem 2.3 (Lag layout: extension consistency implies AR truncation invariance; p.5):** Fix 1 ≤ t < T. Under R^(m)_T(x) = P_{t→T} R^(m)_t(x) P_{t→T}^⊤ (Eq. 20) and ρ_T([z,0]) = ρ_t(z), o_T(x; X̃_{T:1}) = o_t(x; X_{t:1}).
- **Proposition 2.4 (HyperGLU decouples routing/magnitude; p.5):** With h^scale, h^gate ∈ R^{1×t} produced by the same instantiation form as h_t (with split cores), the activated set depends only on sign(h^gate) (routing), while Softplus(h^scale) > 0 modulates magnitudes independently.
- **Theorem 2.5 (Budget asymmetry in residual two-layer blocks; p.5):** f(x) = x + σ(xW_1)W_2 with x ∈ R^{1×d}. (i) If rank(W_2) ≤ r, then f(x) − x lies in a fixed subspace of dim ≤ r ∀x. (ii) If rank(W_1) ≤ r, then ∃ L ∈ R^{d×r} and ψ such that f(x) = x + ψ(xL).
- **Proposition 2.6 (Dynamic-MLP view explains empirical principles; p.6):** (i) prefer QK compression over VO compression; (ii) LoRA on V/O most parameter-efficient; (iii) linear attention collapses routing/selection; (iv) registers enlarge the hidden pool.

**Appendix C (Theoretical supports):**
- **Lemma C.1 (ReLU is diagonal gating):** ReLU(z) = z D(z) for D(z) := diag(1{z_i > 0}). Trivial, one-line proof.
- **Theorem C.2 (Fixed 2-layer ReLU MLP selects sub-network):** f(x) = (xW_1 + b_1) D_x W_2 + b_1 D_x W_2 + b_2; on regions where D_x is constant, f reduces to an affine map.
- **Proposition C.3 (Dynamic two-layer form):** Direct substitution.
- **Theorem C.5 (Three-stage memory and multi-stage pruning):** Under Assumption B.1, output equals Σ_{i=1}^t α_θ(x_t;u_i)_+ β_θ(x_t;v_i) / ρ_t(h_t); pool measure μ^pool ⊃ μ^act via hard gate.
- **Lemma C.6 (DPLR temporal-mixing parameterization admits prefix-extension consistency):** With given length-t DPLR parameters, the length-T extension R_T(x) = P_{t→T} R_t(x) P_{t→T}^⊤.
- **Corollary C.7 (Extension consistency, monotone expressivity, non-instantiated pool slots):** Under (33), realizable function family is monotone in T.
- **Proposition C.8 (Ever-growing hidden width):** μ^pool has at most t atoms.
- **Proposition C.9 (Implicit infinite reachable atom set across contexts):** A_θ ⊆ Ω is infinite when token/state space contains a continuum.
- **Theorem C.10 (Polyhedral spline under static mixing):** Under static R^(1), L^(1), R^(2), L^(2), x → o(x;X) is CPWL with hyperplane boundaries H_j = {x : x b_j = 0}, b_j the j-th column of B(X) = L^(1) X^⊤ R^(1).
- **Corollary C.12 (Diagonal vs. mixing R^(1) effects, static):** Diagonal R^(1) preserves hyperplane geometry; off-diagonal mixing replaces normals by linear combinations.
- **Theorem C.13 (Pullback orthant partition and piecewise-smoothness):** If h_j(·;X) is C^1 with non-zero gradient at boundary points, partition boundaries are C^1 hypersurfaces.
- **Proposition C.14 (Local linearization and deformation terms):** dh = (dx)L^(1)(x)X^⊤R^(1)(x) + x(dL^(1)(x))X^⊤R^(1)(x) + xL^(1)(x)X^⊤(dR^(1)(x)).

**Appendix D (Functional-analytic / NTK):**
- **Lemma D.2 (Reachable atoms lie in a compact set):** Under bounded-norm Assumption D.1.
- **Lemma D.3 (Measurability and boundedness of feature map).**
- **Theorem D.4 (Bounded linear readout over reachable measures):** ‖T_{θ,t} μ‖_{∞,2} ≤ ‖Ψ_θ‖_{∞,2} ‖μ‖_TV.
- **Theorem D.6 (Restriction/activation is a TV contraction):** ‖μ^act‖_TV ≤ ‖μ^pool‖_TV.
- **Theorem D.7 (Variation norm yields a Banach function space).**
- **Lemma D.11 (Current-step Activated Memory stability under margin).**

**Appendix F (Parameterization of HyperMLP):**
- **Theorem F.1 (Lag layout aligns canonical extension with AR truncation):** The proof for Theorem 2.3, expanded.
- **Theorem F.3 (Output-subspace invariance under low-rank W_2):** rank(W_2) ≤ r ⇒ f(x) − x ∈ U with dim(U) ≤ r.
- **Theorem F.5 (Quotient structure under low-rank W_1):** rank(W_1) ≤ r ⇒ ∃ψ: f(x) = x + ψ(xL); δ ∈ Null(W_1^⊤) ⇒ f(x+δ) = f(x) + δ.

**Appendix H (Implications):**
- **Proposition H.1 (Prompt inclusion is additive pool instantiation, no mixing).**
- **Proposition H.3 (Slots are global linear combinations).**
- **Corollary H.4 (Monotone realizable family in context length, lag layout).**
- **Proposition H.5 (Registers enlarge the instantiated pool, no mixing).**
- **Proposition H.7 (Static sequence mixing mixes hyperplane normals).**
- **Proposition H.8 (Dynamic sequence mixing yields warped boundaries).**
- **Proposition H.10 (Ungated normalization yields full-pool signed readout):** Replacing ReLU(L2Norm(·)) by L2Norm(·) collapses pool→activated restriction.

**Appendix I (Function classes and task-level implications):**
- **Proposition I.1 (Strict expressivity gap, summary):** Token-wise ReLU attention induces polyhedral gating (Eq. 88); HyperMLP contains this class and additionally realizes warped piecewise-smooth spline maps with curved hypersurface boundaries.
- **Proposition I.2 (Paying for temporal mixing by shrinking QK yields strict budgeted expressivity gain):** Under the budget constraint 2d(d_qk − d̃_qk) ≥ P_temp(t,r_s) := 4tr_s + 2t + 2dr_s (Eq. 96), there exists a HyperMLP head fitting in the matched per-head budget that realizes a curved-boundary function (Example 1: sigmoid-warped halfspace with d=t=2, d̃_qk=2, r_s=1) not realizable by any token-wise ReLU-attention head with static feature projections.

## Assumption inventory (verbatim, location)

- **Assumption B.1 (Positive scalar L2 normalization across t; p.14):** For each t ≥ 1, ∃ ρ_t : R^{1×t} → (0, ∞) such that L2Norm_t(z) = z/ρ_t(z). Concrete: ρ_t(z) = √(‖z‖_2^2 + ε), ε > 0.
- **Assumption C.4 (Scalar positive L2 normalization across t):** Same as B.1, restated.
- **Assumption D.1 (Bounded contexts and uniformly bounded mixings; p.22):** Bounded input domain X ⊂ R^{1×d}; bounded set of context matrices; ‖R^(j)_θ(x)‖_op ≤ C_Rj, ‖L^(j)_θ(x)‖_op ≤ C_Lj on X.
- **Eq. 33 (extension consistency, used in Lemma C.6 and Cor C.7):** R^(m)_T(x) = P_{t→T} R^(m)_t(x) P_{t→T}^⊤.
- **Eq. 34 (padding invariance):** ρ_T([z, 0]) = ρ_t(z).
- **(96) Budget constraint:** 2d(d_qk − d̃_qk) ≥ P_temp(t, r_s) = 4t r_s + 2t + 2d r_s.

## Load-bearing lemma list

The most important *load-bearing* theoretical claim is the strict-expressivity gap **Prop I.1 / I.2**, which is the paper's headline novelty contribution. Its proof relies on:
- **Theorem C.10** (token-wise ReLU attention has polyhedral CPWL geometry — used as the lower-class baseline)
- **Theorem C.13** (HyperMLP can produce C^1 curved boundaries via non-trivial dR^(1))
- **Example 1 in I.2** (concrete sigmoid-warped halfspace witness)
- **Theorem F.3 / F.5** (output-subspace and quotient-structure invariances — used to argue why shrinking QK rather than VO is the right way to "pay" for temporal mixing while preserving the budget)

The other "explanatory" results in §2 / Appendix H all hinge on **Theorem C.5** (the pool/activated decomposition), which itself depends on **Lemma B.2** (gate invariance under scalar L2 normalization, trivial under Assumption B.1).

The lag-layout AR-truncation invariance (**Thm 2.3 / F.1**) hinges on **Lemma C.6** (DPLR extension consistency) AND **Eq. 34** padding invariance of ρ.

## Appendix proofs cross-check

Spot-checked the load-bearing proofs:

- **Theorem C.5** (pool/activated decomposition): proof under Assumption B.1: σ_t(h_t) = (1/ρ_t(h_t))[ReLU(h_t)] = (1/ρ_t)[h_t ⊙ 1{h_t > 0}]; absorbing the indicator into the restricted measure μ^act = g_x μ^pool; correct, one-line algebra.
- **Lemma C.6** (DPLR extension consistency): direct substitution of P_{t→T} into D_T = P_{t→T} D_t P_{t→T}^⊤ and A_T S(x) B_T^⊤ = P_{t→T} (A_t S(x) B_t^⊤) P_{t→T}^⊤. Correct.
- **Theorem F.1** (lag-layout AR-truncation invariance): chains (50), Eq. 34 padding, and the L2Norm sign-invariance Lemma B.2. Correct under the stated assumptions.
- **Theorem F.3** (low-rank W_2 → fixed-subspace update): one-line linear-algebra: Δ(x) = σ(xW_1) W_2, so for any u ∈ R^{1×h}, u W_2 ∈ Row(W_2); thus Δ(x) ∈ U := Row(W_2). Correct.
- **Theorem F.5** (low-rank W_1 → quotient structure): factor W_1 = LR; substitute σ((xL)R W_2) — direct. Correct.
- **Proposition I.1 strict containment**: Example 1 in I.2 constructs f(x) = (1/ρ_t(h)) ReLU(x_2 + φ(c x_1) x_1) e_2^⊤. The set {x : x_2 + φ(c x_1) x_1 = 0} is a smooth curve (in particular for φ = sigmoid, c > 0, it is the graph x_2 = −sigmoid(c x_1) x_1). This curve is **not** contained in any finite union of affine hyperplanes; its tangent direction varies with x_1. Therefore f cannot equal any token-wise ReLU-attention output of the form (91), whose nondifferentiability set is contained in a finite hyperplane arrangement (Theorem C.10). Correct.
- **Budget feasibility check for Example 1 at matched budget** (Prop I.2 statement): with d=2, t=2, d̃_qk=2, r_s=1: P_temp = 4·2·1 + 2·2 + 2·2·1 = 16; budget condition 2d(d_qk − d̃_qk) = 4(d_qk − 2) ≥ 16 ⇒ d_qk ≥ 6. So the matched-budget claim requires the *baseline* d_qk ≥ 6 with d=2, which is allowed. The example's HyperMLP head (with d̃_qk = 2, r_s = 1) fits in the same per-head total, and the strict-separation against the *baseline class* (with any fixed-projection static-attention head, including d_qk = 6) holds. Correct.

## Theory score rationale (theoretical grounds only)

The paper is well-organized and the theorems are technically correct. However, the bulk of the formal content is **algebraic restatement rather than substantively new theory**:

1. **Lemma C.1, Theorem C.2** — completely standard ReLU-as-diagonal-gating and CPWL decomposition of two-layer ReLU networks. These are textbook material.
2. **Theorem 2.1 / Proposition C.3 / Theorem C.5** — direct algebraic substitution that re-expresses attention in dynamic-MLP / pool-readout form. Definitional.
3. **Theorem C.10, C.13, C.14** — standard polyhedral-spline / pullback-partition analysis of two-layer ReLU networks with input-dependent feature mixings. Direct application of the implicit function theorem and standard CPWL theory; the framing (warped vs polyhedral) is useful but the math is standard.
4. **Lemma C.6 / Theorem F.1** — bookkeeping identities about block-diagonal extension under explicit P_{t→T} embeddings. Correct, but the result is largely an artifact-of-definition: the authors construct extension-consistent operators specifically so that this identity holds, and then state that as a theorem.
5. **Theorem F.3 / F.5** — one-line linear-algebra facts about residual two-layer blocks under low-rank W_1 or W_2. Standard.
6. **Theorem D.4–D.7, Lemma D.11** — straightforward Banach-space / variation-norm bookkeeping, applying standard TV-contraction and bounded-linear-functional arguments.

The genuine theoretical novelty is concentrated in **Propositions I.1 / I.2 (strict expressivity gap)**. This is correct and non-trivial: under matched per-head budget, single-head HyperMLP's function class strictly contains single-head token-wise ReLU attention's function class, witnessed by a curved-boundary function in R^2. The proof is sound (verified via Example 1 + Theorem C.10).

**However, the strict-expressivity claim's scope is meaningfully narrower than the prose suggests.** The comparison is *single-head* with *fixed input-independent projections* (Eq. 91). Practical attention is multi-head, multi-layer, with universal-approximation guarantees for the composed class. The paper does not establish, and does not claim, that the strict gap survives composition — yet the abstract and §4 frame this gap as the explanation for empirical gains over softmax/ReLU-attention transformers. So the prose oversells what the formal result delivers.

A secondary concern: the lag-layout AR-truncation invariance (Thm 2.3 / F.1) requires padding-invariance ρ_T([z,0]) = ρ_t(z), which holds for the paper's specific affine-free L2Norm but **fails for standard RMSNorm** (which divides by √(‖z‖_2^2 / t), depending on T). Since the paper positions L2Norm as RMSNorm-like (line 65), the theorem is tied to a specific normalization choice — this caveat is not flagged in the main text.

**Calibration:** This is a "weak but defensible" theory paper in the 4–6 band. Theorems are correct, framing is useful, but most of the formal content is reformulation and the novel strict-separation result is restricted to a narrower comparison class than the prose claims to explain. Score: **4** (weak but defensible; novelty marginal; scope of theorem narrower than prose suggests).

**Confidence:** I read the paper end-to-end including all of Appendices A–F and key parts of G–N. I anchored my critique to specific theorem/equation numbers (Prop I.1, I.2, Thm C.10, F.1, F.3, F.5, Eq. 34, 96, 91), spot-checked the load-bearing proofs against the appendix, and verified the strict-separation example's geometry. I did not cross-check against external prior work for *every* prior fast-weight or warped-boundary result, so confidence is **4**, not 5.

## Empirical context (out of Theory scope, NOT used in score)

(Empirical context recorded for owner picture only — explicitly NOT used in Theory score per the "Stay in the Theory lane" rule.)
