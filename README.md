# erudio-transcriber

Turn a folder of videos into searchable text, entirely on your own machine.

For every video it produces an `mp3`, an `srt` and a `txt` transcript (Whisper, running on your GPU) and a
set of frames taken **only when the slide changes**. A vocabulary file with names and jargon is handed to
Whisper as hotwords, so terms it would normally get wrong come out right. A thermal guard pauses the job
when the GPU gets too hot, and a rerun picks up exactly where the previous run stopped.

Nothing is uploaded anywhere: no API keys, no cloud.

## Features
- **Local transcription** with [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (`large-v3`,
  VAD filter, int8 on CUDA by default).
- **Vocabulary hints**: a `vocab.txt` is sent to Whisper as hotwords on every window.
- **Slide-change frames**: frames are kept only when the picture changes (and always the first one), not at a
  fixed interval.
- **Resumable queue**: each step skips what already exists; a failed video does not stop the others.
- **Thermal guard**: pauses when the GPU reaches the upper limit and resumes only after it cools below the
  lower one (defaults 78 C and 72 C).
- **Read-only sources**: the original folder is never written to; its tree is mirrored in the output folder.
- **Command line and desktop window** (PySide6) on top of the same core.
- **Pluggable**: every outside technology sits behind a small port, so other engines and platforms can be
  added as drivers without touching the core.

## Status
Early MVP. It runs on Windows with an NVIDIA GPU and ffmpeg. See [Roadmap](#roadmap) for what is still
missing, notably building the vocabulary automatically and packaging an executable.

## Requirements
- Python 3.11 or newer
- [ffmpeg](https://ffmpeg.org/) on `PATH` (Windows: `winget install Gyan.FFmpeg`, also found automatically)
- An NVIDIA GPU with recent drivers for the default setup (`nvidia-smi` is used to read the temperature)

## Install
```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[whisper,qt]"
```
The `whisper` extra installs faster-whisper and the CUDA libraries it needs (cuBLAS and cuDNN); the `qt`
extra installs PySide6 for the window. The core itself only depends on numpy.

## Usage
```bash
erudio-transcriber SOURCE OUTPUT --language pt      # command line
erudio-transcriber-gui                              # desktop window
```

`SOURCE` is a video or a folder of videos (searched recursively, `.mp4 .mkv .mov .webm .ts`) and is only
read. `OUTPUT` receives the results in the same folder tree.

| Option | Default | Meaning |
|---|---|---|
| `--language` | `pt` | Spoken language passed to Whisper |
| `--model` | `large-v3` | Whisper model name |
| `--device` | `cuda` | `cuda` or `cpu` |
| `--no-frames` | off | Skip the slide-change frames |
| `--vocabulary FILE` | none | Use this vocabulary file instead of looking for `vocab.txt` |
| `--pause-at` | `78` | Pause when the GPU reaches this temperature (C) |
| `--resume-at` | `72` | Resume once it is at or below this temperature (C) |

### Output
```
OUTPUT/
  vocab.txt                  optional, project-wide vocabulary
  <same folders as SOURCE>/
    lesson.mp3               mono 16 kHz audio
    lesson.srt               subtitles
    lesson.txt               lines like "[00:01:23] text", written last (completion marker)
    lesson.frames/           slide-change frames named HH-MM-SS.jpg, plus a .done marker
```
A video is considered finished when its `txt` and `srt` exist (and, with frames enabled, the `.done`
marker is inside its `.frames` folder). Running the same command again only does what is missing.

### Vocabulary
Put a `vocab.txt` in the folder of a video's output (module level) or in the root of `OUTPUT`; the closest
one wins, and `--vocabulary` overrides both. One term per line, best terms first, `#` starts a comment:

```
# names, brands and jargon Whisper tends to get wrong
Amyr Klink
Tinder
```
Whisper reads only about 223 tokens of hotwords per window, so the first ~600 characters are used: put the
most distinctive terms at the top. The app does not create this file yet.

## How it is organized
Ports and drivers (hexagonal). Dependencies point inward: `domain` <- `core` / `ports` <- `drivers` /
`application` <- `ui`.

| Package | Role |
|---|---|
| `domain/` | Immutable data (`Segment`, `Transcript`, `ThermalReading`, `ProgressEvent`, ...). No I/O |
| `ports/` | One small `Protocol` per capability: `Transcriber`, `AudioExtractor`, `SlideDetector`, `FrameExtractor`, `ThermalSensor`, `ProgressSink` |
| `core/` | Pure functions: srt/txt rendering, output layout, vocabulary, slide selection, thermal decision |
| `drivers/` | Built-in adapters: faster-whisper, ffmpeg (audio, frames, slides), nvidia-smi |
| `application/` | Per-video job, resumable queue, thermal gate |
| `ui/qt/` | PySide6 window; the only package that imports Qt |
| `composition.py` | Turns driver names into a `Toolkit`; used by the CLI and the window |

## Writing a driver
Want another engine (a different Whisper runtime, an AMD or macOS temperature sensor, ...)? Implement the
port and register it; the core does not change.

1. Pick the port in `src/erudio_transcriber/ports/` you want to implement.
2. Implement it in your own package, with a factory `create(options)` that takes a mapping of strings and
   returns the driver.
3. Register the factory as an entry point in the matching group (`erudio_transcriber.transcribers`,
   `.audio_extractors`, `.slide_detectors`, `.frame_extractors`, `.thermal_sensors`):

```toml
[project.entry-points."erudio_transcriber.thermal_sensors"]
macos = "my_package.sensor:create_sensor"
```

`erudio_transcriber.composition.build_toolkit` accepts driver names, so a registered driver can replace a
built-in one.

## Development
```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[whisper,qt]" pytest pytest-cov ruff mypy
.venv/Scripts/python -m pytest --cov                                  # tests, 90% coverage gate
.venv/Scripts/python -m ruff check && .venv/Scripts/python -m ruff format --check
.venv/Scripts/python -m mypy                                          # strict
```
With uv: `uv sync` and prefix the same commands with `uv run`.

The ffmpeg drivers are tested against a small synthetic video (skipped when ffmpeg is missing). The GUI
and the Whisper driver are checked by running the app, not by unit tests.

## Roadmap
- [ ] Build `vocab.txt` from the documents next to the videos (PDF, txt, md, docx, xlsx), with a review
      screen, and ask whether to provide it manually or derive it from video frames when there is too little
      material
- [ ] CPU temperature and sensors for Linux and macOS
- [ ] Frame preview in the window
- [ ] Packaging as an executable (the Whisper model and CUDA libraries would stay outside it)
- [ ] Python 3.12+ and PEP 695 type aliases

## Contributing
Keep modules small and single-purpose, add a port when behavior must be replaceable, keep decisions in
pure functions, and cover new code with tests that do not need a GPU. Run the checks listed under
[Development](#development) before sending a change.
