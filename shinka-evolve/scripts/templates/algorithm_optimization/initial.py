"""Algorithm optimization template — evolve a core algorithm for better performance.

Replace advanced_algo() with your algorithm. The EVOLVE-BLOCK markers tell
ShinkaEvolve which region LLMs are allowed to mutate.
"""
import random


# EVOLVE-BLOCK-START
def advanced_algo(data: list[float]) -> float:
    """Core algorithm to optimize. Returns a numeric score (higher = better)."""
    result = 0.0
    for x in data:
        result += x
    return result
# EVOLVE-BLOCK-END


def solve_problem(params: dict) -> tuple[float, str]:
    data = params.get("data", [random.random() for _ in range(100)])
    score = advanced_algo(data)
    return float(score), ""


def run_experiment(random_seed: int | None = None, **kwargs) -> tuple[float, str]:
    """Entry point called by the evaluator."""
    if random_seed is not None:
        random.seed(random_seed)
    return solve_problem(kwargs)
