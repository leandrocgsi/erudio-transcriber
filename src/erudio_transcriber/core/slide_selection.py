from collections.abc import Callable, Sequence
from typing import TypeAlias

Distance: TypeAlias = Callable[[int, int], float]


def merge_changes(changes: Sequence[int], step: float, merge_seconds: float) -> tuple[int, ...]:
    """Keeps the last change of each burst, once it settles; sample 0 always stays."""
    groups: list[list[int]] = []
    for index in changes:
        if groups and (index - groups[-1][-1]) * step < merge_seconds:
            groups[-1].append(index)
        else:
            groups.append([index])
    return (0, *(group[-1] for group in groups))


def drop_duplicates(indices: Sequence[int], distance: Distance, limit: float) -> tuple[int, ...]:
    kept: list[int] = []
    for index in indices:
        if kept and distance(index, kept[-1]) <= limit:
            continue
        kept.append(index)
    return tuple(kept)


def frame_second(index: int, step: float) -> int:
    """About one second after the change; the first frame stays at the very start."""
    return int(index * step) + (1 if index > 0 else 0)
