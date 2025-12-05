# MANIFEST

## Architecture
- CLI: `livey_supplychain/cli.py` (Typer)
- Scanner: `scanner.py` reads composer.lock/json
- Policy: `policy.py` Pydantic schema and loader
- Score engine: `score.py` implements LiveyScore v3
- Packagist provider: `providers/packagist.py` with cache
- Report: `report.py` builds JSON
- Models: `models.py` typed entities
- Utils: `utils.py` common helpers and cache path
- Assets: logo + dashboard in `assets/`
- Policy template: `tools/supply_chain_policy.yaml`
- Tests: `tests/` with fixtures and pytest cases

## Data Flow
composer.lock → scanner → packages → optional Packagist metadata → score engine (policy weights) → findings → JSON report → dashboard

## Commands
See `docs/README.md` for CLI usage and options.
