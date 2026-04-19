from tactical_aa_research.purged_cv import purged_time_series_folds


def test_purged_folds_chronological_and_separated():
    folds = list(
        purged_time_series_folds(
            n=120,
            n_splits=4,
            purge_gap=6,
            embargo=2,
            min_train=24,
        )
    )
    assert folds, "Expected at least one fold"
    prev_test_start = -1
    for fd in folds:
        # train and test are non-overlapping and ordered
        assert fd.train_start == 0
        assert fd.train_end > fd.train_start
        assert fd.test_end > fd.test_start
        assert fd.train_end <= fd.test_start - (6 + 2)
        assert fd.test_start > prev_test_start
        prev_test_start = fd.test_start

