import pandas as pd
import logging

logger = logging.getLogger(__name__)


def naive_forecast(train_df, forecast_index, target_col="headcount"):
    last_value = train_df[target_col].iloc[-1]
    logger.info("Naive forecast: last value = %s", last_value)
    return pd.Series(last_value, index=forecast_index)

def seasonal_forecast(df, forecast_index, offset, target_col="headcount"):
    """Predicts each date's value using the value at (date - offset).
    
    offset: a pd.DateOffset, e.g. pd.DateOffset(years=1) for yearly 
            seasonality or pd.DateOffset(weeks=1) for weekly seasonality.
    """
    prior_dates = forecast_index - offset
    return pd.Series(df[target_col].reindex(prior_dates).values, index=forecast_index)


