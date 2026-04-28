# Phase A Scratch: 2f23edaf — Tabula RASA (RASA Attention for Relational Reasoning)

## 4f.1 Pre-result prediction
- Expert profile: researcher familiar with graph transformers (Dwivedi 2020, Graphormer), transformer circuit complexity (Merrill & Sabharwal 2022, Sanford et al. 2023), and KGQA methods
- Predicted headline result: sparse adjacency masking + edge-type biases should improve multi-hop KGQA; the TC0 lower bound for graph connectivity is a known result that motivates graph-aware attention
- Predicted directionality: with the paper (adding structural inductive bias helps multi-hop reasoning)
- Confidence in prediction: medium-high

---

## 4a. Atomic claim decomposition

| Claim # | Phenomenon | Method | Setting | Result |
|---|---|---|---|---|
| 1 | Transformers can't solve graph connectivity in constant depth | TC0 circuit complexity analysis (Sanford et al. 2023 cited) | Standard transformer | Ω(k) layers necessary for k-hop reasoning |
| 2 | RASA search space reduction | Sparse adjacency masking: O(2^m) instead of O(2^n) | KGQA with knowledge graph | Search space reduction by exponential factor |
| 3 | RASA attention mechanism | Edge-type biases + sparse adjacency masking (minimal modification) | MetaQA multi-hop KGQA | 97.7% on 3-hop (vs. EmbedKGQA 94.8%) |
| 4 | Minimal overhead | Edge-type embeddings + sparse masking only | Pre-trained transformers | "Minimal implementation overhead" claim |

## 4b. Closest-prior-work identification

- **Neighbor 1:** Dwivedi & Bresson (2020) [Sparse Graph Transformers] — "Introduces adjacency-based sparse masking; RASA adds edge-type biases on top. The masking component of RASA is directly from Dwivedi; the novel piece is the edge-type bias + combination."
- **Neighbor 2:** Sanford et al. (2023) [transformers cannot solve graph connectivity in constant depth] — "Provides the theoretical lower bound that motivates RASA; paper extends this to show RASA reduces search space, but the lower bound itself is prior work."
- **Neighbor 3:** Graphormer (Ying et al. 2021) [spatial + centrality encodings] — "Graphormer uses graph structure via spatial encodings; RASA focuses specifically on multi-hop KGQA with edge types; more targeted and minimal."

## 4c. Pseudo-novelty pattern check

- **Rebrand?** No — RASA adds edge-type biases that Dwivedi doesn't have.
- **Domain transfer?** No — within graph transformer / KGQA space.
- **Composition without insight?** Mostly — Dwivedi masking + Graphormer-style edge biases. The insight is the circuit complexity analysis showing why this minimal modification suffices.
- **Resolution bump?** No.

## 4d. Novel framing vs. novel science

The "search space reduction from O(2^n) to O(2^m)" formulation is the cleanest theoretical contribution: sparse masking with m edges (m << n nodes) reduces the exponential search space. This is a precise claim that motivates the architectural choice.

## 4e. Concurrent work calibration

None identified.

## 4f.2 Actual result and override

- Actual result: 97.7% on MetaQA 3-hop; search space reduction formalized; Ω(k) depth lower bound confirmed
- Match: matches prediction
- Override: **no override**

## 4g. Positioning issues

- **"Minimal modification":** Accurate — only edge-type embeddings + sparse masking.
- **Comparison to Graphormer:** The main results compare to EmbedKGQA (embedding method) rather than Graphormer; a Graphormer baseline on MetaQA would be more informative.

## 4h. Originality score rationale

The combination of circuit complexity analysis + search space formalization + minimal-overhead implementation makes RASA a well-justified contribution. The circuit complexity argument (from Sanford et al. 2023) is prior work, but applying it to justify the specific architecture change is novel. The edge-type bias addition over Dwivedi 2020's masking is small but theoretically motivated. The results are clear. Score higher than pure composition because the theoretical grounding is specific and the implementation is minimal.

## Score & Confidence

- **Originality score: 6** (weak accept — theoretical motivation via circuit complexity + search space reduction; Dwivedi 2020 masking is prior art; edge-type bias adds specificity; solid theory paper)
- **Confidence: 4** (read full related work; Dwivedi 2020 and Sanford 2023 precisely identified; delta articulable per axis)
