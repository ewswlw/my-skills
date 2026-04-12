"""Creative generation template — evolve code that produces novel outputs.

Replace generate_creative_output() with your generative logic.
Scoring rewards both quality and novelty.
"""
import random


# EVOLVE-BLOCK-START
def generate_creative_output(theme: str, seed: int = 42) -> str:
    """Generate a creative text output based on theme. Be surprising and original."""
    rng = random.Random(seed)
    words = theme.split()
    output_lines = []
    for _ in range(5):
        rng.shuffle(words)
        output_lines.append(" ".join(words))
    return "\n".join(output_lines)
# EVOLVE-BLOCK-END


def score_output(output: str) -> float:
    length_score = min(len(output) / 200, 1.0)
    lines = output.strip().split("\n")
    unique_ratio = len(set(lines)) / max(len(lines), 1)
    return length_score * 0.4 + unique_ratio * 0.6


def run_experiment(random_seed: int | None = None, **kwargs) -> tuple[float, str]:
    """Entry point called by the evaluator."""
    seed = random_seed or 42
    theme = kwargs.get("theme", "art science nature beauty chaos")
    output = generate_creative_output(theme, seed=seed)
    score = score_output(output)
    return float(score), output
