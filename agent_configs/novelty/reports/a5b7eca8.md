# Novelty Audit — dXPP (a5b7eca8)

**The novel axis is decoupling QP solving from differentiation via a softplus-smoothed penalty reformulation: the backward pass reduces to solving a primal-dimensional SPD linear system — smaller and better-conditioned than OptNet's (Amos & Kolter 2017) KKT system — while remaining solver-agnostic in the forward pass.**

## Decomposition

- **OptNet KKT differentiation (the direct prior):** OptNet differentiates through the KKT conditions, requiring solving a large indefinite linear system in the backward pass. This becomes numerically fragile at active-set changes and under degeneracy. dXPP explicitly targets this failure mode.
- **Penalty-based decoupling (the novel axis):** The key insight: solve the QP with any black-box solver in the forward pass, then map the solution to a smooth penalty problem (via softplus smoothing) and implicitly differentiate through it in the backward pass. The resulting linear system is primal-dimensional, symmetric positive definite, and remains well-defined under degeneracy. This is a specific technical contribution not present in OptNet or fixed-point IFD approaches.
- **Solver-agnostic property (practical value):** Since the backward pass doesn't need access to the QP solver's internal state, any off-the-shelf solver (open source or commercial) can be used in the forward pass. This is a significant practical advantage over approaches that require solver-specific backward implementations.

## Reframe

"Penalty-based decoupling for differentiable QP: solver-agnostic forward pass with a softplus-smoothed primal-dimensional SPD backward pass that avoids KKT fragility." The paper is correctly positioned — "we bypass KKT by solving a much smaller, better-conditioned linear system in the primal variables."

## Concrete fix

A numerical comparison against augmented-Lagrangian IFD (as in [4] cited in related work) would clarify whether the SPD property or the solver-agnostic design is the primary practical advantage. Both are claimed but only the first is specifically novel over the cited augmented-Lagrangian approaches.
