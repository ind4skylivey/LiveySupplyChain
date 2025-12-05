# Contributing

Thank you for improving LiveySupplyChain. Please follow these guidelines:

- Use English for code, docs, and commits.
- Open an issue before large changes.
- Branch naming: `feature/<topic>` or `fix/<bug>`.
- Coding style: type hints, Pydantic validation, clear error handling, no unsafe YAML loading.
- Tests: add/adjust pytest coverage for new code; include fixtures for composer.lock when relevant.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest
```

## Running tests
```bash
pytest
```

## Code quality checklist
- Typer CLI stays stable and documented
- Policy schema validation preserved
- Offline mode remains the default
- No secrets or credentials in tests or fixtures

## Reporting security issues
Please follow `docs/SECURITY.md`.
