# Novelty Audit — Tabula RASA (2f23edaf)

**The novel axis is combining circuit-complexity-motivated sparse adjacency masking (Dwivedi & Bresson 2020) with edge-type bias terms into RASA, with the specific contribution being the search space reduction formalization: RASA reduces the exponential attention search space from O(2^n) to O(2^m) for graphs with n nodes and m edges.**

## Decomposition

- **Sparse adjacency masking (prior art):** Dwivedi & Bresson (2020) already introduce Sparse Graph Transformers with adjacency-based masking. RASA's masking component directly follows this work.
- **Edge-type biases (incremental addition):** RASA adds learnable biases b_r for each relation type r to attention scores between connected positions. This is a small addition over Dwivedi but not a fundamental change.
- **Search space reduction formalization (novel contribution):** The explicit characterization of the search space as O(2^m) for sparse graphs (vs. O(2^n) for dense attention) provides a formal theoretical justification for why the architectural change helps multi-hop reasoning — beyond the circuit complexity lower bound (Sanford et al. 2023) which just says Ω(k) layers are needed. This is the specific novel theoretical contribution.
- **Empirical result (solid):** 97.7% on MetaQA 3-hop vs. EmbedKGQA 94.8% (2.9pp gain) confirms practical utility.

## Reframe

RASA is most accurately framed as "the minimal modification to standard transformers that, via a search-space-reduction argument, provides structural inductive bias for multi-hop relational reasoning." The "Tabula RASA" title is somewhat misleading (it suggests starting fresh, when RASA is actually a minimal add-on).

## Concrete fix

A comparison against Graphormer (Ying et al. 2021) on MetaQA would be more informative than comparison against EmbedKGQA (an embedding method, not a transformer). Graphormer is the most direct related graph transformer baseline.
