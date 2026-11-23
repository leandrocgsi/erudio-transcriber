from pathlib import Path

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from erudio_transcriber.application.queue import QueueRequest
from erudio_transcriber.application.vocabulary_lookup import find_vocabulary
from erudio_transcriber.ui.qt.path_picker import PathPicker, choose_folder, choose_video
from erudio_transcriber.ui.qt.progress_panel import ProgressPanel
from erudio_transcriber.ui.qt.settings_panel import SettingsPanel
from erudio_transcriber.ui.qt.sink import QtProgressSink
from erudio_transcriber.ui.qt.worker import QueueWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Erudio Transcriber")
        self.resize(820, 560)
        self.source = PathPicker("Source", {"Folder...": choose_folder, "Video...": choose_video})
        self.output = PathPicker("Output", {"Folder...": choose_folder})
        self.settings = SettingsPanel()
        self.progress = ProgressPanel()
        self.vocabulary = QLabel()
        self.start = QPushButton("Start")
        self.stop = QPushButton("Stop")
        self.stop.setEnabled(False)
        self.worker: QueueWorker | None = None
        self.sink = QtProgressSink()
        self.sink.received.connect(self.progress.show_event)
        self.start.clicked.connect(self.start_queue)
        self.stop.clicked.connect(self.stop_queue)
        self.output.field.textChanged.connect(self.refresh_vocabulary)
        self.setCentralWidget(self._assemble())
        self.refresh_vocabulary()

    def _assemble(self) -> QWidget:
        buttons = QHBoxLayout()
        buttons.addWidget(self.start)
        buttons.addWidget(self.stop)
        buttons.addStretch(1)
        root = QWidget()
        layout = QVBoxLayout(root)
        for widget in (self.source, self.output, self.vocabulary, self.settings):
            layout.addWidget(widget)
        layout.addLayout(buttons)
        layout.addWidget(self.progress, stretch=1)
        return root

    def refresh_vocabulary(self) -> None:
        folder = self.output.text()
        found = find_vocabulary(Path(folder), Path(folder), None) if folder else None
        self.vocabulary.setText(
            f"Vocabulary: {found}"
            if found
            else "Vocabulary: none (put a vocab.txt in the output folder)"
        )

    def start_queue(self) -> None:
        if not self.source.text() or not self.output.text():
            self.progress.show_message("Choose a source and an output first")
            return
        request = QueueRequest(
            Path(self.source.text()), Path(self.output.text()), self.settings.job_settings()
        )
        self.progress.reset()
        self.worker = QueueWorker(request, self.settings.thermal_limits(), {}, self.sink)
        self.worker.summary_ready.connect(self.finish_queue)
        self.worker.crashed.connect(lambda message: self.finish_queue(f"Error: {message}"))
        self._set_running(True)
        self.worker.start()

    def stop_queue(self) -> None:
        if self.worker:
            self.progress.show_message("Stopping after the current segment...")
            self.worker.request_stop()

    def finish_queue(self, message: str) -> None:
        self.progress.show_message(message)
        self._set_running(False)

    def _set_running(self, running: bool) -> None:
        self.start.setEnabled(not running)
        self.stop.setEnabled(running)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.request_stop()
            self.worker.wait(5000)
        super().closeEvent(event)
