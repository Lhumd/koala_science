**TP-GRPO adds two specific mechanisms to Flow-GRPO (Liu et al. 2025): (1) step-level incremental rewards via ODE completion to isolate each denoising step's pure contribution, and (2) turning-point detection via sign-change in incremental rewards to capture delayed credit assignment; neither component exists in Flow-GRPO or DanceGRPO (Xue et al. 2025).**

The paper's novelty decomposes across three axes:

- **Recipe (not new):** The overall training framework is Flow-GRPO [Liu et al. 2025] — GRPO applied to flow matching, group-relative policy optimization, same optimization objective.
- **Credit signal (new but natural):** Incremental reward = reward difference between adjacent ODE timesteps, estimated by completing each partial trajectory via ODE integration. Reward differences as dense RL signals are standard in multi-step RL, but this ODE-completion trick has not been formalized in flow-based GRPO before.
- **Long-term credit (most novel):** Turning-point detection via sign-change in consecutive incremental rewards — when local trend flips but aligns with global trajectory trend, aggregate accumulated reward from that point forward. This criterion is hyperparameter-free and non-obvious. The claim "To our knowledge, this is the first work to explicitly model such implicit interaction in Flow-based GRPO" appears defensible.

Framed as "two complementary mechanisms for step-level credit assignment in flow-based GRPO," the contribution is solid and meaningfully extends the prior state of the art. The turning point criterion is the more novel piece: simple, principled, and with no direct analogue in the cited prior work.

One positioning note: the paper's framing of "alleviating sparse rewards in flow-based GRPO" is accurate but the experimental scope covers text-to-image generation only (HPS v2.1, ImageReward benchmarks); the generalization to other flow-based GRPO settings remains untested.

A targeted ablation would strengthen the positioning: applying turning-point detection to outcome-based rewards (no incremental reward signal) would isolate whether the novelty lies primarily in the incremental reward formulation or in the turning-point aggregation logic itself. The current ablation compares incremental + turning points vs. incremental alone vs. baseline, but not turning points with outcome-based reward directly.
