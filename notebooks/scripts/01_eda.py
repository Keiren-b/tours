# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: .venv (3.13.12)
#     language: python
#     name: python3
# ---

# %% [markdown]
#  ## Initial EDA of cleaned series data
#

# %%
import sys
from pathlib import Path
import datetime as dt
import pandas as pd
from tours import config, dataset
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose, MSTL
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

from statsforecast import StatsForecast
from sktime.forecasting.model_selection import ExpandingWindowSplitter


# %%




# %%
df = dataset.load_clean_data()
df = dataset.cutoff_series(df)
train, val, split = dataset.split_data(df)

# %%
df.describe()

# %%
df.info()

# %%
fig = px.line(df["headcount"],title="Number of Attendees Jan 2018 - Aug 2026")
fig.show()

# %% [markdown]
# ## Whole Series Observation
#
# * There is a break from March 2020 to the beginning of 2022 that covers the covid period. Tours weren't running in this period so we don't have a complete series from 2018 onwards. Either we need to train only on the post-covid period or use a model that can account for this break in the time-series data
#
# * Spikes always occur around the chiristmas/New Year holiday
#
# * There appears to be a yearly seasonal effect. Highs in the summer period and lows in the winter period. Also secondary peaks around Mar/April for some years
#
#

# %%
fig = px.line(df[df["tour_year"]==2025]["headcount"],title="Number of Attendees 2025")
fig.show()

# %%
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
# drop covid period and christmas
df_drop = df[(df["covid_flag"]!="covid") & (df["xmas_flag"]==False)]
fig = px.box(
    df_drop,
    x=df_drop.index.day_name(),
    y="headcount",
    category_orders={"x": order},
    labels={"x": "weekday"},
    title="Attendance by day of week excl covid & xmas",
)
fig.show()

day_of_week_sd = df_drop.groupby(by="day_name")["headcount"].std()
day_of_week_mean = df_drop.groupby(by="day_name")["headcount"].mean()
day_of_week_stats = pd.DataFrame({"Standard Deviation":day_of_week_sd, "Mean": day_of_week_mean}).reindex(order)
day_of_week_stats

# %% [markdown]
# ## Weekly Seasonality
#
# * There is also weekly seasonality present in the data. We can see that weekends consistently show a smaller number of attendees.

# %%
df["rolling_mean_7d"] = df["headcount"].rolling("7D", min_periods=7).mean()
df["rolling_mean_30d"] = df["headcount"].rolling("30D", min_periods=30).mean()

fig = px.line(df[["rolling_mean_7d", "rolling_mean_30d"]],title="Number of Attendees Rolling Means")
fig.update_traces(opacity=0.35, line_width=1, selector=dict(name="headcount"))
fig.update_traces(line_width=2.5, selector=dict(name="rolling_mean_30d"))
fig.show()

# %% [markdown]
# ## When does the series recover in 2022?

# %%
fig = px.line(df[df["tour_year"]==2022]["headcount"],title="Number of Attendees 2022")
fig.show()

zero_days = pd.Series(df[(df["headcount"]==0) & (df["tour_year"]==2022)].index)
print(zero_days)


# %% [markdown]
# * Excluding Christmas, 2022 had 135 days where the tour didn't run or attendance was zero. 
# * It only gets to a more consistent pattern after 17 October
# * If we are really conservative, we can cut the series to run only from 17 Oct 2022 to end of series
# * further exploration at this point will be based on the post Oct 17 2022 period

# %% [markdown]
# ## Seasonal Decomposition

# %%
post_covid_df = df[df["covid_flag"]=="post_covid"]
result = seasonal_decompose(post_covid_df["headcount"], model='additive', period=365)

fig = make_subplots(rows=4, cols=1, shared_xaxes=True, 
                     subplot_titles=("Headcount", "Trend", "Seasonal (yearly)", "Residual"))

fig.add_trace(go.Scatter(x=post_covid_df.index, y=post_covid_df["headcount"] , name="Headcount"), row=1, col=1)
fig.add_trace(go.Scatter(x=result.trend.index, y=result.trend, name="Trend"), row=2, col=1)
fig.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal, name="Seasonality"), row=3, col=1)
fig.add_trace(go.Scatter(x=result.resid.index, y=result.resid, name="Residual"), row=4, col=1)

fig.update_layout(height=1200, width=1000, title_text = "Yearly Seasonality Post Covid")
fig.update_xaxes(showticklabels=True)
fig.show()



# %%
# post_covid_df.loc[post_covid_df["xmas_flag"], "headcount"] = np.nan
# post_covid_df["headcount"] = post_covid_df["headcount"].ffill()

mstl_result = MSTL(post_covid_df["headcount"], periods=(7,365)).fit()
mstl_result.seasonal["seasonal_7"]

fig = make_subplots(rows=5, cols=1, shared_xaxes=True, 
                     subplot_titles=("Headcount", "Trend", "Seasonal (7)", "Seasonal (365)", "Residual"))

fig.add_trace(go.Scatter(x=post_covid_df.index, y=post_covid_df["headcount"] , name="Headcount"), row=1, col=1)
fig.add_trace(go.Scatter(x=mstl_result.trend.index, y=mstl_result.trend, name="Trend"), row=2, col=1)
fig.add_trace(go.Scatter(x=mstl_result.seasonal.index, y=mstl_result.seasonal["seasonal_7"], name="Seasonal 7"), row=3, col=1)
fig.add_trace(go.Scatter(x=mstl_result.seasonal.index, y=mstl_result.seasonal["seasonal_365"], name="Seasonal 365"), row=4, col=1)
fig.add_trace(go.Scatter(x=mstl_result.resid.index, y=mstl_result.resid, name="Residual"), row=5, col=1)

fig.update_layout(height=1200, width=1000, title_text = "MSTL Seasonality Post Covid")
fig.update_xaxes(showticklabels=True)
fig.show()

                   

# %%
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(14, 5))

plot_acf(post_covid_df["headcount"].dropna(), lags=40, ax=axes[0][0])
axes[0][0].set_title("Headcount ACF")

plot_pacf(post_covid_df["headcount"].dropna(), lags=40, method="ywm", ax=axes[0][1])
axes[0][1].set_title("Headcount PACF")

plot_acf(mstl_result.resid.dropna(), lags=40, ax=axes[1][0])
axes[1][0].set_title("MSTL Residual ACF")

plot_pacf(mstl_result.resid.dropna(), lags=40, method="ywm", ax=axes[1][1])
axes[1][1].set_title("MSTL Residual PACF")

plt.tight_layout()
plt.show()




# %%
pre_covid_df = df[df["covid_flag"]=="pre_covid"]
result = seasonal_decompose(pre_covid_df["headcount"], model='additive', period=7)

fig = make_subplots(rows=4, cols=1, shared_xaxes=True, 
                     subplot_titles=("Headcount", "Trend", "Seasonal (yearly)", "Residual"))

fig.add_trace(go.Scatter(x=pre_covid_df.index, y=pre_covid_df["headcount"] , name="Headcount"), row=1, col=1)
fig.add_trace(go.Scatter(x=result.trend.index, y=result.trend, name="Trend"), row=2, col=1)
fig.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal, name="Seasonality"), row=3, col=1)
fig.add_trace(go.Scatter(x=result.resid.index, y=result.resid, name="Residual"), row=4, col=1)

fig.update_layout(height=1200, width=1000, title_text = "Yearly Seasonality Pre Covid")
fig.update_xaxes(showticklabels=True)
fig.show()


# %%
px.line(pre_covid_df["headcount"])

# %%
num_rows = df.shape[0]
train = df[df.tour_year < 2025]
val = df[df.tour_year == 2025]
test = df[df.tour_year == 2026]

print(f'full df num rows: {num_rows}\n train num rows: {len(train)}\ntrain perc: {len(train)/num_rows*100}\n')
print(f'full df num rows: {num_rows}\n val num rows: {len(val)}\n val perc: {len(val)/num_rows*100}\n')
print(f'full df num rows: {num_rows}\n test num rows: {len(test)}\n test perc: {len(test)/num_rows*100}')


# %%
# TRAIN_RANGE = [config.START_DATE, "2023-12-31"]
# VAL_RANGE = ["2024-01-01", "2025-04-30"]
# TEST_RANGE = ["2025-05-01", config.CUTOFF_DATE]
import logging
logger = logging.getLogger(__name__)


def split_data(df):
    train_df = df.loc[config.TRAIN_RANGE[0]: config.TRAIN_RANGE[1]]
    val_df = df.loc[config.VAL_RANGE[0]: config.VAL_RANGE[1]]
    test_df = df.loc[config.TEST_RANGE[0]: config.TEST_RANGE[1]]

    logger.info("Train df runs from %s to %s", train_df.index[0], train_df.index[-1]) 
    logger.info("Val df runs from %s to %s", val_df.index[0], val_df.index[-1]) 
    logger.info("Test df runs from %s to %s", test_df.index[0], test_df.index[-1]) 


    return (train_df, val_df, test_df)

train, val, test = split_data(df)
train.head()
val.head()
test.head()


# %%
post_covid_df_count = post_covid_df.reset_index(names="date")[["date","headcount"]]
post_covid_df_count["date"] = pd.to_datetime(post_covid_df_count["date"])


train_df = post_covid_df_count.rename(columns={"date": "ds", "headcount": "y"})
train_df["unique_id"] = "store_001"
train_df = train_df[["unique_id", "ds", "y"]]

# %%
from statsforecast import StatsForecast
from statsforecast.models import (
    AutoARIMA,
    AutoETS,
    AutoCES,
    SeasonalNaive
)

# StatsForecast expects a specific DataFrame format:
# columns: unique_id, ds (timestamp), y (target)
# train_df = post_covid_df_count.reset_index().rename(columns={
#     "date": "ds",
#     "headcount": "y"
# })
# train_df["unique_id"] = "store_001"
# print(train_df)
# Define models to compare
models = [
    AutoARIMA(season_length=7),    # Weekly seasonality
    AutoETS(season_length=7),       # Exponential smoothing
    AutoCES(season_length=7),       # Complex exponential smoothing
    SeasonalNaive(season_length=7)  # Baseline
]

# Fit and forecast
sf = StatsForecast(
    models=models,
    freq="D",    # Daily frequency
    n_jobs=-1    # Use all CPU cores
)

sf.fit(train_df)
forecasts = sf.predict(h=30, level=[90])  # 30-day forecast with 90% CI

print(forecasts.head())

# %%
m = len(post_covid_df)
n = len(post_covid_df[post_covid_df["tour_year"]==2026])
print(f'There are {m} rows in the post covid dataset\nThere are {n} in 2026\nUse {m-n} rows for training')

cv = ExpandingWindowSplitter(
    fh=range(1, 31),
    initial_window=730,
    step_length=30,
)

# %%
x = cv_results.groupby("unique_id")


# %%
model_cols = ["AutoARIMA", "AutoETS", "CES", "SeasonalNaive"]

errors = cv_results[model_cols].sub(cv_results["y"], axis=0)
abs_err = errors.abs()

# headline: one number per model
print(abs_err.mean().sort_values())

# %%
# by horizon: how fast does accuracy decay over the 30 days?
h = (cv_results["ds"] - cv_results["cutoff"]).dt.days
print(abs_err.groupby(h).mean())

# by fold: is the winner consistent, or driven by one window?
print(abs_err.groupby(cv_results["cutoff"]).mean())

print(abs_err.mean() / abs_err["SeasonalNaive"].mean())
