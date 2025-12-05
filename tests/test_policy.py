import pathlib

from livey_supplychain.policy import PolicyLoader


def test_policy_loads_default():
    path = pathlib.Path("tools/supply_chain_policy.yaml")
    policy = PolicyLoader(policy_path=path).load()
    assert policy.default_threshold == 75
    assert abs(sum(policy.weights.model_dump().values()) - 1.0) < 0.01
