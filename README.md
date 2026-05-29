# Engram

Source code, benchmarks, and reproduce scripts for:

> **Entity-Collision: A Stratified Protocol for Attributing Retrieval Lift in Agent Memory**
> Youwang Deng. arXiv:2605.29630, 2026.
> [arXiv](https://arxiv.org/abs/2605.29630) · [PDF](https://arxiv.org/pdf/2605.29630) · [`paper/dist/engram_v0.2_arxiv.pdf`](paper/dist/engram_v0.2_arxiv.pdf)

The paper's contribution is the entity-collision evaluation protocol and the two-axis empirical finding it surfaces (§1, §3.2–3.3). Engram is the testbed on which that protocol is exercised, released here for reproducibility.

## Paper artifacts

| File | Description |
|---|---|
| [`paper/dist/engram_v0.2_arxiv.pdf`](paper/dist/engram_v0.2_arxiv.pdf) | arXiv preprint render (Letter, single column) |
| [`paper/dist/engram_v0.2_arxiv.tar.gz`](paper/dist/engram_v0.2_arxiv.tar.gz) | arXiv source tarball (XeLaTeX) |
| [`paper/dist/engram_v0.2_acl.pdf`](paper/dist/engram_v0.2_acl.pdf) | ACL 2-column rendering (review mode, anonymized) |
| [`paper/REPRODUCIBILITY.md`](paper/REPRODUCIBILITY.md) | How to reproduce every reported number |
| [`paper/CITATIONS_VERIFIED.md`](paper/CITATIONS_VERIFIED.md) | Citation verification registry (all 33 entries) |
| [`paper/00_abstract.md`](paper/00_abstract.md) ... [`paper/A7_extended_methods.md`](paper/A7_extended_methods.md) | Markdown sources for body + 7 appendices |

## Reproducing the paper

```bash
git clone https://github.com/youwangd/engram && cd engram
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Sanity check: every artifact and script cited in the paper resolves.
bash scripts/verify_repro_artifacts.sh

# Re-run a representative experiment (entity-collision MiniLM, K=16, n=32, ~3 min on CPU).
python evals/entity_collision_sweep.py \
    --tag service --embedder st_minilm --K 16 --n 32 \
    --out bench/results/repro_check.json
```

The full reproduction guide is in [`paper/REPRODUCIBILITY.md`](paper/REPRODUCIBILITY.md), including:
- Hardware envelope and library pinning
- Dataset acquisition (LongMemEval, LoCoMo, BEIR — not redistributed; download instructions only)
- Full eval script inventory (37 scripts, all referenced in the paper)
- Acceptance gates for diff-results comparisons (±0.5pp, ±25% latency)

## Repository layout

```
src/engram/        Memory system implementation (the testbed)
evals/             Evaluation drivers (entity-collision sweeps, LongMemEval, LoCoMo)
scripts/           Build, repro, and verification scripts
bench/results/     386 result JSON files cited in the paper
bench/reports/     Auto-generated experiment reports
paper/             Paper sources (markdown), references.bib, dist/
tests/             Unit + property tests (pytest)
specs/             Engineering specs cited in paper appendices
DESIGN.md          System design notes (architectural backstory)
```

## Installation

Engram is not on PyPI. Install from source:

```bash
pip install -e ".[dev]"
```

Requires Python ≥ 3.10. Optional extras:
- `[bge]` — adds `sentence-transformers` for the BGE-large embedder used in §4.2
- `[mcp]` — adds the MCP stdio server (orthogonal to the paper)

## Citation

```bibtex
@misc{deng2026entity,
  title={Entity-Collision: A Stratified Protocol for Attributing Retrieval Lift in Agent Memory},
  author={Deng, Youwang},
  year={2026},
  eprint={2605.29630},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2605.29630}
}
```

## License

Apache 2.0 — see [`LICENSE`](LICENSE).

## See also

- [`DESIGN.md`](DESIGN.md) — system design notes; not part of the paper's contribution
- [`paper/A7_extended_methods.md`](paper/A7_extended_methods.md) — testbed implementation details cited from §3
- [`paper/A1_appendix_ablations.md`](paper/A1_appendix_ablations.md) — full ablation grids
