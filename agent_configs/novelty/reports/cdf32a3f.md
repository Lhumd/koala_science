# Novelty Audit — GFlowPO (cdf32a3f)

**The novel axis is applying GFlowNets' off-policy proportional-to-reward sampling to prompt optimization, where StablePrompt (Kwon et al. 2024) uses on-policy PPO; this enables more sample-efficient exploration of the discrete prompt space under sparse rewards.**

## Decomposition

- **RL-based prompt optimization (prior art):** StablePrompt (Kwon et al. 2024) already applies RL to train a prompt-LM via on-policy PPO, with meta-prompt from a fixed distribution. GFlowPO addresses StablePrompt's limitations: on-policy updates are sample-inefficient, and a fixed-distribution meta-prompt doesn't adapt to discovered high-reward prompts.
- **GFlowNet off-policy sampling (the novel axis):** GFlowNets are provably better at diverse proportional-to-reward sampling vs. PPO's maximization focus. In the prompt space (combinatorially large, sparse rewards), this property is particularly valuable. The VarGrad objective with a replay buffer enables off-policy training. This is a motivated application of a known method's unique strengths.
- **Dynamic Memory Update (incremental):** DMU injects high-reward past prompts into the meta-prompt dynamically. This is a useful engineering component but not conceptually novel beyond "replay interesting examples."

## Reframe

GFlowPO is most accurately framed as "off-policy posterior inference for prompt search, using GFlowNets to sample proportionally to reward instead of maximizing it." The distinction from StablePrompt on the off-policy axis (and its sample efficiency consequences) is the strongest differentiator.

## Concrete fix

A head-to-head comparison with StablePrompt controlling for replay (GFlowPO without DMU vs. StablePrompt with replay) would isolate the GFlowNet contribution from the memory update. Currently both are changed simultaneously relative to StablePrompt.
