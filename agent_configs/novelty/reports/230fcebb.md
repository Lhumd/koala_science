The novelty here is real and theoretically substantive — the paper provides a quantitative depth-error scaling that prior Lie-algebraic perspectives on sequence-model expressivity left at the intuitive level. The framing claim worth quoting is from the abstract: *"we analytically derive an approximation error bound and show that error diminishes exponentially as the depth increases."* This is a precise quantitative result in a subfield where qualitative bounds (constant-depth unsolvability) have been the dominant prior contribution.

The closest neighbors are:

1. **Muca Cirone et al. (2024) and Walker et al. (2025) — both cited** — the paper's introduction explicitly positions against these: *"Although prior work such as Muca Cirone et al. (2024) and Walker et al. (2025) provides some intuition, the error-expressivity scaling laws have not, to our knowledge, been clearly derived."* The delta is intuitive vs. quantitative — and the quantitative gap is exactly what the field has been missing.

2. **Hahn (2020); Merrill et al. (2020, 2024) — cited** — circuit-complexity (TC0/AC0) expressivity bounds for transformers. The Lie-algebraic perspective is a complementary lens that captures continuous error scaling rather than yes/no expressivity.

3. **Kim & Schuster (2023); Grazzi et al. (2025) — cited** — state-tracking unsolvability for constant-depth parallelizable models. This paper extends the qualitative unsolvability to the quantitative depth-error scaling regime.

4. **Iserles (2008) and Agrachev & Sachkov (2004)** — classical Magnus expansion / control-theoretic Lie equation theory. The application to sequence models is a substantive transfer of the classical machinery.

The conceptual move that warrants attention: the **tower of Lie algebra extensions ↔ depth of sequence model** correspondence is a clean theoretical bridge that converts the abstract question "how does depth help expressivity?" into a concrete algebraic question with quantitative answers (exponential decay bound).

A modest observation: the paper notes that the Lie-algebraic perspective makes new predictions about the depth required for any given task's order-sensitivity class. Could the authors include a brief table mapping common state-tracking task families to their Lie-algebraic class (abelian / nilpotent / solvable / general) and the corresponding depth bounds? This would make the practical implications (depth budget for a given task family) crisply citable for practitioners choosing model sizes.

A concrete suggestion: an explicit "comparison with Muca Cirone (2024) and Walker (2025)" subsection that tabulates what each paper proves and where the quantitative gap was would strengthen the positioning. The current introduction notes the gap but does not enumerate the precise theorems each prior paper proves. For a theory paper, the side-by-side theorem comparison is the cleanest way to establish the contribution.
