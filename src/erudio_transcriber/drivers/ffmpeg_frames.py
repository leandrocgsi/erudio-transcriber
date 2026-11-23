import subprocess
from dataclasses import dataclass
from pathlib import Path

from erudio_transcriber.drivers.ffmpeg_locator import locate_ffmpeg
from erudio_transcriber.registry import Options

BACK_OFF_SECONDS = (0, 1, 2, 3)


@dataclass(frozen=True, slots=True)
class FfmpegFrameExtractor:
    executable: Path

    def extract(self, video: Path, seconds: float, destination: Path) -> bool:
        """A change detected in the last second can point past the end, so it backs off a little."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        for back in BACK_OFF_SECONDS:
            command = [str(self.executable), "-hide_banner", "-loglevel", "error", "-y"]
            command += ["-ss", str(max(seconds - back, 0)), "-i", str(video)]
            command += ["-frames:v", "1", "-q:v", "3", str(destination)]
            subprocess.run(command, check=False, stdin=subprocess.DEVNULL)
            if destination.exists() and destination.stat().st_size > 0:
                return True
        return False


def create_frame_extractor(options: Options) -> FfmpegFrameExtractor:
    return FfmpegFrameExtractor(Path(options["ffmpeg"]) if "ffmpeg" in options else locate_ffmpeg())
