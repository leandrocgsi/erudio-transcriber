from pathlib import Path
from typing import Protocol


class AudioExtractor(Protocol):
    def extract(self, video: Path, destination: Path) -> Path: ...
