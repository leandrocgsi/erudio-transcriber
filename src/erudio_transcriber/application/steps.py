import logging
from collections.abc import Callable
from pathlib import Path

from erudio_transcriber.application.toolkit import Toolkit
from erudio_transcriber.core.formats import clock, render_srt, render_txt
from erudio_transcriber.core.layout import OutputPaths
from erudio_transcriber.domain.errors import EmptyTranscriptError
from erudio_transcriber.domain.progress import ProgressEvent, Stage
from erudio_transcriber.domain.transcript import Segment
from erudio_transcriber.ports.progress_sink import ProgressSink

logger = logging.getLogger(__name__)

DONE_MARKER = ".done"


def transcript_exists(paths: OutputPaths) -> bool:
    return paths.srt.is_file() and paths.txt.is_file() and paths.txt.stat().st_size > 0


def frames_exist(paths: OutputPaths) -> bool:
    return (paths.frames / DONE_MARKER).is_file()


def write_transcript(
    video: Path,
    paths: OutputPaths,
    toolkit: Toolkit,
    language: str,
    hotwords: str | None,
    sink: ProgressSink,
    pace: Callable[[], None],
) -> None:
    audio = toolkit.audio.extract(video, paths.audio)

    def listener(segment: Segment, duration: float) -> None:
        fraction = min(segment.end / duration, 1.0) if duration else None
        sink.report(ProgressEvent(Stage.TRANSCRIPTION, video.name, fraction, clock(segment.end)))
        pace()

    transcript = toolkit.transcriber.transcribe(audio, language, hotwords, listener)
    if not transcript.segments:
        msg = f"Empty transcript: {video.name}"
        raise EmptyTranscriptError(msg)
    paths.srt.write_text(render_srt(transcript.segments), encoding="utf-8")
    paths.txt.write_text(render_txt(transcript.segments), encoding="utf-8")


def write_frames(
    video: Path,
    paths: OutputPaths,
    toolkit: Toolkit,
    sink: ProgressSink,
    pace: Callable[[], None],
) -> None:
    sink.report(ProgressEvent(Stage.FRAMES, video.name, None, "looking for slide changes"))
    seconds_list = toolkit.slides.detect(video)
    kept = 0
    for position, seconds in enumerate(seconds_list, start=1):
        pace()
        total = int(seconds)
        name = f"{total // 3600:02d}-{total % 3600 // 60:02d}-{total % 60:02d}.jpg"
        destination = paths.frames / name
        if destination.exists() or toolkit.frames.extract(video, seconds, destination):
            kept += 1
        else:
            logger.warning("No frame at %ss in %s", seconds, video.name)
        sink.report(ProgressEvent(Stage.FRAMES, video.name, position / len(seconds_list)))
    paths.frames.mkdir(parents=True, exist_ok=True)
    (paths.frames / DONE_MARKER).write_text(f"{kept} frames\n", encoding="utf-8")
