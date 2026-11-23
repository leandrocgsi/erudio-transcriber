from PySide6.QtWidgets import QLabel, QPlainTextEdit, QProgressBar, QVBoxLayout, QWidget

from erudio_transcriber.domain.progress import ProgressEvent, Stage

PERCENT = 100


class ProgressPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.status = QLabel("Idle")
        self.bar = QProgressBar()
        self.bar.setRange(0, PERCENT)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.status)
        layout.addWidget(self.bar)
        layout.addWidget(self.log, stretch=1)

    def show_event(self, event: ProgressEvent) -> None:
        self.status.setText(f"{event.stage.value}: {event.item} {event.detail}".strip())
        if event.fraction is not None:
            self.bar.setValue(round(event.fraction * PERCENT))
        if event.stage in {Stage.PAUSED, Stage.DONE, Stage.FAILED}:
            self.log.appendPlainText(f"{event.stage.value}: {event.item} {event.detail}".strip())

    def show_message(self, message: str) -> None:
        self.status.setText(message)
        self.log.appendPlainText(message)

    def reset(self) -> None:
        self.bar.setValue(0)
        self.log.clear()
