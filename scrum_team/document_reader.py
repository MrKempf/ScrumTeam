"""Utility helpers for reading requirement documents."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List


def read_requirements(path: str | Path) -> List[str]:
    """Read a requirement document and return a list of normalized requirements."""
    content = Path(path).read_text(encoding="utf-8")
    lines = [line.strip(" \n\r\t-*#") for line in content.splitlines()]
    requirements = [line for line in lines if line]
    return requirements


def extract_keywords(requirements: Iterable[str]) -> List[str]:
    """Extract simple keywords from the requirements to guide architecture choices."""
    keywords: set[str] = set()
    for requirement in requirements:
        for token in requirement.replace(",", " ").replace(".", " ").split():
            normalized = token.lower()
            if len(normalized) >= 4:
                keywords.add(normalized)
    return sorted(keywords)
