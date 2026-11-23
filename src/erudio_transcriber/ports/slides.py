from collections.abc import Sequence
from pathlib import Path
from typing import Protocol


class SlideDetector(Protocol):
    def detect(self, video: Path) -> Sequence[float]: ...


class FrameExtractor(Protocol):
    def extract(self, video: Path, seconds: float, destination: Path) -> bool: ...
