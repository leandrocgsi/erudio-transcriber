from pathlib import Path

from erudio_transcriber.core.vocabulary import hotwords, read_terms


def test_read_terms_skips_comments_and_blank_lines(tmp_path: Path) -> None:
    file = tmp_path / "vocab.txt"
    file.write_text("# header\n\nTinder\n  Amyr Klink  \n", encoding="utf-8")
    assert read_terms(file) == ("Tinder", "Amyr Klink")


def test_hotwords_keeps_the_best_terms_inside_the_budget() -> None:
    assert hotwords(("alpha", "beta", "gamma"), budget=12) == "alpha, beta"


def test_hotwords_is_none_without_terms() -> None:
    assert hotwords(()) is None
