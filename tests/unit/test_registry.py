from importlib.metadata import EntryPoint

import pytest

from erudio_transcriber import registry
from erudio_transcriber.registry import DriverGroup, DriverNotFoundError, available, load


def fake_entry_points(**_: str) -> tuple[EntryPoint, ...]:
    return (EntryPoint("sample", "collections:OrderedDict", DriverGroup.TRANSCRIBER.value),)


def no_entry_points(**_: str) -> tuple[EntryPoint, ...]:
    return ()


def test_builtin_drivers_are_registered() -> None:
    assert "faster-whisper" in available(DriverGroup.TRANSCRIBER)
    assert "nvidia-smi" in available(DriverGroup.THERMAL_SENSOR)


def test_load_reports_the_missing_driver_by_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(registry, "entry_points", no_entry_points)
    with pytest.raises(DriverNotFoundError, match="whisper"):
        load(DriverGroup.TRANSCRIBER, "whisper")


def test_load_returns_the_registered_factory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(registry, "entry_points", fake_entry_points)
    assert available(DriverGroup.TRANSCRIBER) == ("sample",)
    assert load(DriverGroup.TRANSCRIBER, "sample")({}) == {}
