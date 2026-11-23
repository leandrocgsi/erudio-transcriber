import subprocess
from dataclasses import dataclass
from pathlib import Path

from erudio_transcriber.drivers.ffmpeg_locator import locate_ffmpeg
from erudio_transcriber.registry import Options


@dataclass(frozen=True, slots=True)
class FfmpegAudioExtractor:
    executable: Path

    def extract(self, video: Path, destination: Path) -> Path:
        """Writes through a .part file so a half-written mp3 is never taken for a finished one."""
        if destination.exists() and destination.stat().st_size > 0:
            return destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        partial = destination.with_name(f"{destination.stem}.part.mp3")
        command = [str(self.executable), "-hide_banner", "-loglevel", "error", "-y"]
        command += ["-i", str(video), "-vn", "-ac", "1", "-ar", "16000", "-b:a", "48k"]
        subprocess.run([*command, str(partial)], check=True, stdin=subprocess.DEVNULL)
        partial.replace(destination)
        return destination


def create_audio_extractor(options: Options) -> FfmpegAudioExtractor:
    return FfmpegAudioExtractor(Path(options["ffmpeg"]) if "ffmpeg" in options else locate_ffmpeg())
