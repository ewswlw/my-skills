"""ML tuning template — evolve a model training/inference pipeline.

Replace build_and_evaluate_model() with your ML logic.
"""
import random


# EVOLVE-BLOCK-START
def build_and_evaluate_model(X_train, y_train, X_test, y_test) -> float:
    """Build a model, train, and return test accuracy. Higher = better."""
    from collections import Counter
    majority = Counter(y_train).most_common(1)[0][0]
    correct = sum(1 for y in y_test if y == majority)
    return correct / max(len(y_test), 1)
# EVOLVE-BLOCK-END


def generate_dataset(n: int = 200, seed: int = 42):
    rng = random.Random(seed)
    X = [[rng.gauss(0, 1) for _ in range(4)] for _ in range(n)]
    y = [1 if sum(x) > 0 else 0 for x in X]
    split = int(0.8 * n)
    return X[:split], y[:split], X[split:], y[split:]


def run_experiment(random_seed: int | None = None, **kwargs) -> tuple[float, str]:
    """Entry point called by the evaluator."""
    seed = random_seed or 42
    X_train, y_train, X_test, y_test = generate_dataset(n=200, seed=seed)
    accuracy = build_and_evaluate_model(X_train, y_train, X_test, y_test)
    return float(accuracy), f"Test accuracy: {accuracy:.4f}"
