import shutil
from pathlib import Path

WINGET_ROOT = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"


class FfmpegNotFoundError(FileNotFoundError):
    pass


def locate_ffmpeg() -> Path:
    on_path = shutil.which("ffmpeg")
    if on_path:
        return Path(on_path)
    if WINGET_ROOT.is_dir():
        for candidate in WINGET_ROOT.glob("Gyan.FFmpeg*/**/bin/ffmpeg.exe"):
            return candidate
    msg = "ffmpeg not found. Install it (Windows: winget install Gyan.FFmpeg)."
    raise FfmpegNotFoundError(msg)
