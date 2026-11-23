from PySide6.QtCore import QObject, Signal

from erudio_transcriber.domain.progress import ProgressEvent


class QtProgressSink(QObject):
    """Emits a signal so events raised on the worker thread are handled on the GUI thread."""

    received = Signal(object)

    def report(self, event: ProgressEvent) -> None:
        self.received.emit(event)
