<div align="center">

<p align="center">
  <img src="assets/livey_banner.svg" alt="LiveySupplyChain banner" width="780" height="260" />
</p>

### 🔐 Advanced Composer Supply-Chain Security Toolkit

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![License: Proprietary](https://img.shields.io/badge/license-Proprietary-red.svg?style=for-the-badge)](LICENSE)
[![Security: Hardened](https://img.shields.io/badge/security-hardened-green.svg?style=for-the-badge&logo=shieldsdotio&logoColor=white)](docs/SECURITY.md)
[![PyPI Version](https://img.shields.io/badge/pypi-v1.0.0-blue.svg?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org)

**LiveySupplyChain** is a next-generation security analysis framework designed for offensive security researchers, DevSecOps engineers, and supply-chain defenders. Built with Python, it provides deep dependency inspection, threat modeling, and policy enforcement for PHP Composer ecosystems.

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [CLI Reference](#-cli-reference) • [Policy Engine](#-policy-engine) • [Security](#-security-posture)

</div>

---

## 🎯 Overview

LiveySupplyChain implements **LiveyScore v3** — a proprietary multi-vector scoring algorithm that evaluates Composer dependencies across 9+ security dimensions. Unlike traditional vulnerability scanners, this toolkit performs behavioral analysis, supply-chain risk assessment, and policy-driven threat classification.

**Key Capabilities:**
- 🔍 **Deep Package Analysis** — Vendor reputation, version hygiene, maintenance posture
- 🎲 **Risk Quantification** — LiveyScore v3 with severity classification (CRITICAL/HIGH/MEDIUM/LOW)
- 🛡️ **Policy Enforcement** — YAML-based allow/deny lists, threshold gates, anomaly detection
- 🚫 **Offline-First Architecture** — Zero external dependencies by default; opt-in online mode
- 📊 **Rich Reporting** — JSON outputs + interactive HTML dashboard with dark mode
- ⚡ **CI/CD Integration** — Exit codes, fail-under thresholds, JSON artifacts

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔬 Scoring Engine
- **LiveyScore v3** weighted algorithm
- Vendor trust classification
- Version freshness analysis
- Maintenance activity tracking
- Download popularity metrics
- Post-install script detection
- Binary payload inspection
- Dependency depth analysis
- Policy compliance scoring
- Anomaly detection engine

</td>
<td width="50%">

### 🛠️ Toolkit Components
- **CLI Interface** — Powered by Typer + Rich
- **Policy Engine** — YAML schema with validation
- **Packagist Provider** — Metadata cache system
- **Report Generator** — JSON + HTML outputs
- **Dashboard UI** — Filtering, sorting, severity colors
- **Explain Mode** — Per-package breakdowns
- **Cache Management** — Manual purge controls
- **Threshold Gates** — CI fail conditions

</td>
</tr>
</table>

### 📈 Scoring Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Vendor Trust** | 20% | Reputation-based classification (trusted/verified/unknown/banned) |
| **Version Hygiene** | 15% | Constraint types, lockfile drift, version pinning |
| **Maintenance** | 15% | Package age, release frequency, staleness indicators |
| **Popularity** | 10% | Download counts, adoption metrics |
| **Script Risk** | 15% | Post-install/pre-update hooks, shell command detection |
| **Binary Presence** | 10% | Compiled executables, suspicious payloads |
| **Dependency Posture** | 10% | Transitive depth, sub-dependency risk |
| **Policy Alignment** | 5% | Allow/deny list compliance, license checks |
| **Anomalies** | Penalty | Typosquatting, name confusion, unusual patterns |

---

## 🚀 Installation

### Prerequisites
```bash
# Required
python >= 3.10
pip or pipx

# Optional (for online mode)
curl or wget for Packagist API
```

### Install via pipx (Recommended)
```bash
pipx install livey-supplychain
```

### Install via pip
```bash
pip install livey-supplychain
```

### Install from Source (Development)
```bash
git clone https://github.com/ind4skylivey/LiveySupplyChain.git
cd LiveySupplyChain
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest  # For testing
```

### Verify Installation
```bash
livey-supplychain version
# Output: livey-supplychain 1.0.0
```

---

## ⚡ Quick Start

### 1. Initialize Policy
```bash
livey-supplychain init-policy
# Creates: tools/supply_chain_policy.yaml
```

### 2. Scan Dependencies (Offline)
```bash
livey-supplychain scan --offline --output reports/scan.json
```

**Output:**
```
╭─────────────────── LiveyScore summary ───────────────────╮
│ Package              Score  Severity                     │
├──────────────────────────────────────────────────────────┤
│ symfony/console      92     LOW                          │
│ guzzlehttp/guzzle    78     MEDIUM                       │
│ monolog/monolog      85     LOW                          │
╰──────────────────────────────────────────────────────────╯
```

### 3. Deep Analysis (Online Mode)
```bash
livey-supplychain scan --online --output reports/report.json
# Fetches Packagist metadata for enhanced scoring
```

### 4. Explain Package
```bash
livey-supplychain explain symfony/console
```

**Output:**
```
╭─────────────────── symfony/console ───────────────────╮
│ Total Score: 92                                       │
│ Severity: LOW                                         │
├───────────────────────────────────────────────────────┤
│ Vendor Trust:        +20  (Trusted vendor)           │
│ Version Hygiene:     +13  (^7.0 constraint)          │
│ Maintenance:         +15  (Active maintenance)       │
│ Popularity:          +10  (High downloads)           │
│ Script Risk:          +15  (No risky scripts)        │
│ Binary Presence:     +10  (No binaries detected)     │
│ Dependency Posture:   +9  (Shallow depth)            │
╰───────────────────────────────────────────────────────╯
```

### 5. CI/CD Integration
```bash
# Fail build if any package scores below 70
livey-supplychain scan --fail-under 70 --offline

# Example in GitHub Actions
- name: Supply Chain Scan
  run: |
    livey-supplychain scan --fail-under 75 --output reports/scs.json
    
- name: Upload Artifact
  uses: actions/upload-artifact@v3
  with:
    name: supply-chain-report
    path: reports/scs.json
```

---

## 📖 CLI Reference

### `scan`
**Full dependency scan with score computation**

```bash
livey-supplychain scan [OPTIONS] [ROOT]

Arguments:
  ROOT              Project root containing composer.lock [default: .]

Options:
  --policy PATH     Custom policy YAML location
  --online          Fetch Packagist metadata (offline by default)
  --offline         Force offline mode (default)
  --fail-under INT  Exit code 1 if score < threshold
  --output PATH     Write JSON report to file
  --debug           Verbose error messages
```

**Examples:**
```bash
# Basic offline scan
livey-supplychain scan

# Scan with custom policy
livey-supplychain scan --policy security/policy.yaml

# Online scan with threshold gate
livey-supplychain scan --online --fail-under 80 --output reports/prod.json

# Debug mode for troubleshooting
livey-supplychain scan --debug
```

---

### `explain`
**Detailed scoring breakdown for a specific package**

```bash
livey-supplychain explain [PACKAGE] [OPTIONS]

Arguments:
  PACKAGE           Package name (vendor/package)

Options:
  --policy PATH     Custom policy YAML
  --root PATH       Project root [default: .]
  --online          Fetch metadata
```

**Examples:**
```bash
livey-supplychain explain symfony/console
livey-supplychain explain guzzlehttp/guzzle --online --policy tools/strict.yaml
```

---

### `report`
**Generate comprehensive JSON report**

```bash
livey-supplychain report [OPTIONS] [ROOT]

Options:
  --policy PATH     Custom policy YAML
  --online          Fetch Packagist metadata
  --output PATH     JSON output file [required]
```

**Examples:**
```bash
livey-supplychain report --online --output reports/full_report.json
```

---

### `score`
**Quick score table (minimal output)**

```bash
livey-supplychain score [OPTIONS] [ROOT]

Options:
  --policy PATH     Custom policy YAML
  --online          Fetch metadata
```

---

### `init-policy`
**Generate default policy template**

```bash
livey-supplychain init-policy [OPTIONS]

Options:
  --output PATH     Policy destination [default: tools/supply_chain_policy.yaml]
  --force           Overwrite existing policy
```

---

### `cache`
**Manage Packagist metadata cache**

```bash
livey-supplychain cache clear    # Purge all cached data
```

**Cache Location:** `~/.cache/livey_supplychain/`

---

### `version`
**Display toolkit version**

```bash
livey-supplychain version
```

---

## 🔧 Policy Engine

### Policy Schema

LiveySupplyChain uses a YAML-based policy engine for fine-grained control over scoring behavior, vendor classification, and threat detection.

**Default Location:** `tools/supply_chain_policy.yaml`

### Policy Structure

```yaml
weights:
  vendor_trust: 0.20
  version_hygiene: 0.15
  maintenance: 0.15
  popularity: 0.10
  script_risk: 0.15
  binary_presence: 0.10
  dependency_posture: 0.10
  policy_alignment: 0.05

vendor_classes:
  trusted:
    - symfony
    - guzzlehttp
    - monolog
  verified:
    - doctrine
    - phpunit
  unknown: []
  banned:
    - malicious-vendor
    - typosquat-lib

allow_list:
  - symfony/*
  - doctrine/orm

deny_list:
  - evil/package
  - suspicious/*

penalties:
  has_post_install_scripts: -10
  has_binaries: -5
  deep_dependencies: -5
  unknown_vendor: -5
  stale_package: -10

bonuses:
  trusted_vendor: +10
  verified_vendor: +5
  high_downloads: +5

severity_thresholds:
  critical: 40
  high: 60
  medium: 75
  low: 100

default_threshold: 70  # Minimum acceptable score

anomaly_detection:
  typosquatting:
    enabled: true
    threshold: 0.85
  name_confusion:
    enabled: true
  unusual_scripts:
    enabled: true
```

### Customizing Policies

**1. Vendor Classification**
```yaml
vendor_classes:
  trusted:
    - your-org
    - partner-vendor
  banned:
    - risky-vendor
```

**2. Adjust Scoring Weights**
```yaml
weights:
  script_risk: 0.25        # Increase script risk weight
  binary_presence: 0.15    # Increase binary detection weight
```

**3. Threshold Configuration**
```yaml
default_threshold: 80      # Stricter requirements
severity_thresholds:
  critical: 30
  high: 50
  medium: 70
  low: 100
```

**4. Allowlist/Denylist**
```yaml
allow_list:
  - internal/*             # Trust internal packages
  - symfony/*
  
deny_list:
  - deprecated/*
  - abandoned/*
```

---

## 📊 Reports & Dashboard

### JSON Report Structure

```json
{
  "metadata": {
    "scan_time": "2025-12-05T04:30:00Z",
    "root": "/path/to/project",
    "command": "scan",
    "policy": "tools/supply_chain_policy.yaml"
  },
  "packages": [
    {
      "name": "symfony/console",
      "version": "7.0.0",
      "score": {
        "total": 92,
        "severity": "LOW",
        "breakdown": {
          "vendor_trust": 20,
          "version_hygiene": 13,
          "maintenance": 15,
          "popularity": 10,
          "script_risk": 15,
          "binary_presence": 10,
          "dependency_posture": 9
        },
        "reasons": ["Trusted vendor", "Active maintenance"],
        "anomalies": []
      }
    }
  ]
}
```

### Interactive Dashboard

**Location:** `assets/dashboard.html`

**Features:**
- 🌙 **Dark Mode** — Cybersecurity-themed UI
- 🔍 **Search & Filter** — By package name, vendor, severity
- 📊 **Severity Colors** — Visual risk classification
- 📈 **Score Sorting** — Ascending/descending order
- 🔎 **Reason/Anomaly Inspector** — Expandable details
- 📁 **Local File Loading** — No backend required

**Usage:**
1. Generate report: `livey-supplychain report --online --output reports/report.json`
2. Open `assets/dashboard.html` in browser
3. Click "Load Report" and select `reports/report.json`

---

## 🔐 Security Posture

### Threat Model

LiveySupplyChain is designed with a **zero-trust supply-chain** philosophy:

| Threat Vector | Mitigation |
|---------------|------------|
| **Malicious Dependencies** | Vendor classification, deny lists, script detection |
| **Typosquatting** | Levenshtein distance analysis, name confusion detection |
| **Backdoor Scripts** | Post-install/pre-update hook inspection |
| **Binary Payloads** | Compiled executable detection and flagging |
| **Stale Packages** | Maintenance scoring, age analysis |
| **Deep Dependency Trees** | Transitive depth penalties |

### Offline-First Design

**Default Mode:** Offline — No external network requests  
**Online Mode:** Opt-in via `--online` flag

**Cache Security:**
- Metadata cached at `~/.cache/livey_supplychain/`
- Manual purge available: `livey-supplychain cache clear`
- No credential storage

### Responsible Disclosure

**Security issues:** See [docs/SECURITY.md](docs/SECURITY.md)

**Contact:** livey (GitHub: [@ind4skylivey](https://github.com/ind4skylivey))

---

## 🧪 Development

### Environment Setup

```bash
# Clone repository
git clone https://github.com/ind4skylivey/LiveySupplyChain.git
cd LiveySupplyChain

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install in editable mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black mypy
```

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=livey_supplychain --cov-report=html

# Specific test file
pytest tests/test_scanner.py -v
```

### Code Quality

```bash
# Format code
black livey_supplychain/

# Type checking
mypy livey_supplychain/

# Run linters (if configured)
ruff check livey_supplychain/
```

### Project Structure

```
LiveySupplyChain/
├── livey_supplychain/          # Main package
│   ├── __init__.py
│   ├── cli.py                  # Typer CLI entry point
│   ├── scanner.py              # composer.lock parser
│   ├── score.py                # LiveyScore v3 engine
│   ├── policy.py               # YAML policy loader
│   ├── report.py               # JSON report generator
│   ├── models.py               # Pydantic models
│   ├── utils.py                # Utilities & caching
│   └── providers/
│       └── packagist.py        # Metadata provider
├── tests/                      # Test suite
├── tools/                      # Policy templates
├── reports/                    # Generated reports
├── assets/                     # Banner + dashboard
├── docs/                       # Documentation
└── pyproject.toml              # Package metadata
```

---

## 📚 Documentation

- **[SECURITY.md](docs/SECURITY.md)** — Responsible disclosure process
- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** — Contribution guidelines
- **[RESEARCH.md](docs/RESEARCH.md)** — Scoring methodology & research
- **[MANIFEST.md](docs/MANIFEST.md)** — File inventory

---

## 🤝 Contributing

Contributions require explicit authorization. See [CONTRIBUTING.md](docs/CONTRIBUTING.md).

**Key Guidelines:**
- All commits must be in English
- Follow existing code style (Black formatting)
- Add tests for new features
- Update documentation as needed

---

## 📜 License

**LiveySupplyChain™** is proprietary software.

Copyright © 2025 Livey. All rights reserved.

This software, including **LiveyScore™** algorithm, source code, branding, and documentation, is protected intellectual property. Unauthorized use, reproduction, modification, or distribution is strictly prohibited.

**See [LICENSE](LICENSE) for full terms.**

For licensing inquiries: livey ([@ind4skylivey](https://github.com/ind4skylivey))

---

## 🎖️ Credits

**Author:** [ind4skylivey](https://github.com/ind4skylivey)  
**Project:** [LiveySupplyChain](https://github.com/ind4skylivey/LiveySupplyChain)

**Technologies:**
- [Python 3.10+](https://www.python.org)
- [Typer](https://typer.tiangolo.com) — CLI framework
- [Rich](https://rich.readthedocs.io) — Terminal formatting
- [Pydantic](https://pydantic-docs.helpmanual.io) — Data validation
- [PyYAML](https://pyyaml.org) — Policy parsing

---

<div align="center">

**🔐 Secure the Supply Chain 🔐**

[![GitHub](https://img.shields.io/badge/GitHub-ind4skylivey-181717?style=for-the-badge&logo=github)](https://github.com/ind4skylivey)
[![Python](https://img.shields.io/badge/Made%20with-Python-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)

</div>
