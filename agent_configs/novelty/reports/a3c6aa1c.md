# Novelty Audit — 2-Step Agent (a3c6aa1c)

**The novel axis is a rigorous Bayesian formalism for ML-assisted decision making that separates the prior update step from the action step, formally showing that the same ML recommendation can produce opposite actions depending on agent priors — a qualitative result argued in van Geloven et al. (2025) but not previously formalized.**

## Decomposition

- **"Priors matter for ML-DS" (known argument):** van Geloven et al. (2025) and related work argue that agent prior beliefs affect ML decision support impact. The paper formalizes this.
- **2-Step Agent formalism (the novel piece):** The Bayesian two-step framework (step 1: posterior update given ML prediction; step 2: action from posterior) provides a rigorous computational model for agent-ML-DS interaction. The formal model enables precise analysis of when and why the same ML output leads to different (or opposite) actions.
- **Empirical scope (limited):** The validation is on medical domain simulations only; "ML-DS with causal models is left for future work." This limits the "general" claim.

## Reframe

The contribution is most accurately framed as: "a formal Bayesian framework that explains contradictory responses to identical ML recommendations through differences in agent prior beliefs, with implications for RCT design in ML-assisted decision making." The "general computational framework" claim in the abstract is slightly overclaiming given the simulation-only validation.

## Concrete fix

Grounding the framework in empirical data from existing human-AI studies (rather than only simulations) would strengthen the "general" claim. Alternatively, comparing the framework's predictions against observed behavioral data from ML-DS RCTs would validate the formalism.
