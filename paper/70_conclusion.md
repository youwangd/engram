# 7. Conclusion

We presented **entity-collision**, a system-agnostic protocol for
attributing retrieval lift in agent memory. The protocol pins the
BM25 lexical floor by construction — every distractor shares the
answer's entity tokens — and stratifies queries by discriminator
tag so per-tag patterns are not absorbed into a single hit@k
average. The protocol applies to any retriever exposing a
per-document score; we instantiated it on one open-source agent-
memory testbed as a worked example, but the methodology, query
generators, and CI tooling (`evals/entity_collision_*`) are not
testbed-specific.

The headline finding is a **two-axis result** that survives an
encoder-capacity falsification. Lexical-discriminator queries
(closed-vocabulary `service`/`tool`): a 256-dim hash trigram
recovers a real but small fraction of dense-embedder lift, only
at deep collision. Intent-style queries (`preference`, `project`,
`technical`): hash trigrams are n.s. or negative; only a dense
encoder delivers CI-positive lift. **Encoder capacity is not the
binding constraint** — a 2.7×-parameter BGE-large-1024 wins on
intent-style `project` (+8 to +14 pp BGE−MiniLM, CI-positive at
K∈{2,4,8,16}) but loses on lexical `tool`/`technical` (−2.7 to
−11.7 pp, CI-significant). The synthetic two-axis pattern carries
external validity: the intent-tag null replicates on LongMemEval
(n=500) as a single-session-preference recall cliff.

The operational corollary is decision-shaped: **closed-vocabulary
memory queries can ride a hash-trigram embedder at deep collision
for ~50% of dense-embedder lift at zero model-load cost; open-
vocabulary intent-style queries require dense.** This rule is
derived from per-tag stratification, not from a global hit@k
average — the methodological point the protocol enables. Code,
raw benchmark JSON (26 tables), figure scripts, and a single-
entry-point reproduction harness are released with the paper.
