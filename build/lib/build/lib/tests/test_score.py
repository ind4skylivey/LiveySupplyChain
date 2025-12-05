from livey_supplychain.models import Package
from livey_supplychain.policy import PolicyModel
from livey_supplychain.score import score_package


def test_score_package_basic():
    pkg = Package(
        name="symfony/console",
        version="v6.0.0",
        scripts=["post-install-cmd"],
        binaries=["bin/console"],
        require={"php": ">=8.0"},
        dev=False,
    )
    policy = PolicyModel()
    score = score_package(pkg, policy, metadata={"downloads": 50000, "maintainers": 2, "release_age_days": 100})
    assert 0 <= score.total <= 100
    assert score.severity
    assert "Package ships binaries" in score.reasons
