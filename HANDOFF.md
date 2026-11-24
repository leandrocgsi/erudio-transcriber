# HANDOFF

Context for a new Claude Code session that continues this project. Read `CLAUDE.md` first (architecture,
rules, commands, decisions, next steps); this file holds what `CLAUDE.md` does not: where the project came
from, how the author likes to work, what was verified and what already went wrong. Delete it when it stops
being useful.

## Where this came from
- The author turned several Brazilian video courses into Claude Code skills. The reusable pipeline lives in
  the plugin `D:\Code\- CourseSkills\erudio-tools` (skills `course-to-skills`, `course-transcribe`,
  `course-frames`, `course-skill-writer`, `video-transcribe-frames`). Its canonical scripts are in
  `D:\Code\- CourseSkills\erudio-tools\scripts-src` and are the behavioral reference for this app.
- The "Breno job" (15 webinar videos transcribed with a vocabulary and slide-change frames) was run with
  those scripts and finished: results are in `D:\Code\- CourseSkills\breno` (`vocab.txt` there is a good
  example of a hand-curated vocabulary; `PIPELINE.md` records the run).
- The author liked how accurate local Whisper was with hotwords and asked for a personal desktop app over
  the same pipeline. This repo is that app. It started from a conversation about architecture, then an MVP.
- The author's Python style comes from their skills in `D:\Code\- Skills\erudio-skills\erudio-python`
  (`code-style`, `code-organization`, `project-claude-md`, `uv-config`). Read `code-style` and
  `code-organization` before writing code; the rules are summarized in `CLAUDE.md`.

## How the author likes to work
- Answers and discussion in Brazilian Portuguese; code, identifiers, docs and commit messages in English.
- "Na dúvida, me pergunte": ask (AskUserQuestion) for real decisions, otherwise pick the sensible default and
  say so. Do not ask for things you can check.
- Never commit or push unless asked. When asked for a commit message, produce only the command, in the
  `erudio-git:commit-message` format (Conventional Commits subject, bullet body wrapped near 72 columns,
  `git add -A &&` only for the very first commit, no AI attribution trailer).
- Code must look like theirs: no comments, one-line docstrings only for a "why", fully typed, small modules,
  no `Impl`/`Manager`/`Helper`/`Util`, frozen slotted dataclasses, `StrEnum`.
- Components must be easy to replace: other platforms and engines are meant to arrive as drivers from the
  community.
- Scripts and tools must travel with what uses them (portable to another machine).
- Hardware care: the machine is a GTX 1070 Ti laptop-class setup that should stay a few degrees below its
  limits. Keep the thermal pause at 78 C and resume at 72 C by default. When running real transcriptions in
  tests, use short clips.
- Originals are read-only. Never write into the Dropbox source folders; derived files go in a separate
  output folder.

## Environment facts
- Windows 10, Git Bash and PowerShell. Global Python 3.11 has faster-whisper, numpy and the pip CUDA DLLs
  (`site-packages/nvidia/*/bin`); Python 3.13 and a uv-managed 3.14 also exist but lack those packages.
  The project venv is created with `--system-site-packages` to reuse the 3.11 ones.
- ffmpeg comes from winget (`...\WinGet\Packages\Gyan.FFmpeg...\bin\ffmpeg.exe`); `uv` is not on the Git
  Bash `PATH`.
- Whisper large-v3 int8 on the GPU runs at roughly 5x real time; a 90 s clip took about 51 s including the
  model load.

## What was verified (and how to check it again)
- `python -m pytest --cov`, `ruff check`, `ruff format --check`, `mypy` all pass (46 tests, 94.8% coverage).
- End to end on a real clip: cut 90 s from a course video into a scratch folder with
  `ffmpeg -ss 60 -t 90 -i VIDEO -c copy clip.mp4`, run `erudio-transcriber SRC OUT`, check mp3/srt/txt/frames,
  run it again and confirm it reports everything as already done.
- The GUI was run headless (`QT_QPA_PLATFORM=offscreen`): fill the two paths, click Start, wait for the worker
  to finish, read the status label. It was not looked at on a real screen yet.
- Not verified: `pip install -e ".[whisper,qt]"` on a clean machine; pausing on a real hot GPU (the pause
  logic is unit-tested with a scripted sensor).

## Pitfalls already hit
- In the Bash tool, a long command with several heredocs and mixed quotes fails with "unexpected EOF"; write
  files with the file tool instead. The file tool refuses to overwrite a file that was not read first.
- ffmpeg inside a shell loop swallows stdin: always pass `stdin=subprocess.DEVNULL` (already done in the
  drivers).
- The legacy `run_queue.sh` reported every video as failed because `COURSE_SRC` was not exported even though
  the transcripts were fine; the new app has no such environment-variable dependency.
- A slide change detected in the last second of a video points past its end; the frame extractor backs off
  up to 3 s and the queue only logs a warning.
- Never derive `ffprobe` from the ffmpeg path with `str.replace` (an upper-case `.EXE` turns it into ffmpeg
  itself).
- When stopping background jobs, kill the parent loops first and then their children, otherwise the children
  are respawned.
- Python 3.11 rejects `type X = ...` (PEP 695); the project uses `X: TypeAlias = ...` until it moves to 3.12+.

## Open points for the author
- No license chosen yet (needed if the project is opened to the community).
- The venv depends on the global Python 3.11 packages; decide whether to move to a self-contained
  environment (and to uv) or to Python 3.12+.
- User-facing language of the GUI is English; Portuguese could be added later.
- The first commit is not made yet (a command was generated; the author runs it).

## Suggested first message in the new session
```
Read CLAUDE.md and HANDOFF.md in this repo, run the test and lint commands to confirm the environment, and
then start with the first item of "Next steps": port the vocabulary builder from
D:\Code\- CourseSkills\erudio-tools\scripts-src\build_vocab.py behind a VocabularySource port, following the
code style rules. Ask me before any decision that is not covered in those files.
```
