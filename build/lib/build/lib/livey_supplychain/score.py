from __future__ import annotations

import re
from typing import Dict, List, Tuple

from .models import Package, ScoreBreakdown, Severity
from .policy import PolicyModel


def _normalize(value: float) -> float:
    return max(0.0, min(100.0, value))


def _severity(score: float, thresholds) -> Severity:
    if score < thresholds.critical:
        return Severity.CRITICAL
    if score < thresholds.high:
        return Severity.HIGH
    if score < thresholds.medium:
        return Severity.MEDIUM
    if score < thresholds.low:
        return Severity.LOW
    return Severity.INFO


def score_package(pkg: Package, policy: PolicyModel, metadata: Dict) -> ScoreBreakdown:
    reasons: List[str] = []

    # Vendor trust
    vendor_score = 100.0
    if pkg.vendor in policy.denylist.get("vendors", []):
        vendor_score = 0
        reasons.append("Vendor denylisted")
    elif pkg.vendor in policy.allowlist.get("vendors", []):
        vendor_score = 95
        reasons.append("Vendor allowlisted")
    elif pkg.vendor in policy.vendor_classes.get("tier1", []):
        vendor_score = 90
        reasons.append("Trusted vendor class")
    elif pkg.vendor in policy.vendor_classes.get("tier3", []):
        vendor_score = 60
        reasons.append("Unclassified vendor")

    # Version hygiene
    version_score = 100.0
    if re.search(r"(dev|alpha|beta|rc)", pkg.version, re.IGNORECASE):
        version_score -= policy.penalties.prerelease
        reasons.append("Prerelease version")
    if pkg.latest_version and pkg.latest_version != pkg.version:
        version_score -= policy.penalties.stale_version
        reasons.append("Not latest version")

    # Maintenance
    maintenance_score = 100.0
    if metadata.get("release_age_days"):
        days = metadata["release_age_days"]
        if days > 365:
            maintenance_score -= 20
            reasons.append("Release older than 1 year")
        if days > 730:
            maintenance_score -= 30
            reasons.append("Release older than 2 years")
    if metadata.get("maintainers", 1) <= 1:
        maintenance_score -= 10
        reasons.append("Single maintainer risk")

    # Popularity
    popularity_score = 100.0
    downloads = metadata.get("downloads", 0)
    if downloads == 0:
        popularity_score = 60
    elif downloads < 1000:
        popularity_score = 70
    elif downloads < 10000:
        popularity_score = 80
    elif downloads < 100000:
        popularity_score = 90
    else:
        popularity_score = 100

    # Script risk
    script_score = 100.0
    suspicious = [s for s in pkg.scripts if re.search(r"(curl|wget|bash|sh)\s", s, re.IGNORECASE)]
    if suspicious:
        script_score -= policy.penalties.suspicious_script
        reasons.append("Suspicious composer scripts")
    if pkg.scripts:
        script_score -= 5  # generic risk

    # Binary presence
    binary_score = 100.0
    if pkg.binaries:
        binary_score -= policy.penalties.binary_present
        reasons.append("Package ships binaries")

    # Dependency posture
    dependency_score = 100.0
    transitive_count = len(pkg.require)
    if transitive_count > 20:
        dependency_score -= 15
        reasons.append("Large dependency surface")
    if pkg.abandoned:
        dependency_score -= policy.penalties.abandoned
        reasons.append("Package marked abandoned")

    # Policy alignment
    alignment_score = 100.0
    if pkg.name in policy.denylist.get("packages", []):
        alignment_score = 0
        reasons.append("Package denylisted")
    if pkg.name in policy.allowlist.get("packages", []):
        alignment_score = 95
        reasons.append("Package allowlisted")

    # Anomalies
    anomalies: List[str] = []
    if pkg.repository and pkg.dist_type == "zip":
        anomalies.append("Distribution is zip; prefer source")
    if pkg.repository and "github.com" not in pkg.repository:
        anomalies.append("Non-GitHub repository")
    if pkg.dev:
        reasons.append("Dev dependency")

    components = {
        "vendor_trust": _normalize(vendor_score),
        "version_hygiene": _normalize(version_score),
        "maintenance": _normalize(maintenance_score),
        "popularity": _normalize(popularity_score),
        "script_risk": _normalize(script_score),
        "binaries": _normalize(binary_score),
        "dependency_posture": _normalize(dependency_score),
        "policy_alignment": _normalize(alignment_score),
    }

    total = sum(
        components[key] * getattr(policy.weights, key) for key in components
    )
    severity = _severity(total, policy.severities)

    return ScoreBreakdown(
        vendor_trust=components["vendor_trust"],
        version_hygiene=components["version_hygiene"],
        maintenance=components["maintenance"],
        popularity=components["popularity"],
        script_risk=components["script_risk"],
        binaries=components["binaries"],
        dependency_posture=components["dependency_posture"],
        policy_alignment=components["policy_alignment"],
        anomalies=anomalies,
        total=round(total, 2),
        severity=severity,
        reasons=reasons,
    )


def score_packages(packages: List[Package], policy: PolicyModel, metadata: Dict[str, Dict]) -> Dict[str, ScoreBreakdown]:
    results: Dict[str, ScoreBreakdown] = {}
    for pkg in packages:
        pkg_meta = metadata.get(pkg.name, {})
        results[pkg.name] = score_package(pkg, policy, pkg_meta)
    return results

