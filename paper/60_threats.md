# 6. Threats to Validity

<!-- Industry Track triage 2026-05-27 (Phase 4): §6.6 (train-test
     contamination) and §6.8 (intent-tag paraphrase replication)
     folded into §75 Limitations. §6.1 retained as the load-bearing
     paraphrase-robustness threat — it directly defends the two-axis
     claim. Extended threats (§A5.1-§A5.5: hash-dim ablation,
     hit@1-only metric, single-process SQLite, single-machine OS,
     author-as-annotator) live in paper/A5_extended_threats.md. -->

## 6.1 Synthetic corpus

The protocol generates synthetic memories from a fixed sentence
template; real conversational memories are noisier and more
paraphrased. To check whether the headline two-axis claim survives
memory-side paraphrase, we re-ran the strongest lexical cell
(`tool`, n=32, K∈{1,2,4,8,16}) with paired 95% CIs against ≥4
paraphrased templates per fact. The hash lift collapses to CI-null
at K∈{8,16} once templates vary (K=16: +0.023 [−0.006, +0.053],
n.s.); ST retains all four cells CI-strictly above zero, with
K=16 lift *growing* from +0.043 (fixed) to **+0.096 [+0.070, +0.121]**
(paraphrased). Memory-side paraphrase strengthens the two-axis
claim: semantic embedders are paraphrase-robust, hash-trigram
retrievers are template-bound. Replications on `service`,
`preference`, and `project` confirm the pattern (within-lexical
`service` retains **+0.037 [+0.012, +0.062]** at K=16; intent-tag
hash null and MiniLM lift both survive paraphrase, point estimates
within ±0.02 pp of fixed-template). Full per-tag tables in §A5.0.

The supporting threat analyses — single embedder per family with a
hash-dim ablation (§A5.1), hit@1-only metric (§A5.2), single-
process SQLite (§A5.3), single-machine/single-OS (§A5.4), and
author-as-annotator on tag definitions (§A5.5) — live in the
extended-threats appendix. Embedder train-test contamination and
the related leakage-audit gap are stated under §75 Limitations.
