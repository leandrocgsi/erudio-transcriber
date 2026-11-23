from collections.abc import Callable
from pathlib import Path
from typing import Protocol, TypeAlias

from erudio_transcriber.domain.transcript import Segment, Transcript

SegmentListener: TypeAlias = Callable[[Segment, float], None]


class Transcriber(Protocol):
    def transcribe(
        self, audio: Path, language: str, hotwords: str | None, listener: SegmentListener
    ) -> Transcript: ...
