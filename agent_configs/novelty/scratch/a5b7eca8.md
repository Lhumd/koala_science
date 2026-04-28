# Phase A Scratch: a5b7eca8 — dXPP (Penalty Approach for QP Differentiation)

## 4f.1 Pre-result prediction
- Expert profile: differentiable optimization researcher who knows OptNet (KKT-based differentiation) and fixed-point IFD approaches
- Predicted result: a solver-agnostic approach to QP differentiation should be possible; penalty-based smoothing is a natural approach
- Predicted directionality: with paper
- Confidence: medium (solver-agnostic backward pass is a natural goal but the specific penalty approach is non-obvious)

## 4a. Atomic claim decomposition
| Claim # | Phenomenon | Method | Setting | Result |
|---|---|---|---|---|
| 1 | KKT differentiation fragility | Penalty-based forward-backward decoupling | Differentiable QP layers | Bypasses KKT; backward pass = smaller primal-dimensional SPD linear system |
| 2 | Solver-agnostic backward | Black-box QP solver in forward; penalty reformulation in backward | Any QP solver (open source) | 10× speedups; robust to degeneracy |
| 3 | Softplus smoothing | Smooth penalty reformulation via softplus | Convex QPs | Well-defined gradients even at degenerate solutions |

## 4b. Closest prior work
- **Neighbor 1:** OptNet (Amos & Kolter 2017) [KKT-based QP differentiation] — "Foundational work; requires solving large indefinite KKT system in backward; numerically fragile at active-set changes. dXPP decouples forward and backward, solving only a primal-dimensional SPD system."
- **Neighbor 2:** Residual-based implicit differentiation / fixed-point IFD — "Alternative to KKT; similar goal of avoiding full KKT inversion. dXPP's penalty approach gives smaller, better-conditioned linear system."
- **Neighbor 3:** Augmented-Lagrangian variants [various] — "Address infeasibility but still require KKT-like systems in backward. dXPP avoids this via penalty formulation."

## 4c. Pseudo-novelty patterns
- **Composition:** Penalty reformulation + implicit differentiation + SPD linear system. The insight that softplus smoothing turns the penalty into a smooth approximate problem that can be implicitly differentiated with a smaller, better-conditioned system is the key contribution.
- Not a rebrand — specific technical construction.

## 4f.2 Actual result and override
- Actual: "significant speedups and maintains high accuracy... circumvents numerical challenges of KKT-based differentiation"
- Match: matches prediction
- Override: **no override**

## 4g. Positioning issues
- OptNet is correctly identified as the closest prior.
- "Solver-agnostic" is the key practical claim — clearly demonstrated.

## 4h. Score rationale
The penalty-based decoupling is a specific and elegant solution: using softplus smoothing to create a penalty reformulation that (a) can be implicitly differentiated and (b) requires only a primal-dimensional SPD system (vs. KKT's larger indefinite system) is a clean theoretical contribution. The solver-agnostic property is practically important. The result is in the expected direction but the specific approach is non-obvious.

## Score & Confidence
- **Score: 6** (penalty decoupling is genuinely novel; SPD vs. KKT system is precise technical contribution; OptNet is the exact prior to compare against)
- **Confidence: 4** (read abstract, related work, conclusion; OptNet precisely identified; technical delta articulable)
