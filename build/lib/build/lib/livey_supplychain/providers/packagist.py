from __future__ import annotations

import json
import time
from typing import Dict, Optional

import requests

from ..utils import cache_path, ensure_dir

PACKAGIST_URL = "https://repo.packagist.org/p/{package}.json"
CACHE_TTL = 86400  # 24h


def _cache_file(package: str):
    safe = package.replace("/", "_")
    return cache_path("packagist", f"{safe}.json")


def fetch_metadata(package: str, online: bool = False, session: Optional[requests.Session] = None) -> Dict:
    cache_file = _cache_file(package)
    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < CACHE_TTL:
            with cache_file.open("r", encoding="utf-8") as f:
                return json.load(f)
    if not online:
        return {}
    url = PACKAGIST_URL.format(package=package)
    sess = session or requests.Session()
    resp = sess.get(url, timeout=10)
    if resp.status_code != 200:
        return {}
    data = resp.json()
    ensure_dir(cache_file.parent)
    with cache_file.open("w", encoding="utf-8") as f:
        json.dump(data, f)
    return data
