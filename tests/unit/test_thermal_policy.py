from erudio_transcriber.core.thermal_policy import decide, hottest
from erudio_transcriber.domain.thermal import ThermalAction, ThermalLimits, ThermalReading

LIMITS = ThermalLimits(pause_at=78, resume_at=72)


def reading(gpu: int | None, cpu: int | None = None) -> ThermalReading:
    return ThermalReading(gpu_celsius=gpu, cpu_celsius=cpu)


def test_hottest_ignores_missing_sensors() -> None:
    assert hottest(reading(None, 60)) == 60
    assert hottest(reading(None, None)) is None


def test_runs_when_no_sensor_answers() -> None:
    assert decide(reading(None), LIMITS, paused=False) is ThermalAction.RUN


def test_pauses_at_the_upper_limit() -> None:
    assert decide(reading(78), LIMITS, paused=False) is ThermalAction.PAUSE


def test_stays_paused_until_it_cools_below_the_resume_point() -> None:
    assert decide(reading(75), LIMITS, paused=True) is ThermalAction.PAUSE
    assert decide(reading(72), LIMITS, paused=True) is ThermalAction.RUN


def test_keeps_running_between_the_two_limits() -> None:
    assert decide(reading(75), LIMITS, paused=False) is ThermalAction.RUN
