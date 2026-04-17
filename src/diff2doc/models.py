"""Data structures shared across pipeline stages."""

from dataclasses import dataclass


@dataclass
class Hunk:
    """A single chunk of changed lines within a file diff."""

    header: str
    content: str


@dataclass
class FileDiff:
    """All parsed hunks for one changed file in a git diff."""

    path: str
    hunks: list[Hunk]
    explanation: str = ""


@dataclass
class DiffResult:
    """Structured diff data plus the original raw patch text."""

    files: list[FileDiff]
    raw_diff: str
