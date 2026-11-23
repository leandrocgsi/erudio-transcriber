from dataclasses import dataclass
from enum import StrEnum


class ThermalAction(StrEnum):
    RUN = "run"
    PAUSE = "pause"


@dataclass(frozen=True, slots=True)
class ThermalReading:
    gpu_celsius: int | None
    cpu_celsius: int | None


@dataclass(frozen=True, slots=True)
class ThermalLimits:
    """Pause at `pause_at`, resume only at `resume_at`, so the job does not flap."""

    pause_at: int = 78
    resume_at: int = 72
