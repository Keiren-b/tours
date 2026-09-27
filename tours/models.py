import logging

import lightgbm as lgb
import numpy as np
import pandas as pd
from prophet import Prophet
from statsforecast.models import MSTL, AutoARIMA, AutoETS
from statsmodels.tsa.statespace.sarimax import SARIMAX

from tours import config
from tours.features import calendar_features, lag_features

logger = logging.getLogger(__name__)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)  # prophet's backend is chatty

# Every model takes a complete daily training series (no NaN) and a horizon,
# and returns a numpy array of `horizon` predictions for the days after it.


def future_dates(y_train, horizon):
    return pd.date_range(y_train.index[-1] + pd.Timedelta(days=1), periods=horizon, freq="D")


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


def fit_arimax(y_train, horizon):
    """AutoARIMA (weekly season) plus holiday flags and yearly Fourier terms."""
    X_train = calendar_features(y_train.index)
    X_future = calendar_features(future_dates(y_train, horizon))
    keep = X_train.columns[X_train.nunique() > 1]  # a constant column can't be estimated
    model = AutoARIMA(season_length=7).fit(
        y_train.to_numpy(dtype=float), X=X_train[keep].to_numpy(dtype=float)
    )
    return model.predict(h=horizon, X=X_future[keep].to_numpy(dtype=float))["mean"]


def fit_autoets(y_train, horizon):
    model = AutoETS(season_length=7).fit(y_train.to_numpy(dtype=float))
    return model.predict(h=horizon)["mean"]


def fit_mstl(y_train, horizon):
    """Weekly and yearly patterns split out, trend forecast with ETS."""
    model = MSTL(season_length=[7, 365], trend_forecaster=AutoETS(model="ZZN"))
    return model.fit(y_train.to_numpy(dtype=float)).predict(h=horizon)["mean"]


def pre_covid_flag(dates):
    """1 before covid: that era's source counted attendance, later ones count bookings."""
    return (dates < config.COVID_START).astype(float)


def fit_lightgbm(y_train, horizon):
    """Gradient-boosted trees on calendar features and past values.

    Lags start at `horizon` days back so every forecast day can be built from
    data known at the origin (a "direct" model, no feeding predictions back in).
    """
    dates = y_train.index.append(future_dates(y_train, horizon))
    y_all = y_train.reindex(dates)  # future days are NaN
    X = pd.concat([calendar_features(dates), lag_features(y_all, min_lag=horizon)], axis=1).assign(
        day_of_week=dates.dayofweek, pre_covid=pre_covid_flag(dates)
    )
    model = lgb.LGBMRegressor(
        n_estimators=300, learning_rate=0.05, num_leaves=15, min_child_samples=20, verbose=-1
    )
    known = y_train.notna().to_numpy()  # long history has a missing covid period
    model.fit(X.iloc[: len(y_train)][known], y_train[known])
    return model.predict(X.iloc[len(y_train) :])


def prophet_holidays(years):
    days = []
    for year in years:
        days.append(("xmas_day", f"{year}-12-25"))
        days.append(("new_years_day", f"{year}-01-01"))
        days += [("new_year_period", f"{year}-12-{d}") for d in range(26, 32)]
        days.append(("new_year_period", f"{year}-01-02"))
    return pd.DataFrame(days, columns=["holiday", "ds"]).assign(ds=lambda d: pd.to_datetime(d.ds))


def prophet_forecast(y_train, horizon):
    """Trend + weekly and yearly seasonality + Christmas/New Year holidays.

    Returns yhat plus yhat_lower / yhat_upper, an 80% range for each day.
    """
    years = range(y_train.index[0].year, y_train.index[-1].year + 2)
    model = Prophet(
        weekly_seasonality=True,
        yearly_seasonality=True,
        daily_seasonality=False,
        holidays=prophet_holidays(years),
    )
    history = pd.DataFrame({"ds": y_train.index, "y": y_train.to_numpy()}).dropna()
    future = pd.DataFrame({"ds": future_dates(y_train, horizon)})
    if (
        history.ds.min() < config.COVID_START
    ):  # long history: let the pre-covid era have its own level
        model.add_regressor("pre_covid")
        history["pre_covid"] = pre_covid_flag(history.ds)
        future["pre_covid"] = 0.0
    model.fit(history)
    return model.predict(future)[["yhat", "yhat_lower", "yhat_upper"]]


def fit_prophet(y_train, horizon):
    return prophet_forecast(y_train, horizon)["yhat"].to_numpy()


MODELS = {
    "naive": fit_naive,
    "seasonal_7d_naive": fit_7d_seasonal_naive,
    "seasonal_365d_naive": fit_365d_seasonal_naive,
    "sarima": fit_sarima,
    "auto_arima": fit_autoarima,
    "arimax": fit_arimax,
    "autoets": fit_autoets,
    "mstl": fit_mstl,
    "lightgbm": fit_lightgbm,
    "prophet": fit_prophet,
}

# Same models, but trained on everything from 2018 (see dataset.long_history)
LONG_HISTORY_MODELS = {
    "lightgbm_2018": fit_lightgbm,
    "prophet_2018": fit_prophet,
}


def forecast(name, y_train, horizon):
    """Fit model `name` on y_train and return a dated Series of predictions."""
    preds = {**MODELS, **LONG_HISTORY_MODELS}[name](y_train, horizon)
    return pd.Series(np.asarray(preds), index=future_dates(y_train, horizon))
