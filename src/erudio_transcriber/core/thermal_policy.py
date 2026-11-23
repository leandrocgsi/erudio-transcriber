from erudio_transcriber.domain.thermal import ThermalAction, ThermalLimits, ThermalReading


def hottest(reading: ThermalReading) -> int | None:
    values = [value for value in (reading.gpu_celsius, reading.cpu_celsius) if value is not None]
    return max(values) if values else None


def decide(reading: ThermalReading, limits: ThermalLimits, paused: bool) -> ThermalAction:
    temperature = hottest(reading)
    if temperature is None:
        return ThermalAction.RUN
    if temperature >= limits.pause_at:
        return ThermalAction.PAUSE
    if paused and temperature > limits.resume_at:
        return ThermalAction.PAUSE
    return ThermalAction.RUN
