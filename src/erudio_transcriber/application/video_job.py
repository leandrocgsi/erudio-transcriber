from collections.abc import Callable
from pathlib import Path

from erudio_transcriber.application.steps import (
    frames_exist,
    transcript_exists,
    write_frames,
    write_transcript,
)
from erudio_transcriber.application.toolkit import JobSettings, Toolkit
from erudio_transcriber.core.layout import OutputPaths
from erudio_transcriber.domain.progress import ProgressEvent, Stage
from erudio_transcriber.ports.progress_sink import ProgressSink


def process_video(
    video: Path,
    paths: OutputPaths,
    toolkit: Toolkit,
    settings: JobSettings,
    hotwords: str | None,
    sink: ProgressSink,
    pace: Callable[[], None],
) -> bool:
    """Returns False when everything was already there, so a rerun only does what is missing."""
    did_work = False
    if not transcript_exists(paths):
        write_transcript(video, paths, toolkit, settings.language, hotwords, sink, pace)
        did_work = True
    if settings.with_frames and not frames_exist(paths):
        write_frames(video, paths, toolkit, sink, pace)
        did_work = True
    sink.report(ProgressEvent(Stage.DONE, video.name, 1.0))
    return did_work
