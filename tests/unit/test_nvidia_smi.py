import subprocess

import pytest

from erudio_transcriber.drivers.nvidia_smi import create_thermal_sensor


def fake_run(output: str) -> object:
    def run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout=output)

    return run


def test_sensor_reads_the_gpu_temperature(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subprocess, "run", fake_run("67\n"))
    reading = create_thermal_sensor({"nvidia_smi": "nvidia-smi"}).read()
    assert reading.gpu_celsius == 67
    assert reading.cpu_celsius is None


def test_sensor_returns_an_empty_reading_when_the_tool_is_missing() -> None:
    reading = create_thermal_sensor({"nvidia_smi": "definitely-not-installed"}).read()
    assert reading.gpu_celsius is None


def test_sensor_returns_an_empty_reading_for_unreadable_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(subprocess, "run", fake_run("N/A\n"))
    assert create_thermal_sensor({"nvidia_smi": "nvidia-smi"}).read().gpu_celsius is None
