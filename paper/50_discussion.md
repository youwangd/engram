# 5. Discussion

<!-- Industry Track triage 2026-05-27 (Phase 4): §5.6 RM3 result
     compressed to one paragraph + pointer; §5.7 deployment-pp
     anchors and §5.8 power disclosure folded (power moved to §75
     Limitations); §5.9 deployment cost corollaries merged into
     §5.1 since the §3.1.1 latency-cost table already says the same
     thing in less space. §5.2-§5.5 (adaptive-vw null, schema
     lifecycle as artifact, honest consolidation, PRF latency myth)
     remain in paper/A4_extended_discussion.md from Phase 1. -->

## 5.1 When does dense embedding pay?

The two-axis result suggests an operational rule:

> **Closed-vocabulary lookups ("which service / tool does X use?")
> let a 256-dim hash trigram at deep collision recover ~50% of
> dense-embedder lift at zero model-load cost. Open-vocabulary
> intent-style queries ("what does X prefer?", "what is X working
> on?") require dense.**

The intent-tag side is structural rather than incidental: a paired
RM3 \citep{lavrenko2001rm} baseline with Anserini-default
hyperparameters returns the *same* wrong session as BM25 on all 30
LongMemEval-S `single-session-preference` instances (Δhit@1 =
+0.000 exactly), and SIG-regresses `single-session-user` by
−7.1 pp [−14.3, −1.4] via expansion-driven query drift. No PRF
expansion over the lexical channel substitutes for a dense encoder
on intent-style queries; full RM3 panel and corpus-dependent
recall-broadening behaviour in §A.4.16.4. **Embedder selection is
a per-tag deployment decision keyed on the discriminator class of
expected queries.**

The §3.1.1 cost table makes the deployment trade-off explicit:
HashTrigram is essentially free at write time; MiniLM-384 is the
v0.2 default at ~17–21 ms/inst on commodity CPU; BGE-large-1024
is only defensible on accelerator hardware (~720× the per-instance
write budget of MiniLM on CPU, ~7× on MPS). A batched ingest path
deferred to v0.3 (~12 ms/doc projected at bs=32 fp16, ~3× over the
30.6 ms/doc measured on NQ) is required for HotpotQA-scale corpora;
the current path serves FiQA (37 min) and NQ (22.8 h) cleanly
(§4.6, §A.4.16.5). Measuring the bottleneck before publishing is
the engineering corollary of the protocol's measurement-first
stance. The deployment lesson is that **a 2.7× parameter swap
does not uniformly improve retrieval**: BGE-large-1024 wins on
intent-style queries but loses 2.7–11.7 pp on lexical ones, so
embedder size is not the binding constraint a procurement decision
should optimize.

Companion analyses (adaptive-vw null §A4.1; schema lifecycle as
governance §A4.2; consolidation-lift restatement §A4.3; PRF latency
falsification §A4.4) live in the extended-discussion appendix.
