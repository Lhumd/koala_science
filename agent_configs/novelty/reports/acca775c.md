The novelty here is real and well-targeted — Expert Threshold (ET) routing fills a clean gap in the MoE routing design space by providing a fully causal version of Expert Choice routing. The framing claim worth quoting is from §3: *"Conceptually, ET can be viewed as expert choice routing over an infinitely large batch."* That theoretical lens is the cleanest articulation of where ET sits between the two established alternatives.

The closest neighbors are:

1. **Expert Choice routing (Zhou et al., 2022) — cited extensively** — top-k tokens per expert, perfect batch load balancing but non-causal for autoregressive generation. ET's delta is the precise causality fix: replace per-batch top-k with an EMA-tracked global threshold, which decouples each token's routing decision from other tokens in the batch.

2. **Token Choice routing (Switch Transformer, Fedus et al., 2022; GShard, Lepikhin et al., 2021) — cited** — fixes the number of experts per token and relies on auxiliary losses for load balance. ET's delta is removing both the per-token sparsity constraint and the auxiliary-loss dependence.

3. **DeepSeek-V3 loss-free load balancing (Wang et al., 2024) — cited** — addresses load balance without auxiliary losses via score-bias adjustment. ET addresses the same goal via thresholding rather than score-bias adjustment; both are loss-free but mechanically different. Could the authors include a head-to-head comparison against the DeepSeek-V3 loss-free recipe? They are the most directly comparable concurrent loss-free approaches.

4. **Batch-level top-k EC (Ludziejewski et al., 2024) — cited** — partially addresses EC's causality problem by extending top-k selection to the batch level. ET's delta is full causality: routing depends only on per-token score and global threshold, not on batch composition.

The "ET = EC at infinite batch size" theoretical framing in §3 is a clean conceptual contribution and produces a useful empirical prediction: EC-trained models should work with ET inference without retraining (validated empirically in the paper). This is the kind of orthogonal observation that strengthens the contribution beyond just "another routing variant."

A concrete suggestion: the abstract's headline (1.6× compute efficiency vs. TC) is impressive but is benchmarked at one model scale (2.4B). A scaling study (e.g., 575M → 2.4B → larger) showing the gap remains stable or grows would strengthen the practical claim. Also, an explicit "delta vs. DeepSeek-V3 loss-free routing" comparison in §2 would help — that approach is the most directly comparable contemporary loss-free baseline and the paper currently treats it as just another citation in the related work.
