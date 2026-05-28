# arXiv Submission Checklist — Engram v0.2

**Status:** ready to upload as of 2026-05-28.
**Tarball:** `paper/dist/engram_v0.2_arxiv.tar.gz` (283 KB)
**Builder:** `python scripts/build_paper_arxiv.py`

## Pre-flight verification

- [x] Endorsement received for `cs.CL`
- [x] Tarball compiles cleanly with TeX Live in Docker (`xelatex → bibtex → xelatex → xelatex`, 47-page PDF, 0 undefined citations)
- [x] PDF metadata correct: `/Author = "Youwang Deng"`, `/Title = "Entity-Collision: ..."`
- [x] Author block on page 1 shows `Youwang Deng · Independent Researcher · dengyouwang@gmail.com`
- [x] GitHub URL on page 1: `https://github.com/youwangd/engram (Apache 2.0 licensed)`
- [x] Bibliography section renders (33 entries, refereed venues primary)

## arXiv form fields (copy-paste ready)

### Title
> Entity-Collision: A Stratified Protocol for Attributing Retrieval Lift in Agent Memory

### Authors
> Youwang Deng (`dengyouwang@gmail.com`)

### Abstract (195 words, 1342 chars — well under 1920-char limit)
> End-to-end agent-memory benchmarks report a single hit@k per retriever, confounding lexical leakage (uncontrolled query/gold/distractor entity overlap) with tag-mixing (preferences, services, tools averaged together). We propose **entity-collision**, a system-agnostic protocol that pins the BM25 floor by construction — every distractor shares the answer's entity tokens — and stratifies queries by discriminator tag, so any lift over BM25 is attributable to the embedder. Applied to an open-source agent-memory testbed across 5 tags × 3 embedders × 5 collision degrees with paired-bootstrap 95% CIs, the protocol reveals a **two-axis pattern**: a 256-d hash trigram helps only on closed-vocabulary lexical tags at deep collision; MiniLM-384 dominates both axes; and a 2.7×-parameter BGE-large does not uniformly improve on MiniLM — it wins on intent-style queries but loses on lexical ones. Encoder capacity alone is not the binding constraint. The synthetic intent-tag null replicates on LongMemEval (n=500) as a single-session-preference recall cliff. Adaptive vector-weight routing on LoCoMo is a measured null: 11.7pp of oracle headroom exists, but no signal we tested recovers it. All 26 result tables and 37 reproduce scripts are version-controlled and verified by a public registry; the protocol is exercised on a **deterministically governed** memory testbed (event-sourced decision log, DAG-state-machine schema lifecycle) so every reported CI is reproducible byte-for-byte from the ingest stream.

> *(arXiv strips markdown — paste as plain prose, drop the `**bold**` markers if the form rejects them.)*

### Categories
- **Primary:** `cs.CL` (Computation and Language) — endorsed
- **Cross-list:** `cs.IR` (Information Retrieval) — protocol targets retrievers
- **Cross-list:** `cs.AI` (Artificial Intelligence) — agent memory framing

### Comments field (optional but recommended)
> 47 pages with appendix; 6-page body, mandatory Limitations, References, and 7 appendices. Code, benchmarks, and 37 reproduce scripts at https://github.com/youwangd/engram (Apache 2.0). Submitted concurrently to EMNLP 2026 Industry Track.

### License selection
- Pick **arXiv perpetual non-exclusive license**. (NOT CC0 / CC-BY — code is Apache 2.0 but paper rights stay with you.)

### MSC / ACM classification
- Skip (rarely useful for cs.CL). Leave blank.

### Journal reference
- Leave blank (not yet published).

## Upload steps

1. Go to https://arxiv.org/submit
2. Authenticate (existing account; endorsement already on file for cs.CL)
3. **Type:** "Article"
4. **Title / Authors / Abstract:** paste from above
5. **Primary category + cross-lists:** `cs.CL`, `cs.IR`, `cs.AI`
6. **Upload:** `paper/dist/engram_v0.2_arxiv.tar.gz`
7. arXiv will run its own pdflatex/xelatex pass. Verify the rendered PDF on the preview page matches `paper/dist/engram_v0.2_arxiv.pdf` byte-equivalent (or close — different TeX Live version may shift hyphenation).
8. Submit. arXiv announces 14:00 ET the next business day.

## Post-submission

- [ ] Update `paper/05_authors_arxiv.md` line 22: replace `arXiv:XXXX.XXXXX` with the assigned ID
- [ ] Update `paper/build/acl/` rebuild to bake the arXiv ID into the GitHub README badge
- [ ] Add arXiv badge to `README.md`:
  ```markdown
  [![arXiv](https://img.shields.io/badge/arXiv-XXXX.XXXXX-b31b1b.svg)](https://arxiv.org/abs/XXXX.XXXXX)
  ```
- [ ] Add citation BibTeX block to `README.md`:
  ```bibtex
  @misc{deng2026entity,
    title={Entity-Collision: A Stratified Protocol for Attributing Retrieval Lift in Agent Memory},
    author={Deng, Youwang},
    year={2026},
    eprint={XXXX.XXXXX},
    archivePrefix={arXiv},
    primaryClass={cs.CL},
    url={https://arxiv.org/abs/XXXX.XXXXX}
  }
  ```

## Known minor issues (not blockers)

- 1 overfull hbox (2.6pt — well under 5pt threshold)
- 166 underfull hbox warnings (badness 10000 — typesetter complaints, no visible artifacts in 6-page body)
- "Missing character ✓" warnings during compile — these are inside ACL build-checker output; harmless, the actual paper text doesn't use the U+2713 glyph

## What this submission is NOT

- This arXiv version is **NOT anonymized**. Author/email/GitHub all visible.
- For the EMNLP softconf upload (separate workstream, due Jun 16), we'll build a different tarball with author redaction and either keep the "Engram" name visible (relying on ACL post-Jan-2024 relaxed preprint rules) or rename to "SystemX" for safety. That's a later decision.
