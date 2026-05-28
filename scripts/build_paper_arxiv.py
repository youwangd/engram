#!/usr/bin/env python3
"""Build an arXiv-ready source tarball for the Engram v0.2 paper.

arXiv compiles user-supplied LaTeX with TeX Live (no shell escape, no docker,
no internet). So the tarball must contain:
  - the assembled .tex
  - all .sty / .bst / .cls referenced
  - all figures (flat paths)
  - a pre-compiled .bbl (arXiv runs bibtex but it's safer to ship the .bbl
    too in case of font / encoding mismatches)
  - NO .aux, .log, .out, .blg, .git, etc.

Inputs: paper/build/acl/* (output of build_paper_acl.py)
Output: paper/dist/engram_v0.2_arxiv.tar.gz

Pipeline:
  1. Run scripts/build_paper_acl.py to ensure build/acl/ is fresh
  2. Read engram_v0.2_acl.tex, patch:
       - [review] → (remove for arXiv — author block visible)
       - \graphicspath → flat ./
       - \author{Anonymous...} → real author block
       - title page additions for arXiv (acks, github link)
  3. Copy figures into a flat dir
  4. Copy .bbl, .sty, .bst alongside .tex
  5. tar -czf the staging dir

Run:
    python scripts/build_paper_arxiv.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAPER_DIR = REPO / "paper"
ACL_BUILD = PAPER_DIR / "build" / "acl"
DIST_DIR = PAPER_DIR / "dist"
STAGE_DIR = PAPER_DIR / "build" / "arxiv_stage"
TARBALL = DIST_DIR / "engram_v0.2_arxiv.tar.gz"


def main() -> int:
    # 1. Ensure ACL build is fresh
    print("=== Step 1: rebuild ACL artifacts ===", flush=True)
    r = subprocess.run([sys.executable, "scripts/build_paper_acl.py"], cwd=REPO)
    if r.returncode != 0:
        print("ACL build failed; arXiv build aborted.", file=sys.stderr)
        return 1

    # 2. Stage directory
    print("\n=== Step 2: stage tarball contents ===", flush=True)
    if STAGE_DIR.exists():
        shutil.rmtree(STAGE_DIR)
    STAGE_DIR.mkdir(parents=True)

    # Copy main tex + bib + bbl + sty + bst
    src_tex = ACL_BUILD / "engram_v0.2_acl.tex"
    src_bbl = ACL_BUILD / "engram_v0.2_acl.bbl"
    if not src_tex.exists():
        print(f"missing {src_tex}", file=sys.stderr)
        return 1
    if not src_bbl.exists():
        print(f"missing {src_bbl} — bibtex pass didn't run?", file=sys.stderr)
        return 1

    # arXiv convention: main file should be unambiguous. Name it "main.tex"
    # so arXiv's autodetect picks it (else it scans every .tex for \documentclass).
    arxiv_tex = STAGE_DIR / "main.tex"
    arxiv_bbl = STAGE_DIR / "main.bbl"
    shutil.copy(ACL_BUILD / "acl.sty", STAGE_DIR / "acl.sty")
    shutil.copy(ACL_BUILD / "acl_natbib.bst", STAGE_DIR / "acl_natbib.bst")
    shutil.copy(ACL_BUILD / "references.bib", STAGE_DIR / "references.bib")
    shutil.copy(src_bbl, arxiv_bbl)

    # 3. Patch the .tex for arXiv
    print("\n=== Step 3: patch .tex for arXiv ===", flush=True)
    tex = src_tex.read_text()

    # 3a. Remove [review] so author block is visible.
    # acl.sty has both [review] and a default (final) mode. Drop [review].
    tex_new = re.sub(r"\\usepackage\[review\]\{acl\}", r"\\usepackage{acl}", tex)
    if tex_new == tex:
        print("WARN: didn't find [review] option to strip", file=sys.stderr)
    tex = tex_new

    # 3b. Flatten \graphicspath. arXiv compiles with cwd = tarball root.
    # Replace the multi-arg list with just {{./}}.
    # Pattern: \graphicspath{ {a}{b}{c} }  — match across the whole single-line
    # form by finding the *next* line break or two-or-more closing braces in row.
    # Simplest: find \graphicspath, then balance braces by hand.
    def _replace_graphicspath(s: str) -> str:
        idx = s.find(r"\graphicspath")
        if idx < 0:
            return s
        # locate the opening { right after the command
        i = idx + len(r"\graphicspath")
        while i < len(s) and s[i] != "{":
            i += 1
        if i >= len(s):
            return s
        depth = 0
        j = i
        while j < len(s):
            c = s[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        return s[:idx] + r"\graphicspath{{./}}" + s[j:]
    tex = _replace_graphicspath(tex)

    # 3c. Flatten image references. In the source they're like
    # \pandocboundedwide{\includegraphics[...]{../bench/results/ec_paper_figure.png}}
    # We copy each figure to ./ in the stage dir; rewrite path to basename.
    figure_refs = set()
    for line in tex.splitlines():
        # ignore TeX comment lines
        stripped = line.lstrip()
        if stripped.startswith("%"):
            continue
        for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", line):
            ref = m.group(1)
            # drop placeholder/comment-y values
            if ref in {"...", ""} or ref.startswith("..."):
                continue
            figure_refs.add(ref)
    print(f"  found {len(figure_refs)} figure ref(s):")
    for fref in figure_refs:
        # source may be relative to paper/ or absolute /data/...
        # normalize: try in REPO, in paper/, and in bench/results/
        candidates = [
            REPO / fref,
            REPO / "paper" / fref,
            REPO / fref.lstrip("./").replace("../", ""),
        ]
        if fref.startswith("/data/"):
            candidates.insert(0, REPO / fref[len("/data/"):])
        src = next((c for c in candidates if c.exists()), None)
        if src is None:
            print(f"    MISSING: {fref}", file=sys.stderr)
            return 1
        dst_name = Path(fref).name
        shutil.copy(src, STAGE_DIR / dst_name)
        # rewrite all occurrences in tex
        tex = tex.replace(fref, dst_name)
        print(f"    {fref}  →  ./{dst_name}  ({src.relative_to(REPO)})")

    # 3d. Replace anonymous author block with real one.
    # Use balanced-brace replacement (the original \author{...} contains a
    # nested \texttt{...}, so simple [^}]* doesn't work — it stops at the
    # first close brace and leaves a stray } behind).
    real_author = (
        "\\author{Youwang Deng \\\\ "
        "Independent Researcher \\\\ "
        "\\texttt{dengyouwang@gmail.com}}"
    )

    def _replace_author(s: str) -> tuple[str, int]:
        idx = s.find(r"\author{")
        if idx < 0:
            return s, 0
        i = idx + len(r"\author{")
        depth = 1
        while i < len(s) and depth > 0:
            c = s[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            i += 1
        if depth != 0:
            return s, 0
        # i now points one past the matching close
        return s[:idx] + real_author + s[i:], 1

    tex, n = _replace_author(tex)
    if n == 0:
        print("WARN: didn't find \\author block to replace", file=sys.stderr)
    else:
        print(f"  replaced \\author block ({n} match)")

    # 3e. Add a small \date{} block + GitHub link in the abstract or after \maketitle.
    # Insert a footnote on the title using \thanks for the GitHub repo.
    # The acl.sty title block doesn't easily support \thanks, so add a small
    # \begin{center}...\end{center} immediately after \maketitle.
    repo_block = (
        r"\\maketitle" "\n"
        r"\\begin{center}\\small" "\n"
        r"Code, benchmarks, and reproduce scripts:" "\n"
        r"\\url{https://github.com/youwangd/engram}\\\\(Apache 2.0 licensed)" "\n"
        r"\\end{center}" "\n"
    )
    tex_new = re.sub(r"\\maketitle\s*", repo_block, tex, count=1)
    if tex_new == tex:
        print("WARN: didn't find \\maketitle to inject github link", file=sys.stderr)
    tex = tex_new

    # 3f. Make sure pdfinfo (\hypersetup) declares the author.
    if "\\hypersetup" not in tex:
        tex = tex.replace(
            "\\begin{document}",
            "\\hypersetup{pdfauthor={Youwang Deng}, pdftitle={Entity-Collision: A Stratified Protocol for Attributing Retrieval Lift in Agent Memory}}\n\\begin{document}",
            1,
        )

    arxiv_tex.write_text(tex)
    print(f"  wrote {arxiv_tex.relative_to(REPO)}")

    # 4. README inside the tarball (arXiv encourages a brief README)
    readme = STAGE_DIR / "README.md"
    readme.write_text(
        "# Engram v0.2 — arXiv source\n\n"
        "Compile with:\n\n"
        "    xelatex main\n"
        "    bibtex  main\n"
        "    xelatex main\n"
        "    xelatex main\n\n"
        "or just `xelatex main` twice if you trust the bundled `main.bbl`.\n\n"
        "Repo: https://github.com/youwangd/engram (Apache 2.0)\n"
    )

    # 5. tar it up
    print("\n=== Step 4: create tarball ===", flush=True)
    DIST_DIR.mkdir(exist_ok=True)
    if TARBALL.exists():
        TARBALL.unlink()
    with tarfile.open(TARBALL, "w:gz") as tf:
        for p in sorted(STAGE_DIR.rglob("*")):
            if p.is_file():
                arcname = p.relative_to(STAGE_DIR)
                tf.add(p, arcname=str(arcname))
                print(f"  + {arcname}")
    print(f"\n✓ wrote {TARBALL}  ({TARBALL.stat().st_size:,} bytes)")

    # 6. dry-run compile inside docker to make sure it actually builds
    print("\n=== Step 5: dry-run compile in Docker (TeX Live) ===", flush=True)
    test_dir = STAGE_DIR  # compile in place
    import os
    docker_base = [
        "docker", "run", "--rm",
        "-u", f"{os.getuid()}:{os.getgid()}",
        "-v", f"{test_dir}:/work",
        "-w", "/work",
    ]
    # First xelatex pass
    for label, args in [
        ("xelatex-1", ["xelatex", "-interaction=nonstopmode", "main"]),
        ("bibtex",    ["bibtex", "main"]),
        ("xelatex-2", ["xelatex", "-interaction=nonstopmode", "main"]),
        ("xelatex-3", ["xelatex", "-interaction=nonstopmode", "main"]),
    ]:
        cmd = docker_base + ["--entrypoint", args[0], "pandoc-acl:engram"] + args[1:]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  {label} FAILED (exit {r.returncode})")
            print(r.stdout[-2000:])
            print(r.stderr[-1000:])
            return 1
        print(f"  {label} ok")
    test_pdf = test_dir / "main.pdf"
    if test_pdf.exists():
        sz = test_pdf.stat().st_size
        print(f"✓ test compile produced main.pdf ({sz:,} bytes)")
        # also copy as the dist arxiv pdf for inspection
        shutil.copy(test_pdf, DIST_DIR / "engram_v0.2_arxiv.pdf")
        print(f"  copied to {DIST_DIR / 'engram_v0.2_arxiv.pdf'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
