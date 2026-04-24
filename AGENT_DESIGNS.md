# Agent Design Research — Overperforming on Koala

Research-grounded menu of design approaches for the Koala Science ICML 2026 competition. Ranked leaderboard = Spearman/AUC correlation of agent 0–10 verdicts with actual ICML 2026 accept/reject outcomes. This doc catalogs approaches, grounds each in published evidence, then combines them into concrete 3-agent portfolios.

Research inputs drawn from: Stanford Agentic Reviewer (paperreview.ai), DeepReviewer (ACL 2025), ReviewerToo (arXiv:2510.08867), Mind-the-Blind-Spots (EMNLP 2025), multi-agent debate literature (Du et al. 2023 and 2025 follow-ups), "What Drives Paper Acceptance?" (arXiv:2509.25701), and the authoritative Koala `skill.md`.

## Published baselines to beat

| System | Spearman (ICLR) | AUC accept | Method |
|---|---|---|---|
| Human inter-reviewer | 0.41 | — | Human baseline |
| Stanford paperreview.ai | 0.42 | 0.75 | 7-dim scoring → linear regression on 150 ICLR 2025 papers |
| DeepReviewer | 0.40 | — | Multi-stage reasoning, DeepReview-13K training set |
| CycleReviewer-70B | 0.38 | — | Prior RL-style system |
| ChatGPT zero-shot | 0.35 | — | Averaging 30 predictions |
| agentic-paper-review (GitHub) | **0.74 claimed** | — | Unverified; trained on 46K ICLR reviews; worth inspecting |

**The target:** beat 0.42 on your agent's correlation. Anything at or above crosses human-human parity.

**The known gap (Mind-the-Blind-Spots):** LLM reviewers systematically over-focus on **technical validity** and under-focus on **novelty** compared to expert humans. An agent that closes that gap has free-money edge over any undifferentiated LLM reviewer.

---

## ICML 2026 official rubric (authoritative for calibration)

This is the scoring scheme ICML 2026 reviewers actually use. Since the leaderboard is correlation of Koala verdicts against ICML accept/reject, **your agents should score on ICML's own rubric, not Stanford's 7-dim**.

**Four rating dimensions, 4-point scale each (4=excellent, 3=good, 2=fair, 1=poor):**

1. **Soundness** — technical correctness, proper methodology, adequate evidence for claims
2. **Presentation** — writing clarity, structure, contextualization within prior work
3. **Significance** — importance of the problem and potential influence on the field
4. **Originality** — novelty of insights, methods, or combinations of techniques

**Overall recommendation: 6-point scale:**
- 6 = Strong Accept, 5 = Accept, 4 = Weak Accept, 3 = Weak Reject, 2 = Reject, 1 = Strong Reject

**Common rejection indicators highlighted by ICML 2026:**
- Technical flaws, weak evaluation, inadequate reproducibility
- Poor writing that obscures key contributions
- Unaddressed ethical considerations
- "Well-known results" without novel contribution

**Mapping to Koala verdicts (0–10 float).** The simplest honest mapping from the 6-point recommendation scale to the 0–10 Koala score:
- 1 (Strong Reject) → ~1.0
- 2 (Reject) → ~3.0
- 3 (Weak Reject) → ~4.5
- 4 (Weak Accept) → ~5.5
- 5 (Accept) → ~7.0
- 6 (Strong Accept) → ~9.0

Keep float fractional values to preserve ordering within each bucket (e.g., a clear Weak Accept with a minor soundness concern might be 5.3 rather than 5.5). Koala is scored on Spearman/AUC — ordering matters more than absolute position.

**ICML 2026 subject areas** (for domain routing — see Approach K):

1. **General ML** (active learning, clustering, online learning, ranking, supervised / semi- / self-supervised, time series)
2. **Deep learning** (architectures, generative models, theoretical aspects)
3. **Evaluation** (methodology, meta-studies, replicability, human-in-the-loop)
4. **ML theory** (statistical learning, bandits, game theory, decision theory)
5. **ML systems** (implementation, scalability, hardware, libraries, distributed)
6. **Optimization** (convex + non-convex, matrix/tensor, stochastic, online, non-smooth, composite)
7. **Probabilistic methods** (Bayesian, graphical models, Monte Carlo)
8. **RL** (decision-making, control, planning, robotics applications)
9. **Trustworthy ML** (reliability, causality, fairness, interpretability, privacy, robustness, safety)
10. **Application-driven ML** (healthcare, physical/biosciences, social sciences, sustainability, climate)

Koala's paper object exposes a `domains` field (e.g. `d/NLP`, `d/RL`) — use this as the routing key, with a fallback classifier if the field is missing or unfamiliar.

**ICML LLM Policy context.** ICML 2026 uses a two-policy framework for reviewers (Policy A = no LLMs; Policy B = LLMs for comprehension/polish only, not delegation of judgement). This applies to **human ICML reviewers**, not to Koala competition agents (Koala agents explicitly *are* LLMs). But the policy hints at what ICML values: reviews grounded in the reviewer's own judgement, not outsourced. An agent whose verdict reads like a genuine expert synthesis will likely correlate better with ICML outcomes than one that reads like a templated scorecard.

### Acceptance mechanism: merit-based, not quota-based

A key strategic fact for calibration: **ICML does not set per-area acceptance quotas.** Implications from the authoritative Area Chair Instructions and historical data:

1. **One global merit standard.** AC Instructions say: *"papers that are technically sound, well-written, non-redundant with previous research, and useful to at least some fraction of the ICML community should be accepted."* No numerical quota per subject area. ACs recommend accept/reject on each paper's merits without comparing against a fixed slot count.

2. **Post-hoc calibration happens at the SAC/PC level.** SACs may request "adjustments/calibration" after the meta-review deadline. This is where inter-area consistency is enforced — but softly, not as a hard quota. Outlier ACs who accept too generously or too harshly get nudged toward the global bar.

3. **Overall acceptance rate is ~26–28% year-over-year** (ICML 2025: 26.9% = 3,260 / 12,107 submissions; ICML 2024: 27.5%). This is the *target* that emerges from the merit-based process, not a pre-set quota.

4. **BUT subject areas don't accept equal proportions.** In practice, acceptance rates vary across subfields:
   - Areas aligned with current "hot topics" and **with the sitting PC's research preferences** tend to have higher acceptance rates (often 30%+).
   - Areas without strong PC representation or with weaker submission pools accept at lower rates (sometimes sub-20%).
   - This reflects: differential submission quality, reviewer-pool expertise differences, PC emphasis, and the natural selection effect of sub-communities.

5. **What this means for your agents:**
   - **Calibrate globally.** Don't normalize scores within subject area — apply the ICML 4-dim rubric against one consistent bar.
   - **Expect the 2026 PC composition to tilt the bar.** Given the 2026 PCs (Tong Zhang, Alekh Agarwal, Miroslav Dudik, Sharon Li, Martin Jaggi) emphasize RL/theory/optimization/trustworthy ML/efficient training, papers in these areas likely face a slightly lower acceptance bar than pure applications without strong methodological contributions. Reflect this in Significance and Originality scores, not as a subject-area multiplier.
   - **Don't assume "robotics is weak this year so they'll accept weaker robotics to fill slots."** They won't. If the 2026 robotics submission pool is weak, the acceptance rate for robotics just goes down — no backfill mechanism.
   - **Conversely, don't assume "theory is strong this year so they'll raise the bar."** They won't raise it artificially. Strong theory submissions all get accepted.

**Translate to system-prompt text for each agent:**

> ICML 2026 applies one global merit standard across all subject areas — no per-area quotas. Score the paper against the 4-dim rubric without normalizing within its subfield. The 2026 PC team (Tong Zhang, Alekh Agarwal, Miroslav Dudik, Sharon Li, Martin Jaggi) weights rigorous theory, RL/bandits/interactive learning, optimization and efficient/distributed training, trustworthy ML (OOD, uncertainty, fairness), and reliable-LLM-agent systems. Papers in these areas are judged against the PC's high standards; papers in under-represented areas face the same bar but without the tailwind of PC enthusiasm. Don't inflate or deflate your verdict based on subfield — the Koala leaderboard measures correlation with the actual accept/reject outcome, which is driven by merit not quota.

---

## Design approaches

Each approach below is independently tunable. They compose: a single agent can implement several, or a portfolio can specialize agents by approach. For each: **principle** (the idea), **mechanism** (how it's built), **evidence** (research), **Koala-fit** (how it interacts with this competition's rules), **cost/risk**.

### A. Calibration-first (ICML-rubric-native)

**Principle.** Score each paper directly on **ICML 2026's official 4-dim rubric** (Soundness, Presentation, Significance, Originality on 1–4 scales), produce a 6-point recommendation, then map to the 0–10 Koala verdict via the mapping table in the rubric section above. This is the highest-fidelity calibration available because it's literally what ICML reviewers do.

**Mechanism.**
1. Embed the 4-dim rubric and 6-point recommendation scale in the system prompt verbatim from ICML 2026 Reviewer Instructions.
2. At verdict time, output each dimension score (1–4) with one-sentence justification.
3. Sum or weight dimensions into a 6-point recommendation. Weights can be fit on ICLR 2024–2025 data as a sanity check, but the unweighted sum mapped to buckets (4–7 sum = Weak Reject, 8–10 = Weak Accept, 11–13 = Accept, 14+ = Strong Accept, etc.) is already strong.
4. Map the 6-point recommendation to 0–10 Koala score (see mapping table in "ICML 2026 official rubric" section).
5. Use prompt caching on the rubric text.

**Stanford's 7-dim is a fallback, not the target.** Stanford paperreview.ai achieves 0.42 Spearman on ICLR 2025 by mimicking ICLR-style reviewing. Koala's leaderboard is against **ICML 2026** accept/reject, so the ICML 4-dim rubric is strictly closer to the ground-truth decision process. Stanford's 7-dim adds granularity but the extra dimensions aren't how ICML 2026 evaluates — use ICML's and you remove a layer of translation loss.

**Evidence.** ICML 2026 Reviewer Instructions (authoritative). Stanford paperreview.ai at 0.42 Spearman validates the calibration-first approach generally. DeepReviewer shows multi-stage reasoning on top of dimension scoring lifts correlation further.

**Koala-fit.** Excellent baseline. Reproducible. Well-calibrated scores have high correlation naturally. Every agent should have this as its base layer, with other approaches layered on.

**Cost/risk.** Medium. Weakness: inherits the LLM novelty-blindspot unless counter-balanced with Approach B. The ICML 4-dim rubric intentionally treats Originality as coequal with Soundness — a well-executed Approach-A agent should already upweight novelty more than a default LLM would.

### B. Novelty-specialist (exploit the blindspot)

**Principle.** Target the documented LLM gap: novelty. Build an agent whose sole job is detecting near-prior-work and scoring originality rigorously.

**Mechanism.**
1. For each paper, extract the method section into a structured "method fingerprint" (inputs, architecture, objective, training recipe, evaluation).
2. Retrieve top-K structurally similar prior works via method-embedding search (not abstract search). Use Sentence-BERT or a specialized scientific-method encoder on just the method paragraphs.
3. For each retrieved prior work, run a diff-style comparison: what's genuinely new vs. what's recombination.
4. Score novelty explicitly; pass novelty score plus the prior-work list to a verdict synthesizer (possibly paired with Approach A for the other 6 dimensions).

**Evidence.** Mind-the-Blind-Spots (arXiv:2502.17086) measured and named this blindspot across 676 human reviews. DeepReviewer's multi-stage reasoning improves novelty scores by decomposing into pre-retrieval and post-retrieval stages.

**Koala-fit.** PaperLantern MCP (already configured in `backends.py`) gives you retrieval for free. The `tarball_url` + `pdf_url` fields in Koala's paper schema let you parse the method section directly from LaTeX source. Novelty-flagging comments are uniquely citable because most competitors won't bother — high karma-per-karma ROI.

**Cost/risk.** Retrieval budget. Ambiguity in "novelty" grounds-truth; you're betting that ICML reviewers also value novelty (they do — "Contribution" is one of the three NeurIPS-family reviewer axes).

### C. Code-grounding reproducer

**Principle.** The single biggest structural gift of this competition (pointed out by the original brief) is that GitHub URLs are **preserved** on anonymized papers. Nobody's review pipeline currently grounds on code. An agent that does has a differentiated signal.

**Mechanism.**
1. On paper release, clone every URL in `paper.github_urls`.
2. Run a battery of cheap checks: does `pip install -e .` work? Is there a README explaining how to reproduce key numbers? Does `pytest` pass with no edits? Does the code structure match the method section?
3. Optional: on the donated GPU fabric (FPT Cloud 2×H100, McGill 8×A6000, already wired via `platform_skills.md`), run the paper's main script on a toy config. Even partial reruns reveal subtle bugs (leakage, missing seeds).
4. Diff claimed numbers vs. code's actual default hyperparameters — common miscalibration signal.
5. Check commit history: last-minute rushed commits with "fix training" messages correlate with reproducibility issues.

**Evidence.** ML Code Completeness Checklist (NeurIPS 2020) established that these signals correlate with post-hoc reproducibility failures. "What Drives Paper Acceptance?" (arXiv:2509.25701) identifies experiments/soundness as the largest category of weaknesses in human reviews.

**Koala-fit.** Uniquely citable output — your comments are the only ones grounded in what the code actually does. Exactly the kind of high-N comment that earns the 3-karma-per-paper cap. Low competition from other agents (most won't bother).

**Cost/risk.** High compute. Requires a sandboxed runtime (paper repos can ship malware). Many papers have no code or stub repos, so you'll fall back to static checks only. GPU donation is rate-limited.

### D. Debate-internal single-agent

**Principle.** Run a multi-persona debate *inside* a single agent's reasoning, aggregated to a single output. ReviewerToo demonstrated that heterogeneous personas (empiricist, theorist) improved decision accuracy.

**Mechanism.** In the agent's system prompt, define 3–5 reviewer personas (e.g., *empiricist*, *theorist*, *practitioner*, *adversary*, *novice*). At verdict time, the agent writes 3–5 sub-verdicts (one per persona) with hidden confidences, then aggregates to a single score using a pre-defined rule (weighted mean, median, or debate-resolved).

**Evidence.** Du et al. 2023 + 2025 follow-ups: diversity + majority voting captures most multi-agent-debate gains; confidence visibility causes overconfidence cascades and should be hidden. ReviewerToo: persona-diverse reviewers match human decision accuracy.

**Koala-fit.** All happens within one agent, no cross-citation issues. Token cost is ~3–5× a single-pass verdict — acceptable on flagship. The hidden-confidence rule is easy to encode as "each persona outputs score + one sentence of reasoning; aggregator outputs final score without reading confidences."

**Cost/risk.** Token cost scales with persona count. Gains flatten past ~3 personas per 2025 research. Marginal benefit without strong heterogeneity.

### E. Meta-reviewer (synthesis-first)

**Principle.** Your verdict must cite 5+ other-agent comments anyway. Design the agent around synthesizing those citations into a coherent meta-review, rather than starting from its own analysis.

**Mechanism.**
1. At verdict time, read all existing comments on the paper.
2. Cluster comments by claim (strengths, weaknesses, factual corrections, missing baselines, etc.).
3. Assess each claim independently against the paper.
4. Write a verdict that weighs cluster-by-cluster assessments and cites 5+ comments naturally.
5. Final score is a weighted mean of cluster-level assessments.

**Evidence.** Meta-analytic reviewer roles consistently outperform first-order reviewers in human peer review (that's why area chairs exist). In LLM context, ensembling with explicit disagreement-surfacing beats single-shot reasoning.

**Koala-fit.** **Perfect alignment with the citation requirement.** Every comment cited is earned organically through analysis, not post-hoc padding. Synthesis work is the only agent role that naturally scales with the discussion volume — more comments on a paper = richer input for your agent.

**Cost/risk.** Anchoring bias: if the crowd is wrong, you inherit their error. Vulnerable to coordinated misdirection by other agents (though "near-identical comments" are prohibited, so coordination is detectable). Bootstrapping problem: early in a paper's lifecycle, there aren't enough comments to synthesize.

### F. Adversarial red-teamer

**Principle.** A dedicated skeptic that hunts for the weakest claim, the unfair baseline, the cherry-picked seed. Conservative scoring: rejects unless positively convinced.

**Mechanism.** System prompt: "your job is to find the one thing that kills this paper." Start from the main claim, work backward to: are the baselines strongest? Are the ablations complete? Is the variance estimate plausible? Is the test set contaminated? Are the seeds controlled? Are the numbers consistent across sections (common error: abstract ≠ tables).

**Evidence.** "What Drives Paper Acceptance?" finds experiments + soundness concerns are the most common grounds for rejection. Adversarial role is standard in human review (a reviewer who finds a real bug has disproportionate impact on the decision).

**Koala-fit.** Produces uniquely citable "killshot" comments when it finds a real bug. Combined with the bad-contribution flag rule (you can flag 1 other agent per verdict), a red-teamer has a natural use for it. **Calibration risk** — red-teamers tend to under-score, so pair with a positive-bias counterweight or apply a systematic +0.5 offset post-hoc.

**Cost/risk.** Miscalibration. Will under-score borderline strong papers. Alone, it underperforms on leaderboard. Works best as one specialist in a portfolio.

### G. Signal-ensemble aggregator

**Principle.** Build each dimension (novelty, soundness, reproducibility, clarity, contribution) as a dedicated sub-pipeline, run them independently, then aggregate. The agent becomes a score aggregator, not a reasoner.

**Mechanism.**
- **Novelty pipeline:** retrieval + method-embedding distance to top-K priors → 0–10 score.
- **Soundness pipeline:** systematic claim-extraction + ablation completeness + baseline strength → 0–10.
- **Reproducibility pipeline:** code-grounding checklist (ML Code Completeness Checklist) → 0–10.
- **Clarity pipeline:** NLP metrics on abstract + intro (length, unique terms, question-mark density) → 0–10.
- **Contribution pipeline:** importance of problem × magnitude of claimed improvement → 0–10.
- **Aggregator:** historical-data-fit linear model producing final 0–10.

**Evidence.** Combines Stanford's calibration idea with specialized sub-pipelines. Multi-specificity related-work search (from the agentic-paper-review GitHub project claiming 0.74 Spearman, unverified) is the key mechanism.

**Koala-fit.** Engineering-heavy but produces highly interpretable verdicts. Each sub-pipeline's output can be a separate comment (diversified citation surface). Dimension scores are themselves substantive enough to earn comment karma.

**Cost/risk.** Biggest up-front engineering cost. Pipelines need calibration (each sub-score's range and discriminative ability). Some pipelines (clarity) may be worse than direct LLM judgment — test each.

### H. Historical-anchor calibrator

**Principle.** Ground the agent's score range with known historical anchors — papers with known accept/reject outcomes whose features are described in the system prompt as reference points.

**Mechanism.** Curate ~20 ICLR 2024 and ICLR 2025 papers: 5 strong accepts, 5 weak accepts, 5 weak rejects, 5 strong rejects. For each, include a 2-sentence summary + the score the agent should assign it. Place these as in-context examples in the system prompt. At verdict time, the agent explicitly maps the target paper to the closest anchor.

**Evidence.** Few-shot anchor prompting is the most robust calibration technique in the LLM literature. Compensates for the fact that individual LLM scores drift without reference points.

**Koala-fit.** Cheap to implement, large win. But: **information hygiene risk**. If any anchor paper is cited in or referenced by a competition paper, or if the anchor paper is itself in the competition pool, you're in violation of the "no leaked future information" rule. Keep anchors from 2024 and earlier only; avoid anchor papers on rapidly-evolving subfields.

**Cost/risk.** Static; doesn't adapt mid-window. Token cost adds ~1–2K to the system prompt (manageable with prompt caching).

### I. Consensus-aware verdict (strategic deviation)

**Principle.** Ranking on Spearman correlation rewards not matching the mean but discriminating correctly. If you model the distribution of other agents' likely scores, you can strategically deviate where you have conviction.

**Mechanism.** At verdict time: for each paper, read all comments + all early-submitted verdicts (your own, since those are private to you). Estimate the likely mean verdict from the sentiment of the comment pool. If your analysis gives a significantly different score (≥1.5 points), commit to the deviation; else return a score close to the estimated mean.

**Evidence.** Spearman rewards monotonic ordering — not mean-accuracy. Two distributions with equal L2 but different ordering have very different Spearman. Conviction plays on a few papers where you're right can swing your rank more than broad average correctness.

**Koala-fit.** Subtle but powerful. Doesn't require more compute — just a different scoring rule. **Cautions:** the anti-behavior list includes "revising a stance only to match emerging consensus" — the inverse (deviation without basis) could arguably be flagged too. Don't deviate without in-comment-body justification.

**Cost/risk.** Requires discipline: the rule needs to enforce "deviate only when justified," not "deviate for the sake of deviation." Easy to backfire.

### J. Temporal-arbitrage early-mover

**Principle.** Threads started early accumulate ancestor status for all descendants. Given the 3-karma-per-paper cap, getting cited by a popular paper's verdicts early means your karma caps out fast — but that's still +2 net per paper. Scale this up to dozens of papers = meaningful karma inflow before hour 72.

**Mechanism.** In the first 24 hours of the window, aggressively first-move on papers in a specific, narrow domain (e.g., "RL benchmarks" or "LLM safety evaluations"). Write substantive thread-starter comments. Accept that some of these papers will get few verdicts (wasted karma); the ones that do get verdicted will cap out at 3 karma.

**Evidence.** Ancestor-chain karma rule from Koala `skill.md` + the observation that first-to-the-thread comments have the highest citation probability. The 3-karma-per-paper cap makes breadth more important than depth of citations.

**Koala-fit.** Direct karma strategy. Pairs well with any analytical approach (A–G) — the early-mover agent uses whatever analysis it has to first-move on its domain.

**Cost/risk.** Requires confident domain selection up-front. Less-discussed papers waste karma. If your domain is saturated by other competitors, the citations get diluted.

### K. Domain-specialist committee (sub-venue-aware routing)

**Principle.** A generic LLM reviewer applies the same rubric to an RL paper, a learning-theory paper, and a healthcare application paper. But **each ICML subfield has its own quality bar inherited from its dedicated venue** (CoRL/ICRA for robotics RL; COLT/ALT for theory; MICCAI for medical; etc.). An agent that applies the **right subfield venue's** norms to each paper outperforms a generic reviewer on that subfield — and ICML acceptance tracks those subfield norms more than ICML's own generic rubric alone.

**Mechanism.** On paper intake, classify the ICML subject area (use Koala's `domains` field as primary, add LLM-classifier fallback). Load a **venue-aware sub-prompt** that injects the dominant subfield venue's reviewer norms. The agent scores on both (a) ICML's 4-dim rubric and (b) the subfield venue's emphasis, then synthesizes.

**Concrete sub-prompt seeds per subfield:**

| ICML subject area | Sub-venue to simulate | What that venue emphasizes |
|---|---|---|
| **RL + robotics applications** | CoRL, RSS, ICRA, RLC | Real-robot validation or physics-accurate sim; sample efficiency; reward-hacking disclosure; safety constraints; hardware-in-the-loop evidence; real-time feasibility |
| **ML theory / bandits / learning theory** | COLT, ALT, STOC (ML track) | Error-free proofs in main text *and* appendix; tight constants; explicit assumptions; prior-work theorem comparison; minimax optimality arguments |
| **Deep learning — generative models** | NeurIPS DL track, ICLR | FID/IS/CLIP-scores on standard benchmarks; diversity-vs-fidelity tradeoff analysis; mode-collapse checks; samples at multiple seeds |
| **Deep learning — architectures** | NeurIPS, ICLR | Parameter-count/FLOPs-matched baselines; scaling behavior; ablations over every claimed component; test on held-out distributions |
| **Evaluation / meta-studies / replicability** | MLRC, NeurIPS Datasets & Benchmarks | Statistical significance with many seeds; reporting of confidence intervals; pre-registration of claims; detailed negative results |
| **ML systems** | MLSys, OSDI | End-to-end measurements (not just microbenchmarks); realistic workloads; comparison against strongest open-source baseline; artifact evaluation badge equivalent |
| **Optimization** | NeurIPS optimization, SIAM Opt | Convergence-rate proofs with explicit constants; matching lower bounds; comparison on diverse problem classes (convex + non-convex); reproducible convergence curves |
| **Probabilistic methods** | UAI, AISTATS | Posterior-calibration diagnostics; ELBO/KL decomposition; comparisons against HMC/NUTS where tractable; uncertainty quantification |
| **Trustworthy ML — fairness/interp/safety** | FAccT, AIES, SaTML | Explicit harm models; stakeholder impact analysis; auditable metrics; adversarial robustness baselines; reproducibility of societal claims |
| **Application-driven (healthcare)** | MICCAI, NEJM-AI | Clinically-meaningful metrics (AUROC + calibration); out-of-distribution site testing; expert clinician evaluation; IRB / dataset-access disclosure |
| **Application-driven (physical sciences)** | Domain journal (Physical Review, etc.) | Physically-interpretable model; energy/conservation law compliance; comparison to domain-standard methods (DFT, finite-element, etc.); held-out system tests |
| **Application-driven (climate/sustainability)** | ICML Climate Change AI workshop, NeurIPS CCAI | Real-world impact measurement; deployment feasibility; comparison vs. domain baselines; consideration of downstream carbon cost |

**Paper-type triggers that flip the rubric:**
- **Theoretical claim** (contains theorems) → COLT-rigor mode: check every proof, flag hand-waving in appendix, demand tight constants and matching lower bounds.
- **Empirical benchmark paper** → MLRC/D&B mode: demand many seeds, statistical significance, CIs.
- **Real-robot paper** (contains hardware description) → CoRL/ICRA mode: demand real-world video evidence, sim-to-real gap analysis, failure modes.
- **Application paper** → domain-journal mode: demand domain-expert plausibility, comparison to domain-standard baselines.
- **Dataset release** → D&B mode: demand license, demographic coverage, collection ethics, comparison to existing datasets.

**Evidence.** "Agent Reviewers: Domain-specific Multimodal Agents with Shared Memory" (ICML 2025 poster) — shared-memory specialists improve review quality. ReviewerToo's persona-diverse approach matched human accuracy when personas were heterogeneous. CoRL/ICRA papers in ICML are historically under-reviewed by pure-ML reviewers who miss sim-to-real or hardware concerns (anecdotal from ICML area-chair reports but consistent across years).

**Koala-fit.** The single biggest uncaptured variance on ICML's accept/reject signal is probably **domain-mismatched reviewing**. An agent that reviews an RL+robotics paper with CoRL norms, or a theory paper with COLT norms, will correlate significantly better on those subsets than a generic reviewer. Especially powerful because **most competitor agents will apply a generic ML rubric** — domain specialization is differentiated signal.

**Cost/risk.**
- **Long system prompt** — each sub-venue's rubric adds ~500–1500 tokens. Solution: load the relevant sub-rubric dynamically *inside the agent* using paper classification, or include all of them and let the LLM route. Prompt caching makes full inclusion cheap after the first call.
- **Domain misclassification** — a paper tagged as "general ML" might actually be a robotics paper. Mitigation: use multiple classification signals (Koala `domains`, title/abstract keywords, GitHub repo contents).
- **Cross-subfield papers** — a paper applying theory to RL straddles COLT and RLC norms. The agent needs to apply both.
- **Sub-rubric quality** — you're only as good as the sub-prompts you write. Invest most effort on the subfields you expect to see most heavily in ICML 2026 submissions: Deep Learning, RL, Theory, Trustworthy ML (historically ~60% of ICML accepts).

### L. Self-consistency verdict (variance reduction)

**Principle.** Sample the verdict K times (K=3 or 5) with non-zero temperature, take the median. Reduces LLM sampling variance, which is a known noise source in peer-review-style tasks.

**Mechanism.** At verdict time, run the full verdict-generation prompt K times with temp=0.7. Parse score from each. Take median. Use the most frequently cited comments as the citation set.

**Evidence.** Self-consistency (Wang et al. 2023 onward) gives 3–15% gains on reasoning benchmarks. The gain is higher on ambiguous/borderline inputs, which matches the "verdict on borderline papers" case.

**Koala-fit.** Works on top of any other approach. Trivial to add.

**Cost/risk.** K× token cost. On a flagship with Opus, this is expensive — probably do K=3 on Opus or K=5 on Sonnet. Skip on Volume agent.

### N. Decision-maker-aligned calibration (PC/AC persona overlay)

**Principle.** ICML accept/reject is not a uniform function of paper quality — it's a **collective decision made by specific humans**: Program Chairs (PCs) set the overall acceptance tone, Senior Area Chairs (SACs) supervise clusters of Area Chairs (ACs), and ACs make the meta-review call per paper. Each has a known reviewing style visible from public publications, prior OpenReview history, and research-group pages. An agent calibrated to the **style cluster most likely to review the paper** correlates better with that paper's actual outcome than a generic ICML reviewer.

**Mechanism (three layers).**

1. **PC-level tone (global overlay on all agents).** The 2026 PCs set what "ICML material" means this year. For 2026 the PC team is:

   - **Tong Zhang** (UIUC, General Chair) — statistical learning theory, RL, large-scale ML
   - **Alekh Agarwal** (Google) — RL, bandits, interactive learning, numerical optimization
   - **Miroslav Dudik** (Microsoft Research) — theory + applied ML, algorithmic fairness, RL
   - **Sharon Li** (UW-Madison) — OOD detection, uncertainty quantification, trustworthy/reliable LLMs, hallucination detection
   - **Martin Jaggi** (EPFL) — distributed optimization, federated learning, efficient training

   What this tells you about ICML 2026's acceptance tone:
   - **Strong theory/RL/optimization bias.** Papers with rigorous theoretical foundations or RL contributions will land well with this PC team.
   - **Reliability and trustworthiness are first-class.** Safety, OOD, uncertainty, fairness, hallucination — any paper in these areas maps to Sharon Li's or Miroslav Dudik's direct expertise.
   - **Systems/scale/efficiency matter.** Martin Jaggi's influence suggests ML-systems and efficient-training papers get fair shake.
   - **Less-obvious: slight deprioritization of pure applications.** No strong applications-ML chair on the PC team. Application papers will be judged harder on the core-ML novelty axis rather than domain impact.
   
   Translate this into per-agent system-prompt text: "ICML 2026's PC team weights rigorous theory, RL, trustworthy/reliable ML, and efficient/distributed training more than pure applications. Weight Originality and Soundness dimensions accordingly."

2. **AC-cluster personas (per domain specialist).** Each ICML subject area is covered by ~10–30 ACs. You don't know which AC reviews a given paper — but you know the **cluster of AC styles** that covers the subfield. For each domain cluster, build a ~500-token "composite persona" distilled from:
   
   - Public AC lists when ICML 2026 announces them (currently in progress — monitor `icml.cc/Conferences/2026/ProgramCommittee` for updates)
   - For subfields where the AC list isn't public, use historical ICML 2024/2025 AC rosters as a proxy (highly correlated across years)
   - Representative recent papers from those ACs and their research groups
   - Their past reviewing history from other venues (OpenReview public history, where available)
   
   Composite persona example (RL/Robotics cluster):
   
   > The RL/Robotics AC cluster for ICML 2026 includes researchers who publish in CoRL, RSS, ICRA, RLC. They emphasize (a) real-robot validation or physics-accurate sim, (b) sim-to-real gap disclosure, (c) sample efficiency over absolute performance, (d) reward-hacking disclosure. This cluster has historically been skeptical of: sim-only results without transfer discussion, cherry-picked seeds, benchmark-only papers without real-world grounding. They accept: modest numerical gains with careful real-robot demos, theoretical advances with empirical backing, safety-focused advances.

3. **Individual-chair tiebreakers (optional, low-weight).** For borderline papers in narrow subfields where one or two SACs dominate decisions, add specific-person rubric hints. Example: a theoretical-RL paper likely has Alekh Agarwal or a close collaborator in the decision chain; his published work emphasizes sample-complexity lower bounds, PAC-Bayesian analysis, and interactive-learning regret. Calibrate Originality and Soundness scoring to those priorities for borderline theory-RL papers.

**Evidence.** No published benchmarks on PC/AC-aligned calibration specifically (the idea isn't standard in the literature). Mechanistically it follows from: (a) ICML decisions are collective human judgements made by specific chairs, (b) those chairs' preferences are visible in their public record, (c) current LLM reviewers ignore this signal entirely.

**Koala-fit.** Uses only public information (published papers, public reviewer histories, published AC rosters where available). Zero risk of "leaked future information about the exact same paper" (that rule concerns post-publication commentary about the submission being reviewed, not the public profile of the chair who may review it). The persona overlay composes cleanly with Approach K — each domain specialist loads the matching AC-cluster persona on top of the sub-venue rubric.

**Cost/risk.**
- **Staleness.** AC/SAC reviewing styles evolve. Use last-2-year review history preferentially.
- **Cluster-over-individual.** You don't know which specific AC reviews a paper. Mimic the cluster, not a specific human. Never impersonate a specific chair in public-facing comment text — a comment body saying "as Prof. X, I would …" is reputationally and operationally unwise. Internal calibration to a style *cluster* is fine.
- **Pre-competition prep.** Requires 2–6 hours of reconnaissance before kickoff to distill the PC-tone overlay and the AC-cluster personas. If you invest this once, the edge lasts the whole window.
- **Tiebreaker only for borderline cases.** Don't let PC/AC persona override the ICML 4-dim rubric for clearly strong or weak papers. Use it to tiebreak borderline decisions.

### M. Learn-during-window (online calibration)

**Principle.** Once the first wave of papers enters `reviewed` status (hour ~72), their verdicts are public. Compare your early verdicts to the consensus. Update your calibration for the second half.

**Mechanism.** At hours 72+, pull all `reviewed` papers where you verdicted. Compute your score – consensus score diff. If systematically off by ≥0.5, adjust your scoring rule (e.g., add the bias to subsequent verdicts).

**Evidence.** Online calibration is a standard trick in production forecasting (weather, election models). Not widely tested in LLM review literature, but mechanistically sound.

**Koala-fit.** Useful in the tail (hours 72–144) when new papers still release and karma flows. For the first 72h you have no feedback signal, so this approach only applies to the second half.

**Cost/risk.** Requires a stateful agent (or you inject the consensus stats into the system prompt on each launch). `claude-code` and `codex` both support session resume; gemini-cli does not.

---

## Three portfolio recommendations

The constraints that shape portfolio design:

1. **Sibling agents cannot cite each other's comments in verdicts** → force maximum specialization.
2. **3-karma-per-paper cap on earnings** → breadth matters more than depth of earning per paper.
3. **Each agent's verdict correlation is scored independently for the leaderboard** → optimize per-agent, not portfolio-aggregate.
4. **You can only run 3 agents** → one role per agent, not overlapping.

### Portfolio 1 — Specialist trio (recommended default)

Rationale: each agent attacks a different published weakness. Zero overlap. Each agent's verdict signal is independent, so if any one overperforms the others, the best score ranks you.

| Agent | Approaches | Backend | Compute tier |
|---|---|---|---|
| **Reproducer** (flagship) | C + L + domain-aware comments | `claude-code` on Opus/Sonnet API | Premium |
| **Novelty Auditor** | B + H + A (7-dim on non-novelty axes) | `codex` on GPT-5 API | Medium |
| **Calibrated Meta-reviewer** | E + A + D internal debate | `claude-code` on Sonnet API or Max | Medium-cheap |

Expected strengths: Reproducer has a signal no other agent has (code-grounding), targets the big "soundness/reproducibility" reviewer weakness. Novelty Auditor targets the documented LLM blindspot. Meta-reviewer leverages the citation requirement organically, scales with discussion volume.

Expected rank: Reproducer in the top decile if GPU access and repo-cloning work. Novelty Auditor in the top quintile. Meta-reviewer mid-pack, scales with competitor activity.

### Portfolio 2 — Calibration-maximalist

Rationale: if you believe the 0.42 Spearman ceiling is real and hard to beat, triple down on calibration diversity. Three agents running Approach A with different regression fits, anchor sets, and personas.

| Agent | Approaches | Backend |
|---|---|---|
| **Classical Calibrator** | A + H + L | `claude-code` Sonnet |
| **Debate Calibrator** | A + D + L | `codex` GPT-5 |
| **Adversarial Calibrator** | A + F + H | `gemini-cli` Gemini 2.5 Pro |

Expected strengths: low variance, robust. All three agents likely cluster near the 0.42 ceiling. Low engineering risk.

Expected rank: median across all three. Unlikely to produce a top-3 finisher — the whole design avoids differentiated signals. Good if you want consistency over upside.

### Portfolio 3 — Pipeline-as-agent

Rationale: treat the 7-dim signal-ensemble (Approach G) as the portfolio. Each agent implements a subset of signals, and their verdicts are independent views of the same underlying pipeline.

| Agent | Approaches | Focus |
|---|---|---|
| **Code & Soundness** | G (repro+soundness sub-pipelines) + C | Experiments-grounded reject-or-accept |
| **Novelty & Contribution** | G (novelty+contribution sub-pipelines) + B + H | Retrieval-heavy, impact-focused |
| **Clarity & Synthesis** | G (clarity sub-pipeline) + E | Meta-review emphasizing readability |

Expected strengths: highest engineering investment, highest potential ceiling. If the pipeline is well-calibrated and the signals are truly orthogonal, you could exceed 0.5 Spearman per agent.

Expected rank: highest variance. Either a top-3 finish or crashes if any sub-pipeline is miscalibrated.

### Portfolio 4 — Domain-specialist trio with PC/AC alignment (strongly recommended)

Rationale: each agent owns a cluster of adjacent ICML subject areas, applies the dominant sub-venue's rubric, **and** overlays the relevant ICML 2026 PC/AC-cluster persona. No agent tries to be a generalist. Each agent is effectively "the best reviewer ICML could have assigned for papers in my cluster — calibrated to the specific people who will decide ICML 2026."

| Agent | Domain cluster | Sub-venue rubrics loaded | PC/AC overlay | Approaches | Backend |
|---|---|---|---|---|---|
| **RL/Robotics/Systems Specialist** | RL + robotics apps + ML systems + optimization | CoRL, RSS, ICRA, RLC, MLSys | Alekh Agarwal (RL theory), Martin Jaggi (distributed/optimization), Tong Zhang (RL) — high weight on sample-complexity bounds, real-robot validation, distributed efficiency | K + C + A + L + **N** | `claude-code` on Opus/Sonnet API |
| **Theory/Probabilistic Specialist** | ML theory + probabilistic methods + optimization (theoretical side) | COLT, ALT, UAI, AISTATS | Miroslav Dudik (theory+fairness), Alekh Agarwal (learning theory), Tong Zhang (statistical learning) — high weight on tight constants, matching lower bounds, PAC-Bayes rigor | K + B + A + F + **N** | `codex` on GPT-5 API |
| **Applications/Trustworthy Specialist** | Application-driven ML + Trustworthy ML + Evaluation / meta-studies | MICCAI, FAccT, MLRC, NEJM-AI, domain journals | Sharon Li (OOD/uncertainty/reliable-LLM), Miroslav Dudik (fairness) — high weight on reliability, OOD robustness, hallucination detection, auditable fairness metrics | K + E + A + H + **N** | `claude-code` on Sonnet or Max |

**Global PC-tone overlay** (applies to all three agents, added to shared `GLOBAL_RULES.md` contribution):

> The ICML 2026 Program Chairs are Tong Zhang, Alekh Agarwal, Miroslav Dudik, Sharon Li, Martin Jaggi. Their combined research emphasis favors: rigorous theory (especially RL/bandits/learning theory), optimization and efficient/distributed training, trustworthy ML (OOD, uncertainty, fairness), and reliable-agent LLM systems. Papers in these areas will be judged against their high standards; papers in under-represented areas (pure applications without strong methodological contribution) face a higher bar. Weight Originality and Soundness accordingly.

**Why this is likely the winning portfolio:**

1. **Exploits the "ICML-is-not-ICML" effect.** ICML accepts papers across 10+ subject areas; each has its own norms. A generic reviewer is suboptimal on every subfield simultaneously. Your specialists dominate their subfield's correlation signal.

2. **Differentiated from competitor agents.** Most competitors will build generic reviewers (single rubric, all papers). Your agents are the only ones applying sub-venue norms — this is an **uncopiable** edge for 72 hours.

3. **Natural load-balancing.** ICML 2026 papers split roughly: Deep Learning + Architectures ~35%, RL ~10%, Theory ~10%, Trustworthy ~15%, Applications ~20%, others ~10%. Three specialists split work naturally by domain rather than competing for the same papers.

4. **Each agent accumulates deep expertise within its cluster** — repeated application of COLT norms across theory papers within 72 hours lets the agent's caching and retrieval cache build up focused domain knowledge.

5. **Composable with other approaches.** Each specialist is a Committee agent (K) at the top of its stack, but composes with Code-grounding (C) for the RL/Systems agent, Novelty (B) and Adversarial (F) for the Theory agent, Historical-anchors (H) for the Applications agent.

**Expected strengths:** highest per-agent ceiling on the subfields you specialize in. If the specialists work, you plausibly exceed 0.50 Spearman on their subsets.

**Expected risk:** you *underperform* on papers that don't fit cleanly into any cluster (interdisciplinary submissions) or that your domain classification misroutes. Mitigation: have each agent fall back to pure ICML-rubric mode (Approach A) when paper classification confidence is low.

---

## My recommendation

**Portfolio 4 (Domain-specialist trio), with Portfolio 1 as the backup.** Reasoning:

- The **biggest unexploited gap** in the LLM-review literature is not a single blind spot — it's that every paper gets the same rubric. Domain specialization is the one mechanism that directly maps to ICML's own heterogeneous quality bars.
- **Code-grounding (C)** still belongs, but attached to the RL/Systems specialist where it fits naturally (most RL papers have code, most theory papers don't). Don't build it as a standalone flagship — it's a sub-capability of the RL/Systems agent.
- **Novelty (B)** also still belongs, attached to the Theory specialist (theoretical novelty is tractable via prior-work retrieval) and the Applications specialist (cross-domain novelty is a common rejection reason).
- Portfolio 1 (Specialist trio by approach) is the fallback if domain classification turns out to be unreliable — it's still strong.
- Portfolio 2 is safe but gives up upside. Portfolio 3 is high-variance and out of time-budget scope.

### If you want a hybrid (even better, harder to build)

Combine the two: each of Portfolio 1's agents *also* loads the ICML sub-venue rubric from Portfolio 4 based on paper domain. I.e. the Reproducer agent still runs code on every paper, but when the paper is a theory paper with no code, it switches to COLT-rigor proof-checking mode. This is strictly better but harder to prompt-engineer correctly in 72 hours. If you have time after Portfolio 4 is working, upgrade to this.

The 72-hour competition window is enough for Portfolio 4 if you invest Day 0 (today, before kickoff) in writing 3 sub-venue rubrics per agent (9 total). Each rubric is 500–1000 tokens of "what CoRL reviewers emphasize" — mostly boilerplate from the public venue CFPs.

---

## Cross-cutting techniques to add to all 3 agents

Independent of approach, these compose universally:

- **Prompt caching** on the shared `GLOBAL_RULES.md` + `platform_skills.md` sections (Anthropic prompt caching drops static-prompt cost ~10×).
- **Hidden-confidence aggregation** if any multi-pass scoring is used (Du et al. finding).
- **Historical anchors** (Approach H) with 2024-or-earlier papers only (information hygiene).
- **60 comments/min rate limit** — pace agents accordingly; don't burst.
- **`karma_spent` / `karma_remaining`** parsed from `POST /comments/` responses — no balance polling needed.
- **`pdf_url` + `tarball_url` + `github_urls[]`** all used — LaTeX source is richer than PDF for novelty and method extraction; `github_urls` may contain model/data repos beyond just code.
- **Moderation-avoidance wording** for papers in sensitive domains (red-team, safety evals, dual-use) — reject false positives kill karma.

---

## Open research questions (post-competition)

- Does the 3-karma-per-paper cap + sibling exclusion make traditional multi-agent coordination strategies useless? (Likely yes, which is why Portfolio 1 emphasizes independent specialists rather than an ensemble.)
- Can a trained reward model (fit on publicly-released ICLR 2024+2025 decisions) meaningfully beat a linear regression over 7 dimensions? (agentic-paper-review claims 0.74 — worth investigating post-window.)
- How does verdict submission timing within the 24h `deliberating` window affect the downstream karma flywheel?

---

## Sources

### ICML 2026 authoritative
- **ICML 2026 Reviewer Instructions** — 4-dim rubric (Soundness/Presentation/Significance/Originality, 4-point each) + 6-point recommendation. <https://icml.cc/Conferences/2026/ReviewerInstructions>
- **ICML 2026 Call for Papers** — 10 subject areas. <https://icml.cc/Conferences/2026/CallForPapers>
- **ICML 2026 LLM Policy** — two-policy framework for reviewers (informational context for competition agents). <https://icml.cc/Conferences/2026/LLM-Policy>
- **ICML 2026 Peer Review Ethics** — confidentiality norms. <https://icml.cc/Conferences/2026/PeerReviewEthics>

### LLM peer-review literature
- **Stanford Agentic Reviewer (paperreview.ai)** — Tech overview, 7-dim + linear regression, 0.42 Spearman / 0.75 AUC on ICLR 2025. <https://paperreview.ai/tech-overview>
- **DeepReviewer (ACL 2025)** — DeepReview-13K, 0.40 Spearman, multi-stage reasoning. <https://arxiv.org/abs/2503.08569>
- **ReviewerToo (arXiv 2510.08867)** — Persona-diverse reviewers match human accuracy; sycophancy risk.
- **Mind the Blind Spots (EMNLP 2025)** — Facet-level evaluation, novelty blindspot. <https://arxiv.org/abs/2502.17086>
- **Agent Reviewers: Domain-specific Multimodal Agents** (ICML 2025 poster) — shared memory across domain specialists.
- **What Drives Paper Acceptance** — Process analysis of peer review. <https://arxiv.org/abs/2509.25701>
- **OpenReviewer** — Predicting conference decisions with LLMs. <https://openreview.net/forum?id=d4mJdezdHO>
- **ICLR 2025 Feedback RCT** — 20K-review randomized study. <https://arxiv.org/abs/2504.09737>
- **agentic-paper-review (GitHub)** — claims 0.74 Spearman on 46K ICLR reviews; unverified. <https://github.com/debashis1983/agentic-paper-review>

### Multi-agent and calibration
- **Multi-agent debate** — Du et al. 2023 (arXiv:2305.14325); 2025 follow-ups: diversity + hidden confidence > debate structure. <https://composable-models.github.io/llm_debate/>
- **Self-consistency** — Wang et al. 2023 (median-of-K variance reduction).

### Sub-venue reviewer norms (for Approach K sub-prompts)
- **CoRL / RSS / ICRA** — Information for Reviewers, IEEE Robotics and Automation Society. <http://www.ieee-ras.org/conferences-workshops/fully-sponsored/icra/information-for-reviewers>
- **RLC 2026 Call for Papers** — methodological rigor for RL. <https://rl-conference.cc/callforpapers.html>
- **COLT 2026 Call for Papers** — proof rigor and technical details required in main text. <https://learningtheory.org/colt2026/cfp.html>
- **NeurIPS Reviewer Guidelines** — soundness/presentation/contribution axes. <https://neurips.cc/Conferences/2022/ReviewerGuidelines>
- **ML Code Completeness Checklist** — NeurIPS 2020 reproducibility spec.
- **HRI 2026 Reviewer Guidelines** — human-robot interaction domain-specific norms.

### Platform
- **Koala skill.md** — authoritative platform rules. <https://koala.science/skill.md>
