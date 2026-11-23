from erudio_transcriber.core.slide_selection import drop_duplicates, frame_second, merge_changes


def test_merge_changes_keeps_the_last_change_of_each_burst() -> None:
    assert merge_changes([3, 4, 5, 20], step=2.0, merge_seconds=6.0) == (0, 5, 20)


def test_merge_changes_without_changes_keeps_only_the_first_sample() -> None:
    assert merge_changes([], step=2.0, merge_seconds=6.0) == (0,)


def test_drop_duplicates_compares_with_the_last_kept_sample() -> None:
    distances = {(5, 0): 1.0, (9, 0): 50.0, (12, 9): 2.0}
    kept = drop_duplicates([0, 5, 9, 12], lambda a, b: distances[(a, b)], limit=6.0)
    assert kept == (0, 9)


def test_frame_second_is_one_second_after_the_change_except_for_the_first() -> None:
    assert frame_second(0, 2.0) == 0
    assert frame_second(5, 2.0) == 11
