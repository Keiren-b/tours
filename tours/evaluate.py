import numpy as np
from tours.metrics import mae, rmse, bias, mase 

def evaluate(preds, actuals, train_series=None, season_length=1):
    """All metrics at once, as a dict ready for a comparison table."""
    out = {
        "mae": mae(preds, actuals),
        "rmse": rmse(preds, actuals),
        "bias": bias(preds, actuals),
    }
    if train_series is not None:
        out["mase"] = mase(preds, actuals, train_series, season_length)
    return out
