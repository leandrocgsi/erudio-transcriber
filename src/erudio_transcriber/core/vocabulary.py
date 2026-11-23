from pathlib import Path

HOTWORD_BUDGET = 600
SEPARATOR = ", "


def read_terms(path: Path) -> tuple[str, ...]:
    lines = (line.strip() for line in path.read_text(encoding="utf-8").splitlines())
    return tuple(line for line in lines if line and not line.startswith("#"))


def hotwords(terms: tuple[str, ...], budget: int = HOTWORD_BUDGET) -> str | None:
    """Whisper reads only about 223 tokens of hotwords per window, so the best terms go first."""
    chosen: list[str] = []
    used = 0
    for term in terms:
        cost = len(term) + (len(SEPARATOR) if chosen else 0)
        if used + cost > budget:
            break
        chosen.append(term)
        used += cost
    return SEPARATOR.join(chosen) or None
