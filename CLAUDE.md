# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview
`erudio-transcriber` is a personal desktop tool (PySide6 interface planned) that turns a folder of videos
into mp3, srt, txt and slide-change frames, running faster-whisper locally on the user's GPU. A
`vocab.txt` is sent to Whisper as hotwords; a thermal guard pauses the job when the machine runs hot.
Python >= 3.11 (the machine has 3.11; PySide6 and ctranslate2 wheels are the reason not to require 3.14),
package `erudio_transcriber` under `src/`, hatchling build, no runtime dependencies in the core.

It is a rewrite of the scripts in `D:\Code\- CourseSkills\erudio-tools\scripts-src` (`transcribe.py`,
`slide_frames.py`, `build_vocab.py`, `thermal_guard.ps1`, `run_queue.sh`). Those scripts are the behavioral
reference; do not import them.

## Commands
Verified on Windows with the project venv (uv is not installed on this machine; with uv, `uv sync` and
prefix with `uv run`).
```bash
python -m venv .venv
python -m venv --system-site-packages .venv   # reuses the global faster-whisper and CUDA DLLs (Python 3.11)
.venv/Scripts/python -m pip install -e . pytest pytest-cov ruff mypy PySide6   # install
.venv/Scripts/erudio-transcriber.exe SOURCE OUTPUT --language pt   # CLI; --no-frames, --vocabulary FILE
.venv/Scripts/erudio-transcriber-gui.exe                           # GUI (PySide6)
.venv/Scripts/python -m pytest --cov                                    # tests + coverage gate (90%)
.venv/Scripts/python -m pytest tests/unit/test_formats.py::test_clock_rounds_to_whole_seconds   # one test
.venv/Scripts/python -m ruff check && .venv/Scripts/python -m ruff format --check
.venv/Scripts/python -m mypy                                            # strict
```

## Architecture
Ports and drivers, so the community can add platforms and engines without touching the core.
- `domain/`: frozen, slotted dataclasses and `StrEnum`s only (`Segment`, `Transcript`, `ThermalReading`,
  `ThermalLimits`, `ThermalAction`, `ProgressEvent`, `Stage`). No I/O, no imports from the other layers.
- `ports/`: one small `Protocol` per file, one method each (`Transcriber`, `AudioExtractor`,
  `SlideDetector`, `FrameExtractor`, `ThermalSensor`, `ProgressSink`). A port never exposes a vendor type.
- `core/`: pure functions over domain types and ports (`formats`, `layout`, `vocabulary`,
  `thermal_policy`). Anything that decides something lives here, so it is testable without a GPU.
- `registry.py`: drivers are discovered through entry points, one group per port (`DriverGroup`);
  each entry point is a zero-argument factory returning the driver.
- `drivers/`: the built-in adapters, registered as entry points in `pyproject.toml`: `faster_whisper_driver`,
  `ffmpeg_audio`, `ffmpeg_frames`, `ffmpeg_slides` (numpy), `ffmpeg_locator`, `nvidia_smi`. Each exposes a
  `create_*(options)` factory taking a string mapping.
- `application/`: `toolkit.py` (the ports bundled), `steps.py` (transcript and frames steps, skip-if-done),
  `video_job.py` (one video), `queue.py` (the resumable queue, failures do not stop it), `thermal_gate.py`
  (blocks while hot, raises `JobCancelledError` on stop), `vocabulary_lookup.py`.
- `composition.py`: the only place that turns driver names into a `Toolkit`; `cli.py` and `ui/qt/` call it.
- `ui/qt/`: PySide6 adapter, the only package that imports Qt. One small widget per file (`path_picker`,
  `settings_panel`, `progress_panel`), `worker.py` runs the queue in a `QThread`, `sink.py` turns progress
  events into a Qt signal, `window.py` only assembles them.

A new technology is a new driver package, never a branch inside the core. Core code never imports
`faster_whisper`, `subprocess` wrappers for ffmpeg, `PySide6` or a vendor tool.

## Status (MVP)
Works end to end on the author's machine (GTX 1070 Ti, Windows, ffmpeg from winget): CLI and GUI transcribe a
folder, write mp3/srt/txt/frames, resume on rerun, use `vocab.txt` if present and pause on temperature.
Verified with a real 90 s clip (51 s on the GPU) and a headless GUI run. Not done yet: building `vocab.txt`
from documents (`build_vocab.py` is not ported; today the file is read, never created), the vocabulary
review screen, the "manual or from frames?" question, CPU temperature (only the GPU is read), a frame
preview, a Linux/macOS sensor and packaging into an exe (model and CUDA DLLs would stay outside it).

## Rules for new code
- Small modules and small functions; a module has one reason to change. No class that grows past one
  responsibility: split it into a function module plus a small dataclass instead of adding methods.
- No Java accent: no `Interface`/`Impl` pairs (a `Protocol` appears only because drivers really vary), no
  getters/setters, no classes that only group functions, no `Manager`/`Helper`/`Util` names, no factories
  named after the class they build. A plain class is for real mutable state only.
- Behavior that must be replaceable gets a port; behavior that is a pure decision gets a function.
- Dependencies go inward: `domain` <- `core`/`ports` <- drivers/application <- `ui`. Never the reverse.
- Every signature is typed; `mypy --strict` is the bar. `match`/`case` over class hierarchies, `StrEnum`
  for fixed value sets, `@dataclass(frozen=True, slots=True)` for values. Aliases use `X: TypeAlias = ...`
  for now, because the venv is Python 3.11; switch to the PEP 695 `type X = ...` when the project moves to
  3.12+.
- No comments. A one-line docstring only to record a *why* the signature cannot show (see
  `core/vocabulary.py`). No module docstrings, no `Args:`/`Returns:` sections.
- Every `raise` inside an `except` carries `from error`; a message longer than a couple of words is built
  in a local `msg` first. `logging.getLogger(__name__)` with `%s` placeholders.
- Blocking work never runs on the Qt GUI thread; the interface only talks to the application layer through
  `ProgressSink` and a worker.
- 100-column lines; ruff format and check, mypy strict, no per-file carve-outs beyond `pyproject.toml`.
- A driver ships with its own tests; core and pure functions are tested without Whisper, ffmpeg or a GPU.
  The ffmpeg drivers are tested against a synthetic video (skipped when ffmpeg is missing). The coverage
  gate omits `ports/` (protocol stubs), `ui/` and `faster_whisper_driver.py`; the last two are checked by
  running the app (a headless GUI run and a real transcription), not by unit tests.

## Decisions already made by the author
- Personal use first (no installer or licensing concerns), but the code is meant to be extended by the
  community: new platforms and engines arrive as drivers, small components, no giant classes.
- UI is PySide6. The package lives at `D:\Code\Python\erudio-transcriber`; the repo has no commits yet and
  nothing is pushed. Never commit or push without being asked; when asked, only produce the command.
- Vocabulary has two layers. The app uses `vocab.txt` when it exists and does not ask. When it does not,
  it builds one from the documents next to the videos; only if that yields too little does it ask "provide
  it manually, or derive it from video frames?". A better dictionary can be curated beforehand outside the
  app (for example with Claude Code and the `erudio-tools` `course-transcribe` skill); the app only
  consumes the `vocab.txt`, and a plain exe is not expected to curate well on its own.
- No API calls: everything runs locally.

## Next steps, in order
1. Port `build_vocab.py` (sources: PDFs, txt/md/docx/xlsx, folder names) as a driver or core module behind a
   `VocabularySource` port, then the review screen (show the terms, edit, save `vocab.txt`).
2. The "manual or from frames?" question in the GUI and CLI, with frames as the last resort.
3. CPU temperature sensor (the old guard read the ACPI thermal zone) and a Linux/macOS sensor driver.
4. Frame preview, then packaging (PyInstaller; keep the Whisper model and CUDA DLLs outside the exe).
5. Move to Python 3.12+ and the PEP 695 `type` aliases when the faster-whisper and PySide6 wheels allow it.

Reference implementation of everything above: `D:\Code\- CourseSkills\erudio-tools\scripts-src`
(`build_vocab.py`, `thermal_guard.ps1`, `transcribe.py`, `slide_frames.py`) and its skills' docs.

## Behavior to preserve from the scripts
- Whisper: large-v3, GPU int8, `vad_filter`, `beam_size=5`, `condition_on_previous_text=False`, `hotwords`
  taken from `vocab.txt` (best terms first, about 600 characters).
- Output mirrors the source tree under the output root; the source folder is read-only. The `.txt` is
  written last and acts as the completion marker; mp3 goes through a `.part` file and an atomic rename.
- Outputs are `<name>.mp3`, `<name>.srt`, `<name>.txt` (lines `[HH:MM:SS] text`), no `.transcricao` suffix,
  and `<name>.frames/` with a `.done` marker.
- Slide frames: sample every 2 s, mean absolute difference over 128x72 gray frames above 12, merge changes
  closer than 6 s, take the frame about 1 s after the change, drop near-duplicates, always keep the first
  frame, and back off a few seconds when the change falls past the end of the video.
- Vocabulary: use `vocab.txt` if it exists without asking; otherwise build it from the documents next to
  the videos; only when there are not enough terms, ask the user whether to provide it manually or to derive
  it from video frames. Never use frames without that answer.
- Thermal guard: pause at 78 C, resume at 72 C (hysteresis); the machine's own limits are higher, the
  margin is deliberate.

## Dependency versions
Resolve the latest stable version at install time and pin only a floor (`>=`); never copy versions from
another project. Heavy dependencies are optional extras (`whisper`, `qt`) so the core stays installable
and testable on its own.

## Erudio preferences
- Comments in generated code: no
- User-facing text language: English
- Package manager: uv (not installed on this machine yet; the venv commands above are what was verified)
