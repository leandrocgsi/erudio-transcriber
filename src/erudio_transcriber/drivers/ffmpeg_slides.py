import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

import numpy as np
from numpy.typing import NDArray

from erudio_transcriber.core.slide_selection import drop_duplicates, frame_second, merge_changes
from erudio_transcriber.drivers.ffmpeg_locator import locate_ffmpeg
from erudio_transcriber.registry import Options

WIDTH = 128
HEIGHT = 72
STEP_SECONDS = 2.0
MINIMUM_SAMPLES = 2

Sample: TypeAlias = NDArray[np.float32]


@dataclass(frozen=True, slots=True)
class FfmpegSlideDetector:
    executable: Path
    threshold: float = 12.0
    merge_seconds: float = 6.0
    duplicate_limit: float = 6.0

    def detect(self, video: Path) -> Sequence[float]:
        samples = self._sample(video)
        if len(samples) < MINIMUM_SAMPLES:
            return ()
        changes = [
            index
            for index in range(1, len(samples))
            if _difference(samples, index, index - 1) > self.threshold
        ]
        merged = merge_changes(changes, STEP_SECONDS, self.merge_seconds)
        kept = drop_duplicates(
            merged, lambda first, second: _difference(samples, first, second), self.duplicate_limit
        )
        return tuple(float(frame_second(index, STEP_SECONDS)) for index in kept)

    def _sample(self, video: Path) -> list[Sample]:
        command = [str(self.executable), "-hide_banner", "-loglevel", "error", "-i", str(video)]
        command += ["-vf", f"fps=1/{STEP_SECONDS:g},scale={WIDTH}:{HEIGHT},format=gray"]
        command += ["-f", "rawvideo", "-"]
        size = WIDTH * HEIGHT
        samples: list[Sample] = []
        with subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL) as process:
            stream = process.stdout
            while stream is not None and len(chunk := stream.read(size)) == size:
                samples.append(np.frombuffer(chunk, np.uint8).astype(np.float32))
        return samples


def _difference(samples: Sequence[Sample], first: int, second: int) -> float:
    return float(np.abs(samples[first] - samples[second]).mean())


def create_slide_detector(options: Options) -> FfmpegSlideDetector:
    executable = Path(options["ffmpeg"]) if "ffmpeg" in options else locate_ffmpeg()
    return FfmpegSlideDetector(executable, threshold=float(options.get("slide_threshold", 12.0)))
