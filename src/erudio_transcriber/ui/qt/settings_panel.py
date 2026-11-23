from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QSpinBox, QWidget

from erudio_transcriber.application.toolkit import JobSettings
from erudio_transcriber.domain.thermal import ThermalLimits

LANGUAGES = {"Portuguese": "pt", "English": "en", "Spanish": "es"}


class SettingsPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.language = QComboBox()
        self.language.addItems(list(LANGUAGES))
        self.frames = QCheckBox("Slide-change frames")
        self.frames.setChecked(True)
        self.pause_at = _temperature_box(78)
        self.resume_at = _temperature_box(72)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("Language"))
        layout.addWidget(self.language)
        layout.addWidget(self.frames)
        layout.addStretch(1)
        layout.addWidget(QLabel("Pause at (C)"))
        layout.addWidget(self.pause_at)
        layout.addWidget(QLabel("Resume at (C)"))
        layout.addWidget(self.resume_at)

    def job_settings(self) -> JobSettings:
        return JobSettings(LANGUAGES[self.language.currentText()], self.frames.isChecked())

    def thermal_limits(self) -> ThermalLimits:
        return ThermalLimits(self.pause_at.value(), self.resume_at.value())


def _temperature_box(value: int) -> QSpinBox:
    box = QSpinBox()
    box.setRange(40, 95)
    box.setValue(value)
    return box
