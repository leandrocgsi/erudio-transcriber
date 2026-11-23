from pathlib import Path

from erudio_transcriber.core.vocabulary import hotwords, read_terms

VOCABULARY_FILE = "vocab.txt"


def find_vocabulary(video_folder: Path, output_root: Path, explicit: Path | None) -> Path | None:
    """An explicit file wins, then the video's own folder, then the project-wide file."""
    candidates = (explicit, video_folder / VOCABULARY_FILE, output_root / VOCABULARY_FILE)
    return next((path for path in candidates if path is not None and path.is_file()), None)


def hotwords_for(vocabulary: Path | None) -> str | None:
    return hotwords(read_terms(vocabulary)) if vocabulary else None
