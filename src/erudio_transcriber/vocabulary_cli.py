import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from erudio_transcriber.application.vocabulary_builder import build_vocabulary, write_vocabulary
from erudio_transcriber.application.vocabulary_lookup import VOCABULARY_FILE
from erudio_transcriber.ports.vocabulary_source import VocabularySource
from erudio_transcriber.registry import DriverGroup, available, load


def parse(arguments: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="erudio-transcriber-vocab")
    parser.add_argument("source", type=Path, help="course folder (never written to)")
    parser.add_argument("output", type=Path, help="folder that receives vocab.txt")
    parser.add_argument("--max-terms", type=int, default=120)
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    args = parse(sys.argv[1:] if arguments is None else arguments)
    sources = [
        cast(VocabularySource, load(DriverGroup.VOCABULARY_SOURCE, name)({}))
        for name in available(DriverGroup.VOCABULARY_SOURCE)
    ]
    terms = build_vocabulary(args.source, sources, args.max_terms)
    destination = args.output / VOCABULARY_FILE
    write_vocabulary(destination, terms)
    print(f"{len(terms)} terms -> {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
