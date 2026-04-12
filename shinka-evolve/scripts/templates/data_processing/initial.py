"""Data processing template — evolve a data transformation pipeline.

Replace transform_data() with your processing logic.
"""
import random


# EVOLVE-BLOCK-START
def transform_data(records: list[dict]) -> list[dict]:
    """Process raw records into cleaned/enriched output. Optimize for throughput and quality."""
    output = []
    for rec in records:
        cleaned = {k: str(v).strip() for k, v in rec.items()}
        output.append(cleaned)
    return output
# EVOLVE-BLOCK-END


def generate_test_data(n: int = 50, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    fields = ["name", "value", "category"]
    return [{f: f"sample_{rng.randint(0, 1000)}" for f in fields} for _ in range(n)]


def run_experiment(random_seed: int | None = None, **kwargs) -> tuple[float, str]:
    """Entry point called by the evaluator."""
    seed = random_seed or 42
    data = generate_test_data(n=100, seed=seed)

    import time
    start = time.perf_counter()
    result = transform_data(data)
    elapsed = time.perf_counter() - start

    completeness = sum(1 for r in result if all(r.values())) / max(len(result), 1)
    speed_score = max(0, 1.0 - elapsed)
    score = completeness * 0.7 + speed_score * 0.3

    return float(score), f"Processed {len(result)} records in {elapsed:.4f}s"
