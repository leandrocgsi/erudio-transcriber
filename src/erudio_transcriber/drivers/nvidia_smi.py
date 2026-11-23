import shutil
import subprocess
from dataclasses import dataclass

from erudio_transcriber.domain.thermal import ThermalReading
from erudio_transcriber.registry import Options

QUERY = ["--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"]
TIMEOUT_SECONDS = 10


@dataclass(frozen=True, slots=True)
class NvidiaSmiSensor:
    executable: str

    def read(self) -> ThermalReading:
        try:
            result = subprocess.run(
                [self.executable, *QUERY],
                capture_output=True,
                text=True,
                check=True,
                timeout=TIMEOUT_SECONDS,
            )
            return ThermalReading(gpu_celsius=int(result.stdout.split()[0]), cpu_celsius=None)
        except (OSError, subprocess.SubprocessError, ValueError, IndexError):
            return ThermalReading(gpu_celsius=None, cpu_celsius=None)


def create_thermal_sensor(options: Options) -> NvidiaSmiSensor:
    return NvidiaSmiSensor(options.get("nvidia_smi") or shutil.which("nvidia-smi") or "nvidia-smi")
