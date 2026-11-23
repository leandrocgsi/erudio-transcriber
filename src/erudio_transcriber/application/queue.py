import logging
from dataclasses import dataclass
from pathlib import Path

from erudio_transcriber.application.thermal_gate import ThermalGate
from erudio_transcriber.application.toolkit import JobSettings, Toolkit
from erudio_transcriber.application.video_job import process_video
from erudio_transcriber.application.vocabulary_lookup import find_vocabulary, hotwords_for
from erudio_transcriber.core.layout import output_paths
from erudio_transcriber.core.media_files import find_videos
from erudio_transcriber.domain.errors import JobCancelledError
from erudio_transcriber.domain.progress import ProgressEvent, Stage
from erudio_transcriber.ports.progress_sink import ProgressSink

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class QueueRequest:
    source: Path
    output: Path
    settings: JobSettings
    vocabulary: Path | None = None


@dataclass(frozen=True, slots=True)
class QueueSummary:
    processed: int
    skipped: int
    failed: tuple[str, ...]
    cancelled: bool


def source_root(source: Path) -> Path:
    return source.parent if source.is_file() else source


def run_queue(
    request: QueueRequest, toolkit: Toolkit, gate: ThermalGate, sink: ProgressSink
) -> QueueSummary:
    root = source_root(request.source)
    processed, skipped = 0, 0
    failed: list[str] = []
    for video in find_videos(request.source):
        paths = output_paths(video, root, request.output)
        vocabulary = find_vocabulary(paths.txt.parent, request.output, request.vocabulary)
        try:
            gate()
            did_work = process_video(
                video, paths, toolkit, request.settings, hotwords_for(vocabulary), sink, gate
            )
        except JobCancelledError:
            return QueueSummary(processed, skipped, tuple(failed), cancelled=True)
        except Exception as error:
            logger.exception("Failed: %s", video.name)
            failed.append(video.name)
            sink.report(ProgressEvent(Stage.FAILED, video.name, detail=str(error)))
            continue
        processed, skipped = (processed + 1, skipped) if did_work else (processed, skipped + 1)
    return QueueSummary(processed, skipped, tuple(failed), cancelled=False)
