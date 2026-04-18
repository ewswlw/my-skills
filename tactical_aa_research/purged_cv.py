"""
Purged / embargoed time-series CV for monthly return series.

Walk-forward style: each fold's train is a strict prefix ending `purge_gap`
months before the test block; optional `embargo` months skipped after train
before test starts (serial correlation buffer).

Not sklearn-compatible; yields integer index ranges on 0..n-1.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass
class Fold:
    train_start: int
    train_end: int  # exclusive
    test_start: int
    test_end: int  # exclusive


def purged_time_series_folds(
    n: int,
    *,
    n_splits: int = 5,
    purge_gap: int = 12,
    embargo: int = 2,
    min_train: int = 36,
) -> Iterator[Fold]:
    """
    Split [0, n) into `n_splits` contiguous test blocks (last block may be longer).
    Train for fold k is [0, test_start - purge_gap - embargo) clipped to min_train minimum
    length by requiring test_start >= min_train + purge_gap + embargo.

    Yields folds in chronological test-block order.
    """
    if n < min_train + purge_gap + embargo + 24:
        raise ValueError(f"Series too short for n={n} splits={n_splits}")

    # test block boundaries (equal size except last)
    base = n // n_splits
    rem = n % n_splits
    edges = [0]
    for k in range(n_splits):
        sz = base + (1 if k < rem else 0)
        edges.append(edges[-1] + sz)

    for k in range(n_splits):
        ts, te = edges[k], edges[k + 1]
        if te - ts < 3:
            continue
        train_end = ts - purge_gap - embargo
        if train_end < min_train:
            continue
        yield Fold(train_start=0, train_end=train_end, test_start=ts, test_end=te)


def fold_train_test_masks(n: int, fold: Fold) -> tuple[slice, slice]:
    return slice(fold.train_start, fold.train_end), slice(fold.test_start, fold.test_end)
