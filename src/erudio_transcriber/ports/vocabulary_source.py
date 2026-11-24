from pathlib import Path
from typing import Protocol


class VocabularySource(Protocol):
    def texts(self, folder: Path) -> tuple[str, ...]: ...
