# Novelty Audit — Certificate-Guided Pruning (5c3d6bff)

**The novel axis is making the pruning active set At a computable first-class object with measurable volume shrinkage, explicitly exposing what zooming (Bubeck et al. 2011) keeps implicit; the sample complexity Õ(ε^{-(2+α)}) is unchanged from prior art.**

## Decomposition

- **Sample complexity (not novel):** The rate Õ(ε^{-(2+α)}) under the near-optimality dimension condition matches HOO/zooming (Bubeck et al. 2011). The paper is transparent about this: "our bound is the same as zooming but with explicit certificates."
- **Certificate mechanism (novel):** In zooming, the active set is an analysis artifact — it does not exist as a computable runtime object. CGP constructs At := {x : Ut(x) ≥ ℓt} explicitly, making Vol(At) a measurable shrinkage quantity. This enables principled stopping (stop when Vol(At) < ε-target) and anytime optimality bounds that prior methods cannot provide. This is the strongest novel axis.
- **Unknown-L guarantee (specifically novel):** CGP-Adaptive provides the first certificate-valid guarantee for unknown Lipschitz constant with only O(log T) multiplicative overhead. LIPO (Malherbe & Vayatis 2017) handles unknown L but lacks certificates; this closes that gap.
- **High-dimensional certificates (CGP-TR):** Trust region variant with local certificates scales to d > 50 where global Lipschitz methods fail entirely; outperforms TuRBO by 9–12% while additionally providing local optimality certificates (a capability TuRBO explicitly lacks).

## Reframe

The contribution is most accurately framed as "the first anytime-computable certificate for Lipschitz optimization that is valid under noise, with extensions to unknown L and high dimension" — not a new complexity class, but a new guarantees class. The Bubeck 2011 comparison is the load-bearing prior-work claim: could the authors add a column to Table 1 explicitly listing HOO/zooming and confirming their certificate fields?

## Concrete fix

Adding a direct numerical comparison with LIPO (Malherbe & Vayatis 2017) in the benchmark tables, and a clearer statement of the complexity class position ("we achieve the same rate as HOO, plus certificates"), would make the contribution precise and prevent reviewers from expecting a complexity improvement.
