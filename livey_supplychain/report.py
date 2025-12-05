from __future__ import annotations

import pathlib
from typing import Dict, List

from .models import Finding, Package, Report, ScoreBreakdown
from .utils import save_json, utc_now_iso


def build_report(project: str, mode: str, packages: List[Package], scores: Dict[str, ScoreBreakdown], policy_path: str | None) -> Report:
    findings: List[Finding] = []
    summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for pkg in packages:
        score = scores[pkg.name]
        findings.append(Finding(package=pkg, score=score))
        summary[score.severity.value] += 1
    return Report(
        generated_at=utc_now_iso(),
        project=project,
        mode=mode,
        summary=summary,
        findings=findings,
        policy_path=policy_path,
    )


def write_report(report: Report, output: pathlib.Path) -> pathlib.Path:
    serializable = report.model_dump()
    save_json(output, serializable)
    return output
