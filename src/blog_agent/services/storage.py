"""Persistence for generated blogs and their images.

All paths live under the configured ``output_dir`` so artefacts are easy to find, mount, and clean up.
"""

from __future__ import annotations
import re
from pathlib import Path
from typing import Protocol
from blog_agent.core import get_settings


def safe_slug(title: str) -> str:
    s = re.sub(r"[^a-z0-9 _-]+", "", title.strip().lower())
    s = re.sub(r"\s+", "_", s).strip("_")
    return s or "blog"

class BlogStorage(Protocol):
    def write_markdown(self, title: str, markdown: str) -> Path: ...


class FileSystemStorage:
    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir

    def write_markdown(self, title: str, markdown: str) -> Path:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        path = self._output_dir / f"{safe_slug(title)}.md"
        path.write_text(markdown, encoding="utf-8")
        return path
    
def get_storage():
    return FileSystemStorage(output_dir=Path(get_settings().output_dir))