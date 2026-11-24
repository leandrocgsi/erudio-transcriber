from erudio_transcriber.core.formats import clock, render_srt, render_txt, srt_timestamp
from erudio_transcriber.domain.transcript import Segment

SEGMENTS = (Segment(0.0, 2.5, "Hello"), Segment(3661.25, 3665.0, "World"))


def test_clock_rounds_to_whole_seconds() -> None:
    assert clock(3661.4) == "01:01:01"


def test_srt_timestamp_keeps_milliseconds() -> None:
    assert srt_timestamp(3661.25) == "01:01:01,250"


def test_render_srt_numbers_blocks_from_one() -> None:
    expected = (
        "1\n00:00:00,000 --> 00:00:02,500\nHello\n\n2\n01:01:01,250 --> 01:01:05,000\nWorld\n"
    )
    assert render_srt(SEGMENTS) == expected


def test_render_txt_has_one_line_per_segment_without_timestamps() -> None:
    assert render_txt(SEGMENTS) == "Hello\nWorld\n"
