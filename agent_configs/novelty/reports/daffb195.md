The novelty here is real but narrow — GameVerse is a well-executed VLM-game benchmark with one methodological framing innovation, and the technical primitives behind that innovation have clear precedent. The framing claim worth quoting is from the abstract: *"Moving beyond traditional fire-and-forget evaluations, it uses a novel reflect-and-retry paradigm to assess how VLMs internalize visual experience and improve policies."*

The closest neighbors are:

1. **Reflexion (Shinn et al., 2023)** — verbal reinforcement-learning-via-self-reflection for LLM agents. The "reflect-and-retry" paradigm is conceptually a direct application of Reflexion's pattern (act → fail → reflect verbally → retry) to the VLM-game-benchmark setting, with the addition that reflection is grounded in expert tutorial videos rather than text-based environment feedback. Reflexion is the methodological ancestor and is the most relevant prior; an explicit "delta vs. Reflexion" paragraph would crystallize the contribution.

2. **Voyager (Wang et al., 2023, cited)** — Minecraft VLM/LLM agent with iterative skill library and self-reflection. The reflect-and-retry mechanism extends Voyager's self-improvement loop to a multi-game evaluation harness with structured tutorial-video grounding.

3. **The 2025 VLM-game benchmark cluster (BALROG, V-MAGE, VideoGameBench, FlashAdventure, Orak, LMGAME-BENCH — all in Table 1)** — fire-and-forget benchmarks. GameVerse's deltas are (a) the reflect-and-retry protocol and (b) the cognitive hierarchical taxonomy across 3 axes (image structure × temporal dynamics × causal linearity). The taxonomy is the genuinely original framing piece — none of the cited benchmarks have an axis-decomposed cognitive categorization.

Two observations:

(a) The "training-free analogue to RL plus SFT" framing (failure trajectories = in-context RL, expert tutorials = in-context SFT) is a useful pedagogical analogy, but it does not produce predictions that the broader in-context-learning literature (Min et al. 2022, Brown et al. 2020) does not already make. Could the authors clarify whether the claim is "this analogy is novel" or "this is the first to demonstrate the analogy in the VLM-game setting"? The latter framing is more honest.

(b) A direct baseline against "Reflexion-on-Voyager applied to our 15 games" would isolate whether GameVerse's specific reflect-and-retry protocol (with video-grounded reflection) contributes beyond what generic Reflexion gives. The current ablations show that reflect-and-retry helps vs. fire-and-forget; the methodological-equivalent comparison (vs. text-grounded Reflexion) would be more diagnostic.

A concrete suggestion: the cognitive hierarchical taxonomy (§3 / Table 1) is the most differentiated contribution and would benefit from being framed predictively rather than descriptively — e.g., "category X predicts difficulty tier Y for VLM agents because of axis Z." The current taxonomy is presented as a categorization scheme; reframing it as a hypothesis-generating framework would strengthen the citation magnetism for downstream benchmark papers.
