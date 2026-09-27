def expanding_window_folds(n_obs, initial_window, horizon, step):
    """Rolling-origin folds as (train_end, test_end) positions.

    Fold k trains on rows [0, train_end) and forecasts rows [train_end, test_end).
    Folds stop once a full horizon no longer fits in the series.
    """
    folds = []
    train_end = initial_window
    while train_end + horizon <= n_obs:
        folds.append((train_end, train_end + horizon))
        train_end += step
    return folds


def assert_no_leakage(train_index, test_index):
    """Every training date must come before every evaluation date."""
    assert train_index.max() < test_index.min(), (
        f"training ends {train_index.max()}, evaluation starts {test_index.min()}"
    )
