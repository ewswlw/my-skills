import random

from tactical_aa_research.discover_strategy import random_trial as discover_random_trial
from tactical_aa_research.joint_pass_search import random_trial as joint_random_trial


def test_discover_random_trial_disables_leverage_when_policy_false():
    t = discover_random_trial(random.Random(11), portfolio_leverage_allowed=False)
    assert float(t["lev_hi"]) == 1.0


def test_joint_random_trial_disables_leverage_when_policy_false():
    t = joint_random_trial(random.Random(17), portfolio_leverage_allowed=False)
    assert float(t["lev_hi"]) == 1.0
