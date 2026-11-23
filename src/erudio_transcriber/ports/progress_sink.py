from typing import Protocol

from erudio_transcriber.domain.progress import ProgressEvent


class ProgressSink(Protocol):
    def report(self, event: ProgressEvent) -> None: ...
