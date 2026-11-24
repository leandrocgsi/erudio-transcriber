from collections.abc import Sequence
from pathlib import Path

from erudio_transcriber.core.term_extraction import extract_terms
from erudio_transcriber.ports.vocabulary_source import VocabularySource

HEADER = "# Whisper hotwords: one term per line, best first. Edit freely; this file is the source."


def build_vocabulary(
    folder: Path, sources: Sequence[VocabularySource], limit: int
) -> tuple[str, ...]:
    return extract_terms((text for source in sources for text in source.texts(folder)), limit)


def write_vocabulary(destination: Path, terms: Sequence[str]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join([HEADER, *terms]) + "\n", encoding="utf-8")
