import json
import shutil
import pathlib

from typer.testing import CliRunner

from livey_supplychain import cli

runner = CliRunner()


def setup_fixture(tmp_path: pathlib.Path):
    src = pathlib.Path("tests/data")
    shutil.copy(src / "composer.lock", tmp_path / "composer.lock")
    shutil.copy(src / "composer.json", tmp_path / "composer.json")


def test_cli_scan_offline(tmp_path):
    setup_fixture(tmp_path)
    output = tmp_path / "report.json"
    result = runner.invoke(
        cli.app,
        ["scan", str(tmp_path), "--offline", "--policy", "tools/supply_chain_policy.yaml", "--fail-under", "0", "--output", str(output)],
    )
    assert result.exit_code == 0
    data = json.loads(output.read_text())
    assert data["summary"]

