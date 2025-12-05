from __future__ import annotations

import pathlib
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, model_validator, field_validator

from .utils import load_yaml


class Weights(BaseModel):
    vendor_trust: float = 0.25
    version_hygiene: float = 0.15
    maintenance: float = 0.15
    popularity: float = 0.10
    script_risk: float = 0.10
    binaries: float = 0.05
    dependency_posture: float = 0.10
    policy_alignment: float = 0.10

    @model_validator(mode="after")
    def total_one(self):  # type: ignore[override]
        total = sum(self.model_dump().values())
        if not 0.99 <= total <= 1.01:
            raise ValueError(f"Weights must sum to 1.0, got {total:.2f}")
        return self


class Penalties(BaseModel):
    prerelease: int = 10
    abandoned: int = 25
    unsigned_dist: int = 15
    suspicious_script: int = 20
    binary_present: int = 15
    stale_version: int = 10


class Bonuses(BaseModel):
    signed_source: int = 10
    maintainer_diversity: int = 5


class Reporting(BaseModel):
    include_transitives: bool = True
    redact_urls: bool = False


class Thresholds(BaseModel):
    critical: int = 40
    high: int = 60
    medium: int = 75
    low: int = 90

    @field_validator("critical", "high", "medium", "low")
    @classmethod
    def between_zero_hundred(cls, v: int) -> int:
        if not 0 <= v <= 100:
            raise ValueError("Thresholds must be between 0-100")
        return v


class PolicyModel(BaseModel):
    version: int = 1
    default_threshold: int = 75
    weights: Weights = Field(default_factory=Weights)
    allowlist: Dict[str, List[str]] = Field(default_factory=lambda: {"vendors": [], "packages": []})
    denylist: Dict[str, List[str]] = Field(default_factory=lambda: {"vendors": [], "packages": []})
    vendor_classes: Dict[str, List[str]] = Field(default_factory=lambda: {"tier1": [], "tier3": ["*"]})
    penalties: Penalties = Field(default_factory=Penalties)
    bonuses: Bonuses = Field(default_factory=Bonuses)
    reporting: Reporting = Field(default_factory=Reporting)
    severities: Thresholds = Field(default_factory=Thresholds)

    @field_validator("default_threshold")
    @classmethod
    def valid_threshold(cls, v: int) -> int:
        if not 0 <= v <= 100:
            raise ValueError("default_threshold must be 0-100")
        return v


class PolicyLoader:
    def __init__(self, policy_path: Optional[pathlib.Path] = None, fallback: Optional[pathlib.Path] = None):
        self.policy_path = policy_path
        self.fallback = fallback

    def load(self) -> PolicyModel:
        paths: List[pathlib.Path] = []
        if self.policy_path:
            paths.append(self.policy_path)
        if self.fallback and (not paths or not paths[0].exists()):
            paths.append(self.fallback)
        if not paths:
            return PolicyModel()
        for path in paths:
            if path and path.exists():
                data = load_yaml(path)
                return PolicyModel(**data)
        return PolicyModel()


__all__ = ["PolicyModel", "PolicyLoader"]
