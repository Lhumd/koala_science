# Novelty Audit — Soft Forward-Backward Representations (5b4fcb9f)

**The paper extends Forward-Backward (FB) representations (Touati & Ollivier 2021) from additive rewards linear in the occupancy measure to a strictly more expressive class: general differentiable utilities (distribution matching, pure exploration), via an entropy-regularized soft FB algorithm.**

## Decomposition

- **FB algorithms for linear utilities (direct prior):** Touati & Ollivier (2021) show that FB representations can zero-shot retrieve approximately optimal policies for any additive reward linear in the occupancy measure. This covers a large class but excludes tasks where the objective is an arbitrary differentiable function of the occupancy measure (e.g., distribution matching, KL-divergence objectives, exploration bonuses).
- **Soft FB for general utilities (the novel axis):** The paper introduces an entropy-regularized forward-backward algorithm that captures stochastic behaviors in a dynamical system. The entropy regularization is the key addition: it enables handling of objectives that are not linear in the occupancy measure, by working with the "softmax" (entropy-regularized) occupancy distribution rather than the point-mass optimal policy.
- **Strictly more expressive problem class (the contribution):** Distribution matching and pure exploration tasks are practically important and explicitly excluded by standard FB. Soft FB addresses these, which is a genuine theoretical advance over Touati 2021.

## Reframe

"Soft FB extends zero-shot RL from linear-reward tasks to arbitrary differentiable utility tasks via entropy regularization of the occupancy measure." The "soft" (entropy-regularized) version is the specific technical contribution relative to standard FB.

## Concrete fix

A direct comparison on tasks that are within the linear-reward class (where both standard FB and Soft FB apply) would show whether the entropy regularization hurts or maintains performance on the subset of tasks where FB is already applicable. If Soft FB matches FB on linear tasks, the extension comes at no cost.
