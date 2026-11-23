from dataclasses import dataclass
from pathlib import Path

from erudio_transcriber.core.media_files import clean_stem


@dataclass(frozen=True, slots=True)
class OutputPaths:
    audio: Path
    srt: Path
    txt: Path
    frames: Path


def mirror(source: Path, source_root: Path, output_root: Path) -> Path:
    """Same relative tree under the output root, so the source folder is never written to."""
    return output_root / source.relative_to(source_root)


def output_paths(video: Path, source_root: Path, output_root: Path) -> OutputPaths:
    folder = mirror(video.parent, source_root, output_root)
    stem = clean_stem(video)
    return OutputPaths(
        audio=folder / f"{stem}.mp3",
        srt=folder / f"{stem}.srt",
        txt=folder / f"{stem}.txt",
        frames=folder / f"{stem}.frames",
    )
