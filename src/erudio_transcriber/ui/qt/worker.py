import logging
import threading

from PySide6.QtCore import QThread, Signal

from erudio_transcriber.application.queue import QueueRequest, run_queue
from erudio_transcriber.composition import build_gate, build_toolkit
from erudio_transcriber.domain.thermal import ThermalLimits
from erudio_transcriber.ui.qt.sink import QtProgressSink

logger = logging.getLogger(__name__)


class QueueWorker(QThread):
    summary_ready = Signal(str)
    crashed = Signal(str)

    def __init__(
        self,
        request: QueueRequest,
        limits: ThermalLimits,
        options: dict[str, str],
        sink: QtProgressSink,
    ) -> None:
        super().__init__()
        self.request = request
        self.limits = limits
        self.options = options
        self.sink = sink
        self.stop = threading.Event()

    def run(self) -> None:
        try:
            toolkit = build_toolkit(self.options)
            gate = build_gate(toolkit, self.limits, self.sink, self.stop)
            summary = run_queue(self.request, toolkit, gate, self.sink)
        except Exception as error:
            logger.exception("Queue crashed")
            self.crashed.emit(str(error))
            return
        failed = f", failed: {', '.join(summary.failed)}" if summary.failed else ""
        state = "Cancelled" if summary.cancelled else "Finished"
        self.summary_ready.emit(
            f"{state}: {summary.processed} processed, {summary.skipped} already done{failed}"
        )

    def request_stop(self) -> None:
        self.stop.set()
