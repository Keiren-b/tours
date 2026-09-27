from pathlib import Path
import pandas as pd
import logging
from tqdm import tqdm
from tours import config

logger = logging.getLogger(__name__)


def load_clean_data():
    df = pd.read_csv(
        config.PROCESSED_DATA_DIR / "morning.csv",
        parse_dates=[config.DATE_COL],
    )
    df = df.sort_values(config.DATE_COL).set_index(config.DATE_COL, drop=True)
    return df.asfreq("D")


def cutoff_series(df):
    df = df.loc[: config.CUTOFF_DATE]
    assert df.index.max() == config.CUTOFF_DATE, (
        f"data ends {df.index.max()}, expected {config.CUTOFF_DATE}"
    )
    return df


def fill_closed(series):
    """Fill missing (closed) days with the value from the same weekday the week before.

    For models that can't take NaN. Only use on training data: score against the
    unfilled actuals so closed days are left out of the metrics.
    """
    filled = series.copy()
    while filled.isna().any():
        before = filled.isna().sum()
        filled = filled.fillna(filled.shift(7))
        if filled.isna().sum() == before:  # nothing a week earlier, e.g. at the start
            filled = filled.ffill().bfill()
    return filled


def long_history(df):
    """Headcount from START_DATE with the covid period and Christmas Day as missing.

    For models that can train across the gap (Prophet, LightGBM). Pre-covid values
    are counted attendance, post-covid are bookings, so pair it with an era flag.
    """
    y = df["headcount"].loc[config.START_DATE :].copy()
    covid = (y.index >= config.COVID_START) & (y.index < config.POST_COVID_START)
    y[covid | df["xmas_flag"].loc[y.index].astype(bool)] = float("nan")
    return y


def latest_date(df):
    """Last day with a recorded headcount."""
    return df["headcount"].last_valid_index()


def check_data(df):
    """Stop on broken data; warn when recent bookings look unusually low."""
    assert df.index.is_unique, "duplicate dates in the data"
    assert (df.index.to_series().diff().dropna() == pd.Timedelta(days=1)).all(), "gap in the dates"
    if "operating_status" in df.columns:
        missing = df.index[df["headcount"].isna() & (df["operating_status"] != "closed")]
        assert missing.empty, f"no headcount on open days: {list(missing.date)[:10]}"

    last = df.index[-1]
    recent = df["headcount"].loc[last - pd.Timedelta(days=27) : last].mean()
    year_ago = df["headcount"].loc[
        last - pd.Timedelta(days=27 + 364) : last - pd.Timedelta(days=364)
    ]
    if year_ago.notna().any() and recent < config.DROP_WARNING_RATIO * year_ago.mean():
        logger.warning(
            "Last 4 weeks average %.1f a day vs %.1f a year earlier: check the data is complete",
            recent,
            year_ago.mean(),
        )


def split_data(df):
    dev_df = df.loc[config.DEV_RANGE[0] : config.DEV_RANGE[1]]
    test_df = df.loc[config.TEST_RANGE[0] : config.TEST_RANGE[1]]

    logger.info("Dev df runs from %s to %s", dev_df.index[0], dev_df.index[-1])
    logger.info("Test df runs from %s to %s", test_df.index[0], test_df.index[-1])

    return (dev_df, test_df)
