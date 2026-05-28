"""Tests for scripts/check_anon.py — EMNLP review-PDF anonymization linter."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_anon.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_anon", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_anon"] = mod  # required for dataclasses introspection
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load_module()


# --- token detection -------------------------------------------------------

@pytest.mark.parametrize("text,label_substr", [
    ("This work was done by Youwang Deng.", "name:youwang"),
    ("Contact: dengyouwang@example.com.", "email:dengyouwang"),
    ("Run on an Amazon Linux box.", "employer:amazon"),
    ("a2z internal tooling.", "employer:a2z"),
    ("Within the corp network.", "employer:corp"),
    ("on a Cloud Desktop instance.", "phrase:cloud-desktop"),
    ("on a cloud  desktop instance.", "phrase:cloud-desktop"),
    ("box.corp.amazon.com was used", "host:corp.amazon"),
    ("internal.a2z.com was used", "host:a2z.com"),
    ("AWS account 123456789012 ran the test.", "aws:account-id"),
    ("see https://github.com/youwangd/Engram for code.", "github:youwangd"),
])
def test_each_forbidden_pattern_fires(mod, text, label_substr):
    findings = list(mod.lint_text(text, path="t"))
    labels = [f.label for f in findings]
    assert any(label_substr in lbl for lbl in labels), \
        f"expected {label_substr!r} in {labels!r} for text={text!r}"


# --- safe text (no false positives on common English) ---------------------

@pytest.mark.parametrize("text", [
    "We trained on the corpus of LongMemEval queries.",
    "The corpora include NQ, HotpotQA, and FiQA.",
    "Corporate sponsorship is disclosed below.",  # 'corporate' != 'corp'
    "Anonymous Author, Anonymous Affiliation.",
    "github.com/anonymous-engram/repo (anonymized).",
    # 'Amazonian' is NOT 'amazon' under \b — substring inside a longer word.
    "We use the Amazonian rainforest as a metaphor.",
    # A 13-digit number must NOT trip the 12-digit AWS rule.
    "The corpus contains 1234567890123 tokens overall.",
    # Embedded digits in a longer string should not trip.
    "checksum 0123456789012345 is fine.",
])
def test_safe_text_no_false_positives_for_corpus_corpora(mod, text):
    findings = list(mod.lint_text(text, path="t"))
    assert findings == [], f"unexpected findings for safe text {text!r}: {findings}"


def test_amazon_word_boundary_strict(mod):
    """The bare word 'Amazon' must fire; 'Amazonian' must not."""
    assert any(
        f.label == "employer:amazon"
        for f in mod.lint_text("Run on Amazon hardware.", path="t")
    )
    assert not any(
        f.label == "employer:amazon"
        for f in mod.lint_text("The Amazonian rainforest.", path="t")
    )


# --- HTML comments stripped by default, scanned with --strict --------------

def test_html_comments_ignored_by_default(mod):
    text = "Body OK.\n<!-- written by Youwang Deng on cloud desktop -->\nMore body."
    findings = list(mod.lint_text(text, path="t"))
    assert findings == []


def test_html_comments_scanned_under_strict(mod):
    text = "Body OK.\n<!-- written by Youwang Deng on cloud desktop -->\nMore body."
    findings = list(mod.lint_text(text, path="t", strict=True))
    labels = {f.label for f in findings}
    assert "name:youwang" in labels
    assert "phrase:cloud-desktop" in labels


def test_line_numbers_preserved_after_comment_strip(mod):
    text = (
        "line 1 fine\n"
        "<!-- multi\n"
        "     line\n"
        "     comment -->\n"
        "Youwang on line 5\n"
    )
    findings = [f for f in mod.lint_text(text, path="t") if f.label == "name:youwang"]
    assert len(findings) == 1
    assert findings[0].line == 5


# --- end-to-end: lint the actual paper body --------------------------------

def test_paper_body_clean_under_default_mode(mod):
    """The numbered paper body (00..70) must lint clean before review-PDF
    build. HTML comments allowed (pandoc strips them)."""
    targets = [REPO_ROOT / p for p in mod.DEFAULT_TARGETS if (REPO_ROOT / p).exists()]
    assert targets, "no paper body files found"
    findings = mod.lint_files(targets)
    assert findings == [], (
        "paper body has anonymization findings — fix before submission:\n"
        + "\n".join(f.format() for f in findings)
    )


# --- CLI exit codes --------------------------------------------------------

def test_cli_clean_returns_0(mod, tmp_path, capsys):
    p = tmp_path / "clean.md"
    p.write_text("All anonymous, all the time.\n")
    rc = mod.main([str(p)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "OK" in out


def test_cli_dirty_returns_1(mod, tmp_path, capsys):
    p = tmp_path / "dirty.md"
    p.write_text("Authored by Youwang in the corp network.\n")
    rc = mod.main([str(p)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "FAIL" in out
    assert "name:youwang" in out
    assert "employer:corp" in out


def test_cli_no_targets_returns_2(mod, tmp_path, capsys, monkeypatch):
    # Run from a directory with no paper/ tree, no args.
    monkeypatch.chdir(tmp_path)
    rc = mod.main([])
    err = capsys.readouterr().err
    assert rc == 2
    assert "no targets" in err.lower()
