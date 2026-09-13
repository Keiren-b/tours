import numpy as np
import pandas as pd


def _align(preds, actuals):
    """Drop rows where either side is missing, return numpy arrays."""
    mask = preds.notna() & actuals.notna()
    return preds[mask].to_numpy(), actuals[mask].to_numpy()


def mae(preds, actuals):
    p, a = _align(preds, actuals)
    return float(np.abs(a - p).mean())


def rmse(preds, actuals):
    p, a = _align(preds, actuals)
    return float(np.sqrt(((a - p) ** 2).mean()))


def bias(preds, actuals):
    """Mean error, signed. Positive = over-forecasting."""
    p, a = _align(preds, actuals)
    return float((p - a).mean())


def mase(preds, actuals, train_series, season_length=1):
    """MAE scaled by the in-sample naive MAE. <1 beats the baseline."""
    p, a = _align(preds, actuals)
    naive_errors = np.abs(np.diff(train_series.dropna().to_numpy(), n=season_length))
    return float(np.abs(a - p).mean() / naive_errors.mean())


