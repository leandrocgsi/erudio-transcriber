import math
import re
from collections import Counter
from collections.abc import Iterable, Iterator

from erudio_transcriber.core.portuguese_words import COMMON, CONNECTORS, fold

WORD = re.compile(r"[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9+#.\-']*[A-Za-zÀ-ÿ0-9+#]|[A-Za-zÀ-ÿ0-9]")
URL = re.compile(r"(?:https?://|www\.)[^\s<>\"')\]]+", re.IGNORECASE)
EMAIL = re.compile(r"\S+@\S+")
LIST_MARK = re.compile(r"^\s*(?:\d{1,2}[.)]\s+|[-*•]\s+)")
ITEM_BREAK = re.compile(r"\s*[,;]\s*|\s+(?:e|and|ou)\s+(?=[A-Z])")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
CAMEL_CASE = re.compile(r"[a-z][A-Z]|[A-Z]{2}[a-z]|(?<![A-Za-z])[a-z]-[A-Z]")
LETTER_AND_DIGIT = re.compile(r"[A-Za-z]\d|\d[A-Za-z]")
ORDINAL = re.compile(r"^\d+[a-zº°]{0,2}$")
FOREIGN_SPELLING = re.compile(r"[kwy]|th|ck|ph|sh|tion|ight|ness|ment$|ing$")
DOMAIN_SUFFIXES = frozenset(
    "com org net br io co app jobs network dev tv eu de ca au nz uk gov edu ai me info us fr".split()
)
GENERIC_LABELS = frozenset({"jobs", "home", "web", "blog", "site", "page", "info", "online"})
FOREIGN_WEIGHT = 2
LIST_WEIGHT = 2
PHRASE_WEIGHT = 3
MIN_LIST_RUN = 3
MAX_PHRASE_TOKENS = 4


def is_technical(token: str) -> bool:
    if "+" in token or "#" in token or LETTER_AND_DIGIT.search(token):
        return not ORDINAL.match(token)
    if token.isalpha() and token.isupper():
        return 2 <= len(token) <= 6
    return bool(CAMEL_CASE.search(token))


def is_foreign(token: str) -> bool:
    key = fold(token)
    return len(key) >= 4 and key == token.lower() and bool(FOREIGN_SPELLING.search(key))


def has_evidence(token: str) -> bool:
    return fold(token) not in COMMON and (is_technical(token) or is_foreign(token))


def is_heading(tokens: list[str]) -> bool:
    letters = [token for token in tokens if any(char.isalpha() for char in token)]
    return len(letters) >= 2 and sum(token.isupper() for token in letters) / len(letters) >= 0.6


def line_tokens(line: str) -> list[str]:
    tokens = WORD.findall(line)
    if is_heading(tokens):
        return [token if len(token) <= 4 else token.capitalize() for token in tokens]
    return tokens


def domain_label(url: str) -> str | None:
    host = re.sub(r"^(?:https?://)?(?:www\.)?", "", url, flags=re.IGNORECASE)
    labels = re.split(r"[/?#:]", host, maxsplit=1)[0].lower().split(".")
    while len(labels) > 1 and labels[-1] in DOMAIN_SUFFIXES:
        labels.pop()
    label = labels[-1]
    ready = len(label) >= 4 and label not in GENERIC_LABELS and label not in DOMAIN_SUFFIXES
    return label.capitalize() if ready and re.fullmatch(r"[a-z0-9\-]+", label) else None


def url_terms(text: str) -> Iterator[tuple[str, int]]:
    for url in URL.findall(text):
        if (label := domain_label(url)) is not None:
            yield label, FOREIGN_WEIGHT


def word_terms(tokens: list[str]) -> Iterator[tuple[str, int]]:
    for token in tokens:
        if has_evidence(token):
            yield token, FOREIGN_WEIGHT


def phrase_runs(tokens: list[str]) -> Iterator[list[str]]:
    run: list[str] = []
    for token in tokens:
        if token[0].isupper() and fold(token) not in COMMON:
            run.append(token)
        elif run and fold(token) in CONNECTORS:
            run.append(token)
        else:
            yield run
            run = []
    yield run


def phrase_terms(tokens: list[str]) -> Iterator[tuple[str, int]]:
    for run in phrase_runs(tokens):
        while run and fold(run[-1]) in CONNECTORS:
            run.pop()
        if 2 <= len(run) <= MAX_PHRASE_TOKENS and any(has_evidence(token) for token in run):
            yield " ".join(run), PHRASE_WEIGHT


def is_name_like(item: str) -> bool:
    tokens = WORD.findall(item)
    words = [token for token in tokens if fold(token) not in CONNECTORS]
    if not words or len(tokens) > MAX_PHRASE_TOKENS or item.strip().endswith(":"):
        return False
    return all(
        (token[0].isupper() or is_technical(token))
        and fold(token) not in COMMON
        and not token.isdigit()
        for token in words
    )


def split_items(line: str) -> list[str]:
    return [item.strip(" \t\"'()[]“”.") for item in ITEM_BREAK.split(LIST_MARK.sub("", line))]


def list_runs(lines: Iterable[str]) -> Iterator[list[str]]:
    run: list[str] = []
    for line in lines:
        items = [item for item in split_items(line) if item]
        for item in items:
            if is_name_like(item):
                run.append(item)
            else:
                yield run
                run = []
        if len(items) != 1 or not run:
            yield run
            run = []
    yield run


def list_terms(lines: Iterable[str]) -> Iterator[tuple[str, int]]:
    for run in list_runs(lines):
        if len(run) >= MIN_LIST_RUN:
            for item in run:
                yield item, LIST_WEIGHT


def text_terms(text: str) -> Iterator[tuple[str, int]]:
    yield from url_terms(text)
    lines = EMAIL.sub(" ", URL.sub(" ", text)).splitlines()
    yield from list_terms(lines)
    for line in lines:
        for sentence in SENTENCE_END.split(line):
            tokens = line_tokens(sentence)
            yield from word_terms(tokens)
            yield from phrase_terms(tokens)


def document_scores(text: str) -> dict[str, float]:
    counts: Counter[str] = Counter()
    weights: dict[str, int] = {}
    for term, weight in text_terms(text):
        counts[term] += 1
        weights[term] = max(weights.get(term, 0), weight)
    return {term: weights[term] * (1 + math.log(count)) for term, count in counts.items()}


def extract_terms(texts: Iterable[str], limit: int) -> tuple[str, ...]:
    scores: Counter[str] = Counter()
    for text in texts:
        scores.update(document_scores(text))
    chosen: list[str] = []
    seen: set[str] = set()
    for term, _ in scores.most_common():
        key = fold(term)
        if key not in seen:
            seen.add(key)
            chosen.append(term)
        if len(chosen) == limit:
            break
    return tuple(chosen)
