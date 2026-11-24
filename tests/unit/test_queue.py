import threading
from pathlib import Path

from erudio_transcriber.application.queue import QueueRequest, run_queue
from erudio_transcriber.application.thermal_gate import ThermalGate
from erudio_transcriber.application.toolkit import JobSettings, Toolkit
from erudio_transcriber.domain.progress import ProgressEvent
from erudio_transcriber.domain.thermal import ThermalLimits, ThermalReading
from erudio_transcriber.domain.transcript import Segment, Transcript
from erudio_transcriber.ports.transcriber import SegmentListener


class FakeTranscriber:
    def __init__(self, fail_on: str | None = None) -> None:
        self.hotwords_seen: list[str | None] = []
        self.fail_on = fail_on

    def transcribe(
        self, audio: Path, language: str, hotwords: str | None, listener: SegmentListener
    ) -> Transcript:
        if self.fail_on and self.fail_on in audio.name:
            msg = "boom"
            raise RuntimeError(msg)
        self.hotwords_seen.append(hotwords)
        segment = Segment(0.0, 2.0, "hello")
        listener(segment, 2.0)
        return Transcript((segment,), 2.0, language)


class FakeAudio:
    def extract(self, video: Path, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"mp3")
        return destination


class FakeSlides:
    def detect(self, video: Path) -> list[float]:
        return [0.0, 11.0]


class FakeFrames:
    def extract(self, video: Path, seconds: float, destination: Path) -> bool:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"jpg")
        return True


class CoolSensor:
    def read(self) -> ThermalReading:
        return ThermalReading(gpu_celsius=50, cpu_celsius=None)


class SilentSink:
    def report(self, event: ProgressEvent) -> None:
        return None


def build(transcriber: FakeTranscriber) -> tuple[Toolkit, ThermalGate]:
    toolkit = Toolkit(transcriber, FakeAudio(), FakeSlides(), FakeFrames(), CoolSensor())
    gate = ThermalGate(CoolSensor(), ThermalLimits(), SilentSink(), threading.Event())
    return toolkit, gate


def make_course(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "source"
    (source / "module").mkdir(parents=True)
    (source / "module" / "a.mp4").write_bytes(b"x")
    (source / "module" / "b.mp4").write_bytes(b"x")
    return source, tmp_path / "out"


def test_queue_writes_every_output_and_a_rerun_skips_everything(tmp_path: Path) -> None:
    source, output = make_course(tmp_path)
    toolkit, gate = build(FakeTranscriber())
    request = QueueRequest(source, output, JobSettings())
    first = run_queue(request, toolkit, gate, SilentSink())
    assert (first.processed, first.skipped, first.failed) == (2, 0, ())
    folder = output / "module"
    assert (folder / "a.txt").read_text(encoding="utf-8") == "hello\n"
    assert (folder / "a.frames" / ".done").is_file()
    assert (folder / "a.frames" / "00-00-11.jpg").is_file()
    second = run_queue(request, toolkit, gate, SilentSink())
    assert (second.processed, second.skipped) == (0, 2)


def test_queue_keeps_going_after_a_failed_video(tmp_path: Path) -> None:
    source, output = make_course(tmp_path)
    toolkit, gate = build(FakeTranscriber(fail_on="a."))
    summary = run_queue(QueueRequest(source, output, JobSettings()), toolkit, gate, SilentSink())
    assert summary.failed == ("a.mp4",)
    assert summary.processed == 1


def test_queue_passes_the_vocabulary_as_hotwords(tmp_path: Path) -> None:
    source, output = make_course(tmp_path)
    output.mkdir()
    (output / "vocab.txt").write_text("# terms\nTinder\nAmyr Klink\n", encoding="utf-8")
    transcriber = FakeTranscriber()
    toolkit, gate = build(transcriber)
    request = QueueRequest(source, output, JobSettings(with_frames=False))
    run_queue(request, toolkit, gate, SilentSink())
    assert transcriber.hotwords_seen == ["Tinder, Amyr Klink", "Tinder, Amyr Klink"]


def test_queue_reports_cancellation(tmp_path: Path) -> None:
    source, output = make_course(tmp_path)
    toolkit, _ = build(FakeTranscriber())
    stop = threading.Event()
    stop.set()
    gate = ThermalGate(CoolSensor(), ThermalLimits(), SilentSink(), stop)
    summary = run_queue(QueueRequest(source, output, JobSettings()), toolkit, gate, SilentSink())
    assert summary.cancelled is True
