# acca775c — Expert Threshold Routing for Autoregressive LM with Dynamic Computation Allocation and Load Balancing

## Verbatim abstract
"We propose Expert Threshold (ET) routing, where each expert maintains an exponential moving average (EMA) threshold estimated from the global token distribution. At both training and inference, each token is independently routed to an expert if its score exceeds the expert's threshold, enabling dynamic computation allocation while achieving load balance without auxiliary losses. This fully causal mechanism eliminates dependence on other tokens in the batch, making it well-suited for autoregressive language modeling."

## Methodology setup
Three-way comparison: TC (Token Choice — fixed top-G experts per token, requires aux losses for balance), EC (Expert Choice — top-k tokens per expert, perfect balance but non-causal), ET (Expert Threshold — EMA-tracked global threshold per expert, both causal and balanced). ET routes via z_{t,i} = 1{r_{t,i} > c_i} where c_i is updated as EMA of k-th largest score per batch.

### 4f.1 Pre-result prediction
- Expert profile: Researcher who has published on MoE routing (Switch Transformer, GShard, DeepSeek MoE), familiar with the TC vs. EC tradeoff, the causality problem with EC for autoregressive LMs (cited as Wang 2024, Ludziejewski 2024), and loss-free load balancing approaches (Wang 2024 DeepSeek).
- Predicted headline result: A causal-EC variant via global thresholds would close the gap with TC + outperform it modestly because (a) it removes the auxiliary-loss interference, (b) enables dynamic computation. Expected gains: small but consistent improvements (0.05-0.1 cross-entropy loss equivalent), claimed compute efficiency ~1.5×.
- Predicted directionality: With paper framing — positive expectation. The "EC as infinite-batch-size limit, ET as the causal version" framing is natural.
- Confidence in prediction: High. The space of MoE routing variants has been exhaustively explored; this is a clean and obvious gap to fill.

## 4a. Atomic claim decomposition

| # | Phenomenon | Method | Setting | Result |
|---|---|---|---|---|
| 1 | TC has load-imbalance problems requiring aux losses; EC is non-causal | Conceptual analysis | MoE routing for autoregressive LMs | Motivation |
| 2 | An EMA-tracked global threshold per expert achieves load balance without aux losses and is fully causal | ET routing algorithm | MoE routing | Methodological contribution |
| 3 | ET = EC in the infinite-batch limit | Theoretical observation | Routing equivalence | Conceptual framing |
| 4 | ET outperforms TC by 0.067 in cross-entropy on 2.4B model trained on FineWeb-Edu | Empirical | MoE pretraining | Empirical (1.6× compute efficiency) |
| 5 | EC-trained models can use ET inference without retraining | Empirical | Train-inference flexibility | Bonus contribution |

## 4b. Closest-prior-work identification

- **Neighbor 1: Expert Choice (Zhou et al., 2022) — cited extensively** — top-k tokens per expert, perfect batch load balancing but non-causal. Delta: ET is the causal version of EC via global threshold.
- **Neighbor 2: Switch Transformer (Fedus et al., 2022) and GShard (Lepikhin et al., 2021) — cited** — Token Choice routing with auxiliary losses. Delta: ET removes aux-loss dependence and adds dynamic computation.
- **Neighbor 3: DeepSeek-V3 loss-free load balancing (Wang et al., 2024) — cited** — uses bias-adjustment for load balance without aux loss. Delta: ET uses thresholding rather than score-bias adjustment; both are loss-free but mechanically different.
- **Neighbor 4: Batch-level top-k EC (Ludziejewski et al., 2024) — cited** — extends EC to batch-level. Delta: still not fully causal; ET is.
- **Neighbor 5: PID controller routing (Team 2025a) — cited** — uses PID feedback for load balance. Delta: ET uses simpler EMA threshold.

## 4c. Pseudo-novelty pattern check

- **Rebrand: NO.** Concretely defined algorithm with new closed-form solution.
- **Domain transfer: NO.**
- **Composition without insight: PARTIAL.** Composes (EC's top-k-per-expert idea) + (EMA tracking) + (per-token thresholding). The combination produces a non-obvious property (causal EC) that addresses a well-known problem (EC's non-causality). Not pure additive.
- **Resolution bump: NO.**

## 4d. Novel framing vs. novel science
"ET as EC at infinite batch size" is a clean theoretical framing that makes new predictions: EC-trained models should work with ET inference (validated by claim 5). Concrete predictive content.

## 4e. Concurrent work calibration
Several 2025 MoE routing variants are concurrent. The specific EMA-threshold mechanism for causal routing is, to my reading, distinctive.

### 4f.2 Actual result and override
- Actual headline result: ET outperforms TC by 0.067 cross-entropy on 2.4B model; 1.6× compute efficiency; near-perfect load balancing without aux losses.
- Match assessment: matches prediction (positive direction, magnitude in expected band).
- Override: "no override"

## 4g. Positioning issues
- **Overclaim relative to evidence: NO.**
- **Wrong reference class: NO.**
- **Missing the natural baseline: NO.** Includes TC, Dense, EC variants.
- **Inflated framing words: NO.**
- **Buried real contribution: NO.**

## Buried-contribution sweep
N/A.

## 4h. Originality score rationale
The strongest novelty axis is claim 2 (EMA-tracked global threshold for fully causal MoE routing) combined with claim 3 (ET = EC at infinite batch). The closest priors (EC for the routing pattern, DeepSeek loss-free for the no-aux-loss design, Ludziejewski for batch-level extension) collectively cover the design space; ET fills a clean gap (causal EC) with a simple mechanism. Real but moderate novelty in the MoE routing subfield. Bucket = 4.

## 5. Bucket score
Bucket = 4. Override: no override. **Final Originality = 4.**

## 6. Confidence
Confidence = 4. Read intro + abstract + §2 preliminaries + §3 method. Named 5 plausible neighbors, all cited. Holding at 4.
