from __future__ import annotations

import json
import pathlib
from typing import Dict, List, Tuple

from .models import Package
from .utils import LiveyError


class LockfileError(LiveyError):
    pass


def _read_json(path: pathlib.Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_composer(root: pathlib.Path) -> Tuple[List[Package], Dict[str, str]]:
    lock_path = root / "composer.lock"
    json_path = root / "composer.json"
    if not lock_path.exists():
        raise LockfileError("composer.lock not found")
    lock_data = _read_json(lock_path)
    composer_data = _read_json(json_path) if json_path.exists() else {}
    scripts = list(composer_data.get("scripts", {}).keys()) if isinstance(composer_data.get("scripts"), dict) else []

    packages: List[Package] = []
    for section, is_dev in (("packages", False), ("packages-dev", True)):
        for pkg in lock_data.get(section, []) or []:
            package = Package(
                name=pkg.get("name", ""),
                version=pkg.get("version", ""),
                description=pkg.get("description"),
                time=pkg.get("time"),
                source_type=pkg.get("source", {}).get("type"),
                dist_type=pkg.get("dist", {}).get("type"),
                scripts=scripts,
                binaries=pkg.get("bin", []),
                require=pkg.get("require", {}),
                dev=is_dev,
                abandoned=bool(pkg.get("abandoned", False)),
                repository=pkg.get("source", {}).get("url"),
                authors=[a.get("name") for a in pkg.get("authors", []) if a.get("name")],
            )
            packages.append(package)
    metadata = {"lock_hash": lock_data.get("content-hash", ""), "packages_count": len(packages)}
    return packages, metadata


def detect_anomalies(packages: List[Package]) -> List[str]:
    anomalies: List[str] = []
    vendors = {}
    for pkg in packages:
        vendors.setdefault(pkg.vendor, 0)
        vendors[pkg.vendor] += 1
    for vendor, count in vendors.items():
        if count > 50:
            anomalies.append(f"Vendor {vendor} has unusually high package count ({count})")
    return anomalies
