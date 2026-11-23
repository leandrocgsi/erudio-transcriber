from pathlib import Path

from erudio_transcriber.core.media_files import clean_stem, find_videos


def test_find_videos_returns_only_videos_sorted(tmp_path: Path) -> None:
    (tmp_path / "b.mp4").write_bytes(b"x")
    (tmp_path / "a.MKV").write_bytes(b"x")
    (tmp_path / "notes.txt").write_text("x")
    assert find_videos(tmp_path) == (tmp_path / "a.MKV", tmp_path / "b.mp4")


def test_find_videos_accepts_a_single_file(tmp_path: Path) -> None:
    video = tmp_path / "one.mp4"
    video.write_bytes(b"x")
    assert find_videos(video) == (video,)


def test_clean_stem_strips_repeated_video_extensions() -> None:
    assert clean_stem(Path("Lesson 01.mp4.mp4")) == "Lesson 01"
    assert clean_stem(Path("plain.mp4")) == "plain"
