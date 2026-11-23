from pathlib import Path

from erudio_transcriber.core.layout import mirror, output_paths


def test_mirror_keeps_the_relative_tree_under_the_output_root() -> None:
    source = Path("/src/course/module/lesson.mp4")
    assert mirror(source, Path("/src"), Path("/out")) == Path("/out/course/module/lesson.mp4")


def test_output_paths_sit_in_the_mirrored_folder_without_double_extensions() -> None:
    paths = output_paths(Path("/src/module/lesson.mp4.mp4"), Path("/src"), Path("/out"))
    assert paths.audio == Path("/out/module/lesson.mp3")
    assert paths.srt == Path("/out/module/lesson.srt")
    assert paths.txt == Path("/out/module/lesson.txt")
    assert paths.frames == Path("/out/module/lesson.frames")
