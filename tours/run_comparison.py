from tours.dataset import load_clean_data, cutoff_series, split_data
from tours.models import naive_forecast, seasonal_forecast
import pandas as pd

def main():
    df = load_clean_data()
    df = cutoff_series(df)
    train_df, val_df, test_df = split_data(df)
    naive_model_val = naive_forecast(train_df=train_df,
                                     forecast_index=val_df.index)
    naive_model_test = naive_forecast(train_df=train_df,
                                    forecast_index=test_df.index)
    naive_seasonal_weekly_val = seasonal_forecast(df,
                                                  val_df.index,
                                                  pd.DateOffset(weeks=1))
    naive_seasonal_weekly_test = seasonal_forecast(df,
                                                  test_df.index,
                                                  pd.DateOffset(weeks=1))
    naive_seasonal_yearly_val = seasonal_forecast(df,
                                                  val_df.index,
                                                  pd.DateOffset(years=1))
    naive_seasonal_yearly_test = seasonal_forecast(df,
                                                  test_df.index,
                                                  pd.DateOffset(years=1))


if __name__ == "__main__":
    main()