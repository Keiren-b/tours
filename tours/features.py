import numpy as np
import pandas as pd

from tours import config

# Exogenous (external) features: things known in advance for any date,
# so they can be built for the forecast days as well as the training days.


def holiday_flags(dates):
    """0/1 columns for the Christmas and New Year effects."""
    month, day = dates.month, dates.day
    return pd.DataFrame(
        {
            "xmas_day": (month == 12) & (day == 25),
            # 26 Dec to 2 Jan is the peak, except New Year's Day itself which is quiet
            "new_year_period": ((month == 12) & (day >= 26)) | ((month == 1) & (day == 2)),
            "new_years_day": (month == 1) & (day == 1),
        },
        index=dates,
    ).astype(float)


def fourier_terms(dates, period=config.YEAR_LENGTH, k=config.FOURIER_K):
    """Sine/cosine pairs that let a linear model draw a smooth yearly curve.

    Time is counted from a fixed origin so the same date always gets the same
    values, whichever window it's in.
    """
    t = (dates - config.FOURIER_ORIGIN).days.to_numpy()
    cols = {}
    for i in range(1, k + 1):
        cols[f"sin_{i}"] = np.sin(2 * np.pi * i * t / period)
        cols[f"cos_{i}"] = np.cos(2 * np.pi * i * t / period)
    return pd.DataFrame(cols, index=dates)


def calendar_features(dates):
    return pd.concat([holiday_flags(dates), fourier_terms(dates)], axis=1)


def lag_features(y, min_lag):
    """Past headcounts, only from at least `min_lag` days back.

    With min_lag = forecast horizon, every forecast day only uses values that
    were already known on the forecast origin, so there's no leakage.
    """
    first_weekly = int(np.ceil(min_lag / 7) * 7)  # same weekday, far enough back
    return pd.DataFrame(
        {
            f"lag_{first_weekly}": y.shift(first_weekly),
            f"lag_{first_weekly + 7}": y.shift(first_weekly + 7),
            "lag_364": y.shift(364),
            "rolling_mean_28": y.shift(min_lag).rolling(28).mean(),
        },
        index=y.index,
    )
