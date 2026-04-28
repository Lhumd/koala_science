# Phase A Scratch: 5b4fcb9f — Soft Forward-Backward Representations for Zero-shot RL

## 4f.1 Pre-result prediction
- Expert profile: RL/offline RL researcher who knows forward-backward (FB) algorithms (Touati & Ollivier 2021) and zero-shot RL
- Predicted result: extending FB to non-linear utilities requires some form of soft/entropy regularization; the extension should be technically non-trivial but natural
- Predicted directionality: with paper
- Confidence: medium

## 4a. Atomic claim decomposition
| Claim # | Phenomenon | Method | Setting | Result |
|---|---|---|---|---|
| 1 | FB algorithms limited to linear utilities | Extension via soft/entropy regularization | Zero-shot RL with general utilities | Distribution matching + exploration now solvable zero-shot |
| 2 | Soft FB algorithm | Novel entropy-regularized forward-backward algorithm | Offline pretraining + zero-shot test | Captures stochastic behaviors; max-entropy objective |
| 3 | General utility zero-shot RL | Distribution matching, pure exploration tasks | Offline data | Zero-shot policy retrieval for any differentiable utility |

## 4b. Closest prior work
- **Neighbor 1:** Touati & Ollivier (2021) [Forward-Backward Representations] — "Direct predecessor. FB handles additive rewards linear in occupancy measure; this paper extends to general differentiable utilities via entropy regularization."
- **Neighbor 2:** Successor features (Barreto et al. 2017) — "General framework for zero-shot generalization; FB is a specific instantiation. Soft FB extends the same idea to non-linear settings."
- **Neighbor 3:** Various goal-conditioned RL / universal value functions — "Related zero-shot approaches; these specialize to specific reward classes; Soft FB handles general utilities."

## 4c. Pseudo-novelty patterns
- **Extension of FB (incremental theoretical contribution):** The core move is adding entropy regularization to FB to handle non-linear utilities. The insight that "max-entropy over occupancy measure" enables general utility handling is specific.
- Not a rebrand.

## 4d. Novel framing
"Zero-shot RL with general utilities" is a strictly more expressive problem class than "zero-shot RL with additive rewards." The paper provides the first solution in this class via Soft FB.

## 4f.2 Actual result and override
- Actual: "soft forward-backward algorithm that leverages entropy regularization to capture stochastic behaviors; approximately optimal policy retrieval for any general utility"
- Match: matches prediction
- Override: **no override**

## 4h. Score rationale
Extending FB from linear to general utilities is a real theoretical contribution. The entropy regularization insight is non-trivial and enables a strictly more expressive zero-shot RL framework. The result is in the expected direction for an expert who knows FB and entropy regularization, but the specific combination for general utilities is novel.

## Score & Confidence
- **Score: 6** (real extension; strictly more expressive problem class; entropy-regularized FB is the novel piece; Touati 2021 as clear predecessor)
- **Confidence: 3** (read abstract + intro + related work; Touati 2021 identified; delta articulable; didn't retrieve Touati full text)
