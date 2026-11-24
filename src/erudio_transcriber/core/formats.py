from collections.abc import Sequence

from erudio_transcriber.domain.transcript import Segment

MILLISECONDS_PER_SECOND = 1000
SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60


def _split(seconds: float) -> tuple[int, int, int, int]:
    total = round(seconds * MILLISECONDS_PER_SECOND)
    total_seconds, milliseconds = divmod(total, MILLISECONDS_PER_SECOND)
    total_minutes, secs = divmod(total_seconds, SECONDS_PER_MINUTE)
    hours, minutes = divmod(total_minutes, MINUTES_PER_HOUR)
    return hours, minutes, secs, milliseconds


def clock(seconds: float) -> str:
    hours, minutes, secs, _ = _split(seconds)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def srt_timestamp(seconds: float) -> str:
    hours, minutes, secs, milliseconds = _split(seconds)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def render_srt(segments: Sequence[Segment]) -> str:
    blocks = [
        f"{index}\n{srt_timestamp(segment.start)} --> {srt_timestamp(segment.end)}\n"
        f"{segment.text}\n"
        for index, segment in enumerate(segments, start=1)
    ]
    return "\n".join(blocks)


def render_txt(segments: Sequence[Segment]) -> str:
    return "".join(f"{segment.text}\n" for segment in segments)
