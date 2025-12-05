# Research Notes

LiveyScore v3 combines vendor trust, version hygiene, maintenance recency, popularity, script risk, binary presence, dependency posture, and policy alignment. Basic anomaly detection flags non-GitHub sources and zip distributions.

Threat considerations for Composer:
- Malicious scripts in install/update hooks
- Abandoned or renamed packages with hijacked namespaces
- Vendor sprawl increasing blast radius
- Unsigned distributions and opaque binary artifacts
- Outdated releases lacking security fixes

Heuristics used:
- Penalties for prerelease versions, abandonment, binaries, suspicious scripts, stale versions
- Bonuses for allowlisted vendors/packages
- Severity mapping configurable via policy thresholds

Future research directions are deliberately excluded from this build-focused release.
