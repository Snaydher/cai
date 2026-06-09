"""Shared helpers for locating and mutating the effective CAI ``.env`` file."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

DEFAULT_SHARED_ENV_PATH = Path("~/.config/cai/.env").expanduser()


def get_explicit_env_file() -> Path | None:
    """Return ``CAI_ENV_FILE`` when set to a non-empty path."""
    raw = (os.environ.get("CAI_ENV_FILE") or "").strip()
    if not raw:
        return None
    return Path(raw).expanduser()


def iter_env_search_dirs(start: Path | None = None) -> Iterable[Path]:
    """Yield the current directory and its parents, nearest-first."""
    base = (start or Path.cwd()).expanduser()
    try:
        base = base.resolve()
    except OSError:
        base = base.absolute()

    current = base
    seen: set[Path] = set()
    while current not in seen:
        seen.add(current)
        yield current
        if current.parent == current:
            break
        current = current.parent


def find_nearest_env_file(start: Path | None = None) -> Path | None:
    """Return the nearest existing ``.env`` from *start* up to filesystem root."""
    for directory in iter_env_search_dirs(start):
        candidate = directory / ".env"
        if candidate.is_file():
            return candidate
    return None


def get_shared_env_file() -> Path:
    """Return the default shared CAI env file location."""
    return DEFAULT_SHARED_ENV_PATH


def get_env_load_candidates(start: Path | None = None) -> list[Path]:
    """Return dotenv load candidates in precedence order."""
    out: list[Path] = []
    seen: set[Path] = set()

    explicit = get_explicit_env_file()
    if explicit is not None:
        try:
            resolved = explicit.resolve()
        except OSError:
            resolved = explicit.absolute()
        if resolved not in seen:
            seen.add(resolved)
            out.append(explicit)

    nearest = find_nearest_env_file(start)
    if nearest is not None:
        try:
            resolved = nearest.resolve()
        except OSError:
            resolved = nearest.absolute()
        if resolved not in seen:
            seen.add(resolved)
            out.append(nearest)

    shared = get_shared_env_file()
    try:
        resolved = shared.resolve()
    except OSError:
        resolved = shared.absolute()
    if resolved not in seen:
        out.append(shared)

    return out


def get_env_write_target(start: Path | None = None) -> Path:
    """Return the file path that CAI should update for persisted env changes."""
    explicit = get_explicit_env_file()
    if explicit is not None:
        return explicit

    nearest = find_nearest_env_file(start)
    if nearest is not None:
        return nearest

    return get_shared_env_file()
