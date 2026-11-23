from collections.abc import Callable
from typing import TypeAlias

from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget

Chooser: TypeAlias = Callable[[QWidget], str]


def choose_folder(parent: QWidget) -> str:
    return QFileDialog.getExistingDirectory(parent, "Choose a folder")


def choose_video(parent: QWidget) -> str:
    path, _ = QFileDialog.getOpenFileName(
        parent, "Choose a video", "", "Videos (*.mp4 *.mkv *.mov *.webm *.ts)"
    )
    return path


class PathPicker(QWidget):
    def __init__(self, label: str, choosers: dict[str, Chooser]) -> None:
        super().__init__()
        self.field = QLineEdit()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(label))
        layout.addWidget(self.field, stretch=1)
        for caption, chooser in choosers.items():
            button = QPushButton(caption)
            button.clicked.connect(lambda _checked=False, pick=chooser: self._choose(pick))
            layout.addWidget(button)

    def text(self) -> str:
        return self.field.text().strip()

    def _choose(self, chooser: Chooser) -> None:
        chosen = chooser(self)
        if chosen:
            self.field.setText(chosen)
