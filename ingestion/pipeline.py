"""Shared, dependency-light extraction pipeline helpers."""

from __future__ import annotations

import hashlib
import re
from typing import Iterable


STAGES = (
    "Uploaded",
    "Parsed",
    "Extracted",
    "Cleaned",
    "Chunked",
    "Embedded",
    "Ready",
)


def file_signature(name: str, data: bytes) -> str:
    """Create a stable cache key for one uploaded file."""
    digest = hashlib.sha256()
    digest.update(name.encode("utf-8"))
    digest.update(data)
    return digest.hexdigest()


def clean_text(text: str) -> str:
    """Normalize whitespace without removing useful punctuation or equations."""
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        piece = clean_text(text[start:end])
        if piece:
            chunks.append(piece)
        if end == len(text):
            break
        start = end - overlap
    return chunks
