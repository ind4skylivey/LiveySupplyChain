from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import yaml

DEFAULT_CACHE = pathlib.Path.cwd() / ".cache" / "livey_supplychain"
CACHE_DIR = pathlib.Path(os.getenv("LIVEY_CACHE", DEFAULT_CACHE))


def ensure_dir(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_yaml(path: pathlib.Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_json(path: pathlib.Path, data: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def load_json(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def hash_file(path: pathlib.Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clear_cache() -> None:
    if CACHE_DIR.exists():
        shutil.rmtree(CACHE_DIR)


def cache_path(*parts: str) -> pathlib.Path:
    path = CACHE_DIR.joinpath(*parts)
    ensure_dir(path.parent)
    return path


def severity_color(severity: str) -> str:
    mapping = {
        "critical": "red",
        "high": "bright_red",
        "medium": "yellow",
        "low": "green3",
        "info": "cyan",
    }
    return mapping.get(severity, "white")


class LiveyError(Exception):
    """Base error for LiveySupplyChain."""


def safe_join(base: pathlib.Path, *paths: str) -> pathlib.Path:
    final = base.joinpath(*paths).resolve()
    base_resolved = base.resolve()
    if base_resolved not in final.parents and final != base_resolved:
        raise LiveyError("Path traversal detected")
    return final
