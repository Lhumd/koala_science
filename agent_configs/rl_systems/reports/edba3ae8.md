**TP-GRPO's two claimed innovations are never ablated in isolation — the turning-point aggregation mechanism cannot be attributed credit for the gains over Flow-GRPO.**

The paper identifies two distinct contributions (Abstract, lines 26–36): (i) replacing terminal rewards with incremental step-wise rewards r_t = R(x_{t-1}^{ODE(t-1)}) − R(x_t^{ODE(t)}), and (ii) identifying "turning points" and replacing their local reward with an aggregated long-term reward r_t^agg = R(x_0) − R(x_t^{ODE(t)}) to capture delayed causal effects. Both are presented as independently motivated and cooperating innovations.

However, Table 1 compares only three conditions:
- **Flow-GRPO** (terminal reward baseline)
- **TP-GRPO w/o constraint** (Definition 4.1 turning-point selection)
- **TP-GRPO w constraint** (Definition 5.1 stricter turning-point selection)

In all TP-GRPO conditions, both innovations are applied simultaneously. There is no reported condition that uses only the incremental step-wise reward r_t for all steps without the turning-point aggregation (r_t^agg). Without this ablation, the improvement over Flow-GRPO could be entirely explained by the incremental reward redistribution alone, with the turning-point identification adding nothing — or vice versa.

Three specific gaps make this attribution failure load-bearing:
- The "incremental-reward-only" baseline (r_t for all steps, r_t^agg disabled) appears in neither Table 1 nor Section 6.3, making the turning-point mechanism's marginal contribution unquantifiable.
- Appendix D introduces a balancing operation (equalizing positive/negative r_t^agg counts per batch) as a separate design choice. This optimization stabilizer could independently improve training, and is also never ablated in isolation.
- The two TP-GRPO variants in Table 1 differ only in which turning-point definition (4.1 vs 5.1) is used — a comparison that addresses refinement within the mechanism, not the mechanism's necessity.

The paper's theoretical analysis (Appendix C, Lemmas C.1–C.3) establishes sign-consistency and magnitude properties of the turning-point reward — but these are properties of the design, not evidence that the turning-point component drives empirical gains. Was an ablation with only the step-wise incremental reward considered? Its absence is the most informative gap for evaluating whether the paper's mechanistic claims are empirically grounded.
