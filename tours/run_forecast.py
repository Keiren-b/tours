"""Monthly forecast: train on all data up to the latest day, forecast the next month.

python -m tours.run_forecast                      # through the end of next month
python -m tours.run_forecast --until 2026-10-31   # a chosen end date
python -m tours.run_forecast --as-of 2026-07-31   # pretend the data ends earlier
"""

import argparse
import logging

import numpy as np
import pandas as pd

from tours import config
from tours.dataset import check_data, fill_closed, latest_date, load_clean_data
from tours.models import forecast, prophet_forecast

logger = logging.getLogger(__name__)


def default_end(last_date):
    """End of the month after the one the data ends in, so the next full month is covered."""
    return last_date + pd.offsets.MonthBegin(1) + pd.offsets.MonthEnd(0)


def is_closed(dates):
    closed = pd.to_datetime(config.CLOSED_DATES)
    return ((dates.month == 12) & (dates.day == 25)) | dates.isin(closed)


def guides_for(people, closed):
    """Guides to roster from the business's split points; 0 on closed days."""
    guides = 1 + np.searchsorted(config.GUIDE_THRESHOLDS, people, side="right")
    return np.where(closed, 0, guides).astype(int)


def main(as_of=None, until=None, model=config.FORECAST_MODEL):
    df = load_clean_data()
    last = pd.Timestamp(as_of) if as_of else latest_date(df)
    if last > config.DATA_END:
        raise ValueError(f"--as-of {last.date()} is after DATA_END {config.DATA_END.date()}")
    df = df.loc[:last]
    check_data(df)

    end = pd.Timestamp(until) if until else default_end(last)
    horizon = (end - last).days
    if horizon < 1:
        raise ValueError(f"--until {end.date()} must be after the last data day {last.date()}")
    if horizon > config.MAX_FORECAST_DAYS:
        logger.warning("Forecasting %d days ahead; models were only tested 30 days ahead", horizon)

    # post-covid only: longer history didn't improve accuracy in the comparison
    history = fill_closed(df["headcount"].loc[config.POST_COVID_START :])
    logger.info("Training %s on %s to %s", model, history.index[0].date(), last.date())

    dates = pd.date_range(last + pd.Timedelta(days=1), end, freq="D")
    out = pd.DataFrame({"date": dates, "day": dates.day_name()})
    if model == "prophet":
        pred = prophet_forecast(history, horizon)
        out["forecast"], out["low"], out["high"] = (
            pred["yhat"].to_numpy(),
            pred["yhat_lower"].to_numpy(),
            pred["yhat_upper"].to_numpy(),
        )
    else:  # other models give a single number, no range
        out["forecast"] = forecast(model, history, horizon).to_numpy()

    closed = is_closed(dates)
    value_cols = [c for c in ["forecast", "low", "high"] if c in out]
    out[value_cols] = out[value_cols].clip(lower=0).round(1)
    out.loc[closed, value_cols] = 0.0
    out["closed"] = closed
    out["guides_needed"] = guides_for(out["forecast"], closed)
    if "high" in out:
        out["guides_if_busy"] = guides_for(out["high"], closed)
    out["model"], out["trained_to"], out["made_on"] = (
        model,
        last.date(),
        pd.Timestamp.today().date(),
    )

    config.FORECASTS_DIR.mkdir(exist_ok=True)
    path = config.FORECASTS_DIR / f"forecast_{dates[0].date()}_to_{end.date()}.csv"
    out.to_csv(path, index=False)

    busiest = out.loc[out["forecast"].idxmax()]
    logger.info(
        "Forecast %s to %s: average %.0f people a day, busiest %s (%.0f people, guides needed: %d). Saved %s",
        dates[0].date(),
        end.date(),
        out.loc[~closed, "forecast"].mean(),
        busiest["date"].date(),
        busiest["forecast"],
        busiest["guides_needed"],
        path.relative_to(config.PROJECT_ROOT),
    )
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--as-of", help="last day of data to use (default: latest in the data)")
    parser.add_argument("--until", help="last day to forecast (default: end of next month)")
    parser.add_argument("--model", default=config.FORECAST_MODEL, help="a name from models.MODELS")
    args = parser.parse_args()
    main(args.as_of, args.until, args.model)
