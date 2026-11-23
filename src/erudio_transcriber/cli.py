import argparse
import logging
import sys
import threading
from collections.abc import Sequence
from pathlib import Path

from erudio_transcriber.application.queue import QueueRequest, QueueSummary, run_queue
from erudio_transcriber.application.toolkit import JobSettings
from erudio_transcriber.composition import build_gate, build_toolkit
from erudio_transcriber.domain.progress import ProgressEvent, Stage
from erudio_transcriber.domain.thermal import ThermalLimits


class ConsoleSink:
    def __init__(self) -> None:
        self.last_line = ""

    def report(self, event: ProgressEvent) -> None:
        percent = f"{event.fraction * 100:5.1f}%" if event.fraction is not None else "      "
        line = f"[{event.stage.value:13}] {percent} {event.item} {event.detail}".rstrip()
        if event.stage is Stage.TRANSCRIPTION:
            print(f"\r{line}", end="", flush=True)
        else:
            print(f"\n{line}" if self.last_line.startswith("[transcription") else line, flush=True)
        self.last_line = line


def parse(arguments: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="erudio-transcriber")
    parser.add_argument("source", type=Path, help="video file or folder (never written to)")
    parser.add_argument("output", type=Path, help="folder that receives mp3, srt, txt and frames")
    parser.add_argument("--language", default="pt")
    parser.add_argument("--model", default="large-v3")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--no-frames", action="store_true")
    parser.add_argument("--vocabulary", type=Path, default=None)
    parser.add_argument("--pause-at", type=int, default=78)
    parser.add_argument("--resume-at", type=int, default=72)
    return parser.parse_args(arguments)


def summarize(summary: QueueSummary) -> str:
    failed = f", failed: {', '.join(summary.failed)}" if summary.failed else ""
    state = "cancelled" if summary.cancelled else "finished"
    return f"{state}: {summary.processed} processed, {summary.skipped} already done{failed}"


def main(arguments: Sequence[str] | None = None) -> int:
    args = parse(sys.argv[1:] if arguments is None else arguments)
    logging.basicConfig(level=logging.WARNING)
    sink = ConsoleSink()
    toolkit = build_toolkit({"model": args.model, "device": args.device})
    gate = build_gate(
        toolkit, ThermalLimits(args.pause_at, args.resume_at), sink, threading.Event()
    )
    settings = JobSettings(language=args.language, with_frames=not args.no_frames)
    request = QueueRequest(args.source, args.output, settings, args.vocabulary)
    summary = run_queue(request, toolkit, gate, sink)
    print(f"\n{summarize(summary)}")
    return 1 if summary.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
