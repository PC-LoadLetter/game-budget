from __future__ import annotations

import fcntl
import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def journal_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with open(lock_path, "w", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def read_journal(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def append_journal(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with journal_lock(path):
        with open(path, "a", encoding="utf-8") as handle:
            if text and not text.endswith("\n"):
                text += "\n"
            if text and not text.startswith("\n") and path.stat().st_size > 0:
                handle.write("\n")
            handle.write(text)
            if not text.endswith("\n"):
                handle.write("\n")


def write_journal(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with journal_lock(path):
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)
