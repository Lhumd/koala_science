# 230fcebb — Why Depth Matters in Parallelizable Sequence Models: A Lie Algebraic View

## Verbatim abstract
"Our theory formulates a correspondence between the depth of a sequence model and the tower of Lie algebra extensions. Echoing recent theoretical studies, we characterize the Lie-algebraic class of constant-depth sequence models and their corresponding expressivity bounds. Furthermore, we analytically derive an approximation error bound and show that error diminishes exponentially as the depth increases, consistent with the strong empirical performance of these models."

## Methodology setup
Use Lie theory (Magnus expansion, derived/lower-central series classification) to formalize sequence-model expressivity. Map state-space models to controlled Lie equations on a Lie group; show that order-symmetric models (Transformers, diagonal SSMs) correspond to abelian Lie algebras; depth corresponds to the tower of Lie algebra extensions. Derive an exponential error decay bound as depth increases.

### 4f.1 Pre-result prediction
- Expert profile: Researcher who has published on transformer expressivity (Hahn 2020, Merrill 2020/2024, Liu et al. on TC0/AC0 circuits, state-tracking results from 2023-2025), familiar with linear-RNN/SSM theory (S4, Mamba, Linear Attention), and aware of Magnus-expansion/Lie-algebraic perspectives on sequence models (Muca Cirone 2024, Walker 2025).
- Predicted headline result: A Lie-algebraic framework would derive that constant-depth parallelizable models cannot solve non-abelian state-tracking problems (already known from Merrill et al.) and that depth helps polynomially or exponentially. The expert prior is that depth helps but the precise scaling has been an open question.
- Predicted directionality: With paper framing — positive expectation. The Lie-algebraic angle is natural for this question.
- Confidence in prediction: Medium-high. The general structure of the result is predictable (constant-depth is limited, depth helps). The specific exponential decay rate would be the novel quantitative claim.

## 4a. Atomic claim decomposition

| # | Phenomenon | Method | Setting | Result |
|---|---|---|---|---|
| 1 | Constant-depth parallelizable sequence models have limited expressivity | Lie-algebraic classification (abelian/nilpotent/solvable) | Sequence model expressivity theory | Echoes prior unsolvability results |
| 2 | Depth corresponds to tower of Lie algebra extensions | Theoretical correspondence | Sequence model → Lie group/algebra | Conceptual contribution |
| 3 | Approximation error decays exponentially with depth | Analytical bound derivation via Magnus expansion / Baker-Campbell-Hausdorff | Order-symmetric models on order-sensitive tasks | Quantitative theoretical contribution |
| 4 | Empirical validation on symbolic word + continuous state-tracking | Experiments | State-tracking tasks | Empirical |

## 4b. Closest-prior-work identification

- **Neighbor 1: Muca Cirone et al. (2024) — cited as providing "some intuition"** — Lie-algebraic perspective on sequence models. Delta: Muca Cirone provides intuition; this paper derives precise quantitative error-scaling laws.
- **Neighbor 2: Walker et al. (2025) — cited similarly** — also intuition without quantitative scaling. Same delta as above.
- **Neighbor 3: Hahn (2020); Merrill et al. (2020); Merrill et al. (2024) — cited** — circuit-complexity / TC0 perspective on transformer expressivity bounds. Delta: Lie-algebraic vs. circuit-complexity perspective; quantitative error scaling rather than yes/no expressivity.
- **Neighbor 4: Kim & Schuster (2023); Grazzi et al. (2025) — cited** — state-tracking unsolvability for constant-depth. Delta: this paper provides the depth-error scaling (rather than just unsolvability at constant depth).
- **Neighbor 5: Iserles (2008) — cited as classical Magnus expansion / Lie equation prior** — provides the mathematical machinery. Delta: this paper applies it to sequence models.

## 4c. Pseudo-novelty pattern check

- **Rebrand: NO.** Quantitative theorems with precise error-decay rates are not vocabulary.
- **Domain transfer: PARTIAL.** Brings classical Lie theory (Iserles, Agrachev-Sachkov control theory) to the sequence-model expressivity question. The new domain has specific properties (parallelizable models = order-symmetric → abelian Lie algebra) that the paper exploits non-trivially.
- **Composition without insight: NO.** The composition (Lie theory + Magnus expansion + sequence-model classification) produces a non-obvious quantitative result (exponential decay) that none of the pieces alone provides.
- **Resolution bump: NO.**

## 4d. Novel framing vs. novel science
The "tower of Lie algebra extensions ↔ depth" correspondence makes new predictions: it predicts the precise depth required for any given task's order-sensitivity class. The exponential decay theorem is a sharp quantitative prediction. Substantial new science.

## 4e. Concurrent work calibration
Muca Cirone (2024) and Walker (2025) are recent — the field is converging on Lie-algebraic perspectives. This paper's claim to novelty is the *quantitative* error scaling, which prior work did not derive.

### 4f.2 Actual result and override
- Actual headline result: Exponential error decay with depth, validated on symbolic word and continuous state-tracking experiments.
- Match assessment: matches prediction (positive direction; the specific exponential rate is the novel quantitative claim, but the qualitative shape was predictable).
- Override: "no override" (exponential vs. polynomial would be a sharper distinction, but expert prior would not strongly predict either direction).

## 4g. Positioning issues
- **Overclaim relative to evidence: NO.** Theorem statements precisely scoped.
- **Wrong reference class: NO.** Compares appropriately to circuit-complexity expressivity results and Lie-algebraic prior work.
- **Missing the natural baseline: NO.** Theory paper.
- **Inflated framing words: NO.** Measured.
- **Buried real contribution: NO.**

## Buried-contribution sweep
N/A.

## 4h. Originality score rationale
The strongest novelty axis is claim 3 (analytical exponential error decay bound) combined with claim 2 (the depth-to-tower-of-extensions correspondence). The closest priors (Muca Cirone 2024, Walker 2025) provided intuition without quantitative results; this paper closes that gap. Real and meaningful novelty within an active theoretical subfield. Bucket = 5.

## 5. Bucket score
Bucket = 5. Override: no override. **Final Originality = 5.**

## 6. Confidence
Confidence = 4. Read intro + abstract + §2 preliminaries (Lie groups/algebras, SSMs as Lie equations). Did not read the proof of the exponential decay theorem in detail. Named 5 plausible neighbors, all cited explicitly. Holding at 4 (not 5) per the prompt's standard for non-PaperLantern grounding (and theory-paper deltas are at the proof-technique level which I have not verified).
