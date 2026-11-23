from pathlib import Path

VIDEO_EXTENSIONS = frozenset({".mp4", ".mkv", ".mov", ".webm", ".ts"})


def find_videos(target: Path) -> tuple[Path, ...]:
    if target.is_file():
        return (target,)
    found = (path for path in target.rglob("*") if path.suffix.lower() in VIDEO_EXTENSIONS)
    return tuple(sorted(path for path in found if path.is_file()))


def clean_stem(path: Path) -> str:
    """Some downloads end in 'lesson.mp4.mp4'; the outputs should not inherit that."""
    name = path.name
    stripped = True
    while stripped:
        stripped = False
        for extension in VIDEO_EXTENSIONS:
            if name.lower().endswith(extension) and len(name) > len(extension):
                name = name[: -len(extension)]
                stripped = True
    return name
