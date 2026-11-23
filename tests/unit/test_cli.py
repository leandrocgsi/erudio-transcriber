from pathlib import Path

import pytest

from erudio_transcriber.application.queue import QueueSummary
from erudio_transcriber.cli import ConsoleSink, parse, summarize
from erudio_transcriber.composition import build_toolkit
from erudio_transcriber.domain.progress import ProgressEvent, Stage


def test_parse_applies_the_defaults() -> None:
    args = parse(["in", "out"])
    assert args.source == Path("in")
    assert (args.language, args.model, args.device) == ("pt", "large-v3", "cuda")
    assert (args.pause_at, args.resume_at, args.no_frames) == (78, 72, False)


def test_parse_reads_the_options() -> None:
    args = parse(["in", "out", "--language", "en", "--no-frames", "--pause-at", "70"])
    assert (args.language, args.no_frames, args.pause_at) == ("en", True, 70)


def test_summarize_names_the_failed_videos() -> None:
    summary = QueueSummary(processed=2, skipped=1, failed=("a.mp4",), cancelled=False)
    assert summarize(summary) == "finished: 2 processed, 1 already done, failed: a.mp4"


def test_summarize_reports_cancellation() -> None:
    summary = QueueSummary(processed=0, skipped=0, failed=(), cancelled=True)
    assert summarize(summary).startswith("cancelled")


def test_console_sink_prints_progress_lines(capsys: pytest.CaptureFixture[str]) -> None:
    sink = ConsoleSink()
    sink.report(ProgressEvent(Stage.FRAMES, "a.mp4", 0.5))
    sink.report(ProgressEvent(Stage.DONE, "a.mp4", 1.0))
    output = capsys.readouterr().out
    assert "50.0% a.mp4" in output
    assert "[done" in output


def test_build_toolkit_wires_the_builtin_drivers() -> None:
    toolkit = build_toolkit({})
    assert type(toolkit.transcriber).__name__ == "FasterWhisperTranscriber"
    assert type(toolkit.sensor).__name__ == "NvidiaSmiSensor"
