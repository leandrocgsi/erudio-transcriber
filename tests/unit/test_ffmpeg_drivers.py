import subprocess
from pathlib import Path

import pytest

from erudio_transcriber.drivers.ffmpeg_audio import create_audio_extractor
from erudio_transcriber.drivers.ffmpeg_frames import create_frame_extractor
from erudio_transcriber.drivers.ffmpeg_locator import FfmpegNotFoundError, locate_ffmpeg
from erudio_transcriber.drivers.ffmpeg_slides import create_slide_detector


def ffmpeg_or_skip() -> Path:
    try:
        return locate_ffmpeg()
    except FfmpegNotFoundError:
        pytest.skip("ffmpeg is not installed")


@pytest.fixture(scope="module")
def two_slide_video(tmp_path_factory: pytest.TempPathFactory) -> Path:
    ffmpeg = ffmpeg_or_skip()
    video = tmp_path_factory.mktemp("media") / "slides.mp4"
    command = [str(ffmpeg), "-hide_banner", "-loglevel", "error", "-y"]
    command += ["-f", "lavfi", "-i", "color=c=black:s=320x180:d=10:r=10"]
    command += ["-f", "lavfi", "-i", "color=c=white:s=320x180:d=10:r=10"]
    command += ["-f", "lavfi", "-i", "sine=frequency=440:duration=20"]
    command += ["-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]", "-map", "[v]", "-map", "2:a"]
    command += ["-pix_fmt", "yuv420p", "-shortest", str(video)]
    subprocess.run(command, check=True, stdin=subprocess.DEVNULL)
    return video


def test_audio_extractor_writes_an_mp3_and_reuses_it(two_slide_video: Path, tmp_path: Path) -> None:
    extractor = create_audio_extractor({})
    destination = tmp_path / "nested" / "slides.mp3"
    assert extractor.extract(two_slide_video, destination) == destination
    first_size = destination.stat().st_size
    assert first_size > 0
    assert not (tmp_path / "nested" / "slides.part.mp3").exists()
    assert extractor.extract(two_slide_video, destination).stat().st_size == first_size


def test_slide_detector_finds_the_first_frame_and_the_change(two_slide_video: Path) -> None:
    seconds = create_slide_detector({}).detect(two_slide_video)
    assert seconds[0] == 0.0
    assert len(seconds) == 2
    assert 10.0 <= seconds[1] <= 13.0


def test_slide_detector_without_enough_samples_finds_nothing(tmp_path: Path) -> None:
    empty = tmp_path / "not-a-video.mp4"
    empty.write_bytes(b"")
    assert create_slide_detector({}).detect(empty) == ()


def test_frame_extractor_saves_a_jpeg(two_slide_video: Path, tmp_path: Path) -> None:
    destination = tmp_path / "frames" / "00-00-01.jpg"
    assert create_frame_extractor({}).extract(two_slide_video, 1.0, destination) is True
    assert destination.stat().st_size > 0


def test_frame_extractor_reports_failure_for_a_broken_video(tmp_path: Path) -> None:
    broken = tmp_path / "broken.mp4"
    broken.write_bytes(b"not a video")
    destination = tmp_path / "frame.jpg"
    assert create_frame_extractor({}).extract(broken, 5.0, destination) is False
