import html
import re
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import TypeAlias
from xml.etree import ElementTree

from erudio_transcriber.registry import Options

Reader: TypeAlias = Callable[[Path], str]

MAX_BYTES = 5_000_000
TAG = re.compile(r"<[^>]+>")
SPREADSHEET_TEXT = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"


def read_plain(path: Path) -> str:
    """Notes saved by older Windows editors are cp1252, so UTF-8 is tried first and only then it."""
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")


def read_markup(path: Path) -> str:
    return html.unescape(TAG.sub(" ", read_plain(path)))


def read_word(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml").decode("utf-8", errors="replace")
    return html.unescape(TAG.sub("", xml.replace("</w:p>", "\n")))


def read_spreadsheet(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if "xl/sharedStrings.xml" not in names:
            return ""
        root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))  # noqa: S314
    return "\n".join(
        "".join(node.text or "" for node in item.iter(SPREADSHEET_TEXT)) for item in root
    )


READERS: dict[str, Reader] = {
    ".txt": read_plain,
    ".md": read_plain,
    ".csv": read_plain,
    ".html": read_markup,
    ".htm": read_markup,
    ".docx": read_word,
    ".xlsx": read_spreadsheet,
}


class DocumentSource:
    def texts(self, folder: Path) -> tuple[str, ...]:
        found = sorted(
            path
            for path in folder.rglob("*")
            if path.suffix.lower() in READERS and path.is_file() and not path.name.startswith("~$")
        )
        return tuple(text for path in found if (text := self.read(path)))

    def read(self, path: Path) -> str:
        if path.stat().st_size > MAX_BYTES:
            return ""
        try:
            return READERS[path.suffix.lower()](path)
        except (OSError, zipfile.BadZipFile, ElementTree.ParseError, KeyError):
            return ""


def create_document_source(options: Options) -> DocumentSource:
    return DocumentSource()
