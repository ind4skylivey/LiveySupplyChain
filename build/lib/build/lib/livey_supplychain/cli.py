from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import track

from . import __app_name__, __version__
from .models import Package
from .policy import PolicyLoader, PolicyModel
from .providers.packagist import fetch_metadata
from .report import build_report, write_report
from .scanner import detect_anomalies, load_composer
from .score import score_packages
from .utils import CACHE_DIR, LiveyError, clear_cache

app = typer.Typer(add_completion=False, help="LiveySupplyChain - Composer supply-chain security toolkit")
console = Console()


@app.command()
def version():
    """Show version."""
    console.print(f"{__app_name__} {__version__}")


def _load_policy(policy_path: Optional[pathlib.Path]) -> PolicyModel:
    fallback = pathlib.Path("tools/supply_chain_policy.yaml")
    loader = PolicyLoader(policy_path=policy_path, fallback=fallback)
    return loader.load()


def _collect_packagist(packages: List[Package], online: bool) -> Dict[str, Dict]:
    metadata: Dict[str, Dict[str, Any]] = {}
    for pkg in track(packages, description="Fetching metadata", disable=not online):
        data = fetch_metadata(pkg.name, online=online)
        pkg_meta: Dict[str, any] = {}
        if data:
            versions = data.get("packages", {}).get(pkg.name, {})
            if versions:
                latest_ver = sorted(versions.keys())[-1]
                latest_data = versions[latest_ver]
                pkg_meta["latest_version"] = latest_ver
                pkg.latest_version = latest_ver
                if latest_data.get("time"):
                    dt = datetime.fromisoformat(latest_data["time"].replace("Z", "+00:00"))
                    pkg_meta["release_age_days"] = (datetime.now(timezone.utc) - dt).days
                downloads = latest_data.get("downloads", {})
                pkg_meta["downloads"] = downloads.get("total") if isinstance(downloads, dict) else None
                pkg.downloads = pkg_meta.get("downloads")
                maintainers = latest_data.get("authors", [])
                pkg_meta["maintainers"] = len(maintainers)
        metadata[pkg.name] = pkg_meta
    return metadata


def _print_summary(scores):
    table = Table(title="LiveyScore summary")
    table.add_column("Package")
    table.add_column("Score", justify="right")
    table.add_column("Severity")
    for name, score in scores.items():
        table.add_row(name, str(score.total), score.severity.value)
    console.print(table)


@app.command()
def scan(
    root: pathlib.Path = typer.Argument(".", help="Project root containing composer.lock"),
    policy: Optional[pathlib.Path] = typer.Option(None, "--policy", help="Path to policy YAML"),
    online: bool = typer.Option(False, "--online/--offline", help="Fetch Packagist metadata"),
    fail_under: Optional[int] = typer.Option(None, help="Fail if score below threshold"),
    output: Optional[pathlib.Path] = typer.Option(None, help="Write report JSON"),
    debug: bool = typer.Option(False, "--debug", help="Verbose errors"),
):
    """Scan composer.lock and compute scores."""
    try:
        policy_model = _load_policy(policy)
        packages, meta = load_composer(root)
        pkg_meta = _collect_packagist(packages, online=online)
        scores = score_packages(packages, policy_model, pkg_meta)
        _print_summary(scores)
        threshold = fail_under or policy_model.default_threshold
        worst = min(scores.values(), key=lambda s: s.total)
        if output:
            report = build_report(str(root), "scan", packages, scores, str(policy) if policy else None)
            write_report(report, output)
            console.print(f"Report written to {output}")
        if worst.total < threshold:
            raise typer.Exit(code=1)
    except LiveyError as e:
        if debug:
            raise
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)


@app.command()
def explain(
    package: Optional[str] = typer.Argument(None, help="Package to explain"),
    root: pathlib.Path = typer.Option(".", help="Project root"),
    policy: Optional[pathlib.Path] = typer.Option(None, "--policy", help="Policy file"),
    online: bool = typer.Option(False, "--online/--offline"),
):
    """Show detailed breakdown per package."""
    policy_model = _load_policy(policy)
    packages, _ = load_composer(root)
    pkg_meta = _collect_packagist(packages, online=online)
    scores = score_packages(packages, policy_model, pkg_meta)
    for pkg in packages:
        if package and pkg.name != package:
            continue
        score = scores[pkg.name]
        console.rule(f"[bold]{pkg.name}[/bold] {pkg.version}")
        console.print(f"Severity: [bold]{score.severity.value}[/bold] Score: {score.total}")
        table = Table(show_header=True, header_style="bold")
        table.add_column("Component")
        table.add_column("Value")
        for comp in [
            "vendor_trust",
            "version_hygiene",
            "maintenance",
            "popularity",
            "script_risk",
            "binaries",
            "dependency_posture",
            "policy_alignment",
        ]:
            table.add_row(comp, str(getattr(score, comp)))
        console.print(table)
        if score.reasons:
            console.print("Reasons:")
            for r in score.reasons:
                console.print(f" - {r}")
        if score.anomalies:
            console.print("Anomalies:")
            for a in score.anomalies:
                console.print(f" ! {a}")
    if package and package not in scores:
        console.print(f"Package {package} not found")


@app.command("init-policy")
def init_policy(path: pathlib.Path = typer.Argument(pathlib.Path("tools/supply_chain_policy.yaml"))):
    """Create default policy file."""
    if path.exists():
        console.print(f"Policy already exists at {path}")
        raise typer.Exit(code=0)
    sample = {
        "version": 1,
        "default_threshold": 75,
        "weights": PolicyModel().weights.dict(),
        "allowlist": {"vendors": ["symfony", "laravel"], "packages": ["phpunit/phpunit"]},
        "denylist": {"vendors": [], "packages": []},
        "vendor_classes": {"tier1": ["symfony/*", "laravel/*"], "tier3": ["*"]},
        "penalties": PolicyModel().penalties.dict(),
        "bonuses": PolicyModel().bonuses.dict(),
        "reporting": PolicyModel().reporting.dict(),
        "severities": PolicyModel().severities.dict(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sample, indent=2), encoding="utf-8")
    console.print(f"Policy written to {path}")


@app.command()
def report(
    root: pathlib.Path = typer.Argument("."),
    policy: Optional[pathlib.Path] = typer.Option(None, "--policy"),
    online: bool = typer.Option(False, "--online/--offline"),
    output: pathlib.Path = typer.Option(pathlib.Path("reports/report.json"), help="Report path"),
):
    """Generate JSON report."""
    policy_model = _load_policy(policy)
    packages, _ = load_composer(root)
    pkg_meta = _collect_packagist(packages, online=online)
    scores = score_packages(packages, policy_model, pkg_meta)
    rep = build_report(str(root), "report", packages, scores, str(policy) if policy else None)
    write_report(rep, output)
    console.print(f"Report stored at {output}")


@app.command()
def score(
    root: pathlib.Path = typer.Argument("."),
    policy: Optional[pathlib.Path] = typer.Option(None, "--policy"),
    online: bool = typer.Option(False, "--online/--offline"),
):
    """Print summary scores."""
    policy_model = _load_policy(policy)
    packages, _ = load_composer(root)
    pkg_meta = _collect_packagist(packages, online=online)
    scores = score_packages(packages, policy_model, pkg_meta)
    _print_summary(scores)


@app.command("cache")
def cache_cmd(action: str = typer.Argument("clear", help="clear")):
    if action == "clear":
        clear_cache()
        console.print(f"Cache cleared at {CACHE_DIR}")
    else:
        console.print("Unknown cache action")
        raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
