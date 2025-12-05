from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Package(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    time: Optional[str] = None
    source_type: Optional[str] = None
    dist_type: Optional[str] = None
    scripts: List[str] = Field(default_factory=list)
    binaries: List[str] = Field(default_factory=list)
    require: Dict[str, str] = Field(default_factory=dict)
    dev: bool = False
    abandoned: bool = False
    repository: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    latest_version: Optional[str] = None
    downloads: Optional[int] = None

    @property
    def vendor(self) -> str:
        return self.name.split("/")[0] if "/" in self.name else self.name


class ScoreBreakdown(BaseModel):
    vendor_trust: float
    version_hygiene: float
    maintenance: float
    popularity: float
    script_risk: float
    binaries: float
    dependency_posture: float
    policy_alignment: float
    anomalies: List[str] = Field(default_factory=list)
    total: float
    severity: Severity
    reasons: List[str] = Field(default_factory=list)


class Finding(BaseModel):
    package: Package
    score: ScoreBreakdown


class Report(BaseModel):
    generated_at: str
    project: str
    mode: str
    summary: Dict[str, int]
    findings: List[Finding]
    policy_path: Optional[str] = None
