import logging

import numpy as np
import pandas as pd
from statsforecast.models import AutoARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

logger = logging.getLogger(__name__)

# Every model takes a complete daily training series (no NaN) and a horizon,
# and returns a numpy array of `horizon` predictions for the days after it.


def fit_naive(y_train, horizon):
    return np.repeat(y_train.iloc[-1], horizon)


def fit_7d_seasonal_naive(y_train, horizon):
    last_week = y_train.to_numpy()[-7:]
    return np.tile(last_week, int(np.ceil(horizon / 7)))[:horizon]


def fit_365d_seasonal_naive(y_train, horizon):
    return y_train.to_numpy()[-365:][:horizon]


def fit_sarima(y_train, horizon):
    model = SARIMAX(
        y_train.to_numpy(),
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 7),
    ).fit(disp=False)
    return np.asarray(model.forecast(steps=horizon))


def fit_autoarima(y_train, horizon):
    model = AutoARIMA(season_length=7).fit(y_train.to_numpy(dtype=float))
    return model.predict(h=horizon)["mean"]


MODELS = {
    "naive": fit_naive,
    "seasonal_7d_naive": fit_7d_seasonal_naive,
    "seasonal_365d_naive": fit_365d_seasonal_naive,
    "sarima": fit_sarima,
    "auto_arima": fit_autoarima,
}


def forecast(name, y_train, horizon):
    """Fit model `name` on y_train and return a dated Series of predictions."""
    preds = MODELS[name](y_train, horizon)
    index = pd.date_range(y_train.index[-1] + pd.Timedelta(days=1), periods=horizon, freq="D")
    return pd.Series(preds, index=index)
