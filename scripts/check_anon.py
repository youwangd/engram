#!/usr/bin/env python3
"""Anonymization linter for the EMNLP review-PDF body.

Implements the mandatory anonymization checklist from `paper/VENUE.md`:
no `youwang`, `dengyouwang`, `amazon`, `a2z`, `corp`, `cloud desktop`,
internal `*.corp.amazon.com` hostnames, AWS account numbers (12-digit),
or self-identifying GitHub URLs in the body of the submitted manuscript.

Scope: by default lints paper body files only — i.e. the numbered
section files `paper/00_abstract.md` through `paper/70_conclusion.md`.
Build/venue/reproducibility/README files are NOT in the submission PDF
and are excluded.

HTML comments (`<!-- ... -->`) are stripped before scanning because
pandoc drops them by default — they're safe in source. If you want
strict source-level cleanliness, pass `--strict`.

Exit codes
----------
0  no findings
1  one or more findings (with line numbers + matched token)
2  usage error

Usage
-----
    python scripts/check_anon.py                  # lint paper body
    python scripts/check_anon.py --strict         # also scan inside <!-- -->
    python scripts/check_anon.py paper/40_results.md  # specific file(s)
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

# (label, compiled regex). Patterns are case-insensitive unless noted.
# Word-boundaries are used where the token would otherwise match common
# English (e.g. "corp" inside "corpus").
FORBIDDEN: list[tuple[str, re.Pattern[str]]] = [
    ("name:youwang", re.compile(r"\byouwang\b", re.IGNORECASE)),
    ("email:dengyouwang", re.compile(r"\bdengyouwang\b", re.IGNORECASE)),
    ("employer:amazon", re.compile(r"\bamazon\b", re.IGNORECASE)),
    ("employer:a2z", re.compile(r"\ba2z\b", re.IGNORECASE)),
    # `corp` only when it stands alone (avoid "corpus", "corpora").
    ("employer:corp", re.compile(r"\bcorp\b", re.IGNORECASE)),
    # `corporate` / `corporation` — flag when adjacent to a sponsor cue.
    ("phrase:cloud-desktop", re.compile(r"\bcloud[-\s]+desktop\b", re.IGNORECASE)),
    # Internal hostname patterns: *.corp.amazon.com, *.aws.dev, .a2z.com etc.
    ("host:corp.amazon", re.compile(r"\b[\w.-]+\.corp\.amazon\.(?:com|dev)\b", re.IGNORECASE)),
    ("host:a2z.com", re.compile(r"\b[\w.-]+\.a2z\.com\b", re.IGNORECASE)),
    # 12-digit AWS account numbers (rough — flag for human review).
    ("aws:account-id", re.compile(r"(?<!\d)\d{12}(?!\d)")),
    # Self-identifying GitHub URL (the public org name reveals identity
    # before camera-ready). VENUE.md says: replace with `[anonymized]`.
    ("github:youwangd", re.compile(r"github\.com/youwangd\b", re.IGNORECASE)),
]

DEFAULT_TARGETS = [
    "paper/00_abstract.md",
    "paper/10_intro.md",
    "paper/20_related.md",
    "paper/30_methods.md",
    "paper/40_results.md",
    "paper/50_discussion.md",
    "paper/60_threats.md",
    "paper/70_conclusion.md",
]

HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    label: str
    matched: str
    excerpt: str

    def format(self) -> str:
        return f"{self.path}:{self.line}: [{self.label}] {self.matched!r} :: {self.excerpt}"


def strip_html_comments(text: str) -> str:
    """Replace each HTML comment with same-length whitespace (preserving
    line numbers + columns) so post-strip line numbers still match the
    source file."""
    def _blank(m: re.Match[str]) -> str:
        s = m.group(0)
        # Preserve newlines so line numbering is unchanged.
        return "".join("\n" if ch == "\n" else " " for ch in s)
    return HTML_COMMENT.sub(_blank, text)


def lint_text(text: str, *, path: str, strict: bool = False) -> Iterator[Finding]:
    scan = text if strict else strip_html_comments(text)
    lines = scan.splitlines()
    for lineno, line in enumerate(lines, start=1):
        for label, pat in FORBIDDEN:
            for m in pat.finditer(line):
                yield Finding(
                    path=path,
                    line=lineno,
                    label=label,
                    matched=m.group(0),
                    excerpt=line.strip()[:160],
                )


def lint_files(paths: Iterable[Path], *, strict: bool = False) -> list[Finding]:
    out: list[Finding] = []
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"warn: cannot read {p}: {e}", file=sys.stderr)
            continue
        out.extend(lint_text(text, path=str(p), strict=strict))
    return out


def _resolve_targets(args: list[str]) -> list[Path]:
    if args:
        return [Path(a) for a in args]
    # Default: paper body (resolve relative to repo root = cwd).
    return [Path(p) for p in DEFAULT_TARGETS if Path(p).exists()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    parser.add_argument(
        "paths", nargs="*",
        help="Files to lint (default: paper/00..70_*.md body files).",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Also scan inside HTML comments (pandoc strips them by default).",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Print only the finding count + paths, not each line.",
    )
    ns = parser.parse_args(argv)

    targets = _resolve_targets(ns.paths)
    if not targets:
        print("error: no targets to lint", file=sys.stderr)
        return 2

    findings = lint_files(targets, strict=ns.strict)
    if not findings:
        print(f"OK: 0 findings across {len(targets)} file(s).")
        return 0

    if ns.quiet:
        print(f"FAIL: {len(findings)} finding(s).")
    else:
        for f in findings:
            print(f.format())
        print(f"FAIL: {len(findings)} finding(s) across {len({f.path for f in findings})} file(s).")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
