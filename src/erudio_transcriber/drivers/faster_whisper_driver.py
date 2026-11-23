import os
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from erudio_transcriber.domain.transcript import Segment, Transcript
from erudio_transcriber.ports.transcriber import SegmentListener
from erudio_transcriber.registry import Options


def register_cuda_libraries() -> None:
    """pip-installed cuBLAS and cuDNN sit in site-packages/nvidia/*/bin, off the DLL path."""
    for entry in sys.path:
        for folder in Path(entry, "nvidia").glob("*/bin"):
            os.add_dll_directory(str(folder))
            os.environ["PATH"] = f"{folder}{os.pathsep}{os.environ['PATH']}"


@lru_cache(maxsize=2)
def load_model(name: str, device: str, compute_type: str) -> Any:
    register_cuda_libraries()
    from faster_whisper import WhisperModel

    return WhisperModel(name, device=device, compute_type=compute_type)


@dataclass(frozen=True, slots=True)
class FasterWhisperTranscriber:
    model_name: str = "large-v3"
    device: str = "cuda"
    compute_type: str = "int8"

    def transcribe(
        self, audio: Path, language: str, hotwords: str | None, listener: SegmentListener
    ) -> Transcript:
        model = load_model(self.model_name, self.device, self.compute_type)
        raw_segments, info = model.transcribe(
            str(audio),
            language=language,
            vad_filter=True,
            beam_size=5,
            condition_on_previous_text=False,
            hotwords=hotwords,
        )
        segments: list[Segment] = []
        for raw in raw_segments:
            segment = Segment(raw.start, raw.end, raw.text.strip())
            segments.append(segment)
            listener(segment, info.duration)
        return Transcript(tuple(segments), info.duration, language)


def create_transcriber(options: Options) -> FasterWhisperTranscriber:
    return FasterWhisperTranscriber(
        model_name=options.get("model", "large-v3"),
        device=options.get("device", "cuda"),
        compute_type=options.get("compute_type", "int8"),
    )
