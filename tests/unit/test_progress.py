from erudio_transcriber.domain.progress import ProgressEvent, Stage


def test_progress_event_defaults_to_no_fraction_and_no_detail() -> None:
    event = ProgressEvent(Stage.AUDIO, "lesson.mp4")
    assert event.fraction is None
    assert event.detail == ""
