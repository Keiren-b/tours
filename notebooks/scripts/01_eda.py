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
from tours import config
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose


# %%
from tours import dataset
import plotly.express as px


# %%
df = dataset.load_clean_data()
df = dataset.cutoff_series(df)
df.head()

# %%
df.describe()

# %%
df.info()

# %%
fig = px.line(df["headcount"],title="Number of Attendees Jan 2018 - Aug 2026")
fig.show()

# %% [markdown]
# Looks like there is a yearly seasonal pattern, and possibly a weekly one too.
# Spikes around Christmas new year, secondary spike around April/May? 
# Also weekly seasonality?

# %%
num_rows = df.shape[0]
train = df[df.tour_year < 2025]
val = df[df.tour_year == 2025]
test = df[df.tour_year == 2026]

print(f'full df num rows: {num_rows}\n train num rows: {len(train)}\ntrain perc: {len(train)/num_rows*100}')\n
print(f'full df num rows: {num_rows}\n val num rows: {len(val)}\val perc: {len(val)/num_rows*100}')
print(f'full df num rows: {num_rows}\n test num rows: {len(test)}\n test perc: {len(test)/num_rows*100}')


# %%
from statsmodels.tsa.seasonal import seasonal_decompose
from plotly.subplots import make_subplots
import plotly.graph_objects as go

result = seasonal_decompose(df["headcount"], model='additive', period=365)

fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                     subplot_titles=("Trend", "Seasonal (yearly)", "Residual"))

fig.add_trace(go.Scatter(x=result.trend.index, y=result.trend, name="Trend"), row=1, col=1)
fig.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal, name="Seasonality"), row=2, col=1)
fig.add_trace(go.Scatter(x=result.resid.index, y=result.resid, name="Residual"), row=3, col=1)

fig.update_layout(height=700, width=1000, title_text = "Yearly Seasonality")
fig.show()



# %%
from statsmodels.tsa.seasonal import MSTL

mstl = MSTL(df["headcount"], periods=[7, 365])
result = mstl.fit()

fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                     subplot_titles=("Trend", "Seasonal (weekly)", "Seasonal (yearly)", "Residual"))

fig.add_trace(go.Scatter(x=result.trend.index, y=result.trend, name="Trend"), row=1, col=1)
fig.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal["seasonal_7"], name="Weekly"), row=2, col=1)
fig.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal["seasonal_365"], name="Yearly"), row=3, col=1)
fig.add_trace(go.Scatter(x=result.resid.index, y=result.resid, name="Residual"), row=4, col=1)

fig.update_layout(height=1200, width=1000, title_text="MSTL Decomposition (weekly + yearly)")
fig.show()

# %%
fig_zoom = go.Figure()
fig_zoom = make_subplots(rows=2, cols=1, shared_xaxes=True,
                     subplot_titles=("Trend", "Seasonal (weekly)", "Seasonal (yearly)", "Residual"))
fig_zoom.add_trace(go.Scatter(
    x=result.seasonal.index[:180],
    y=result.seasonal["seasonal_7"].iloc[:180],
    mode="lines",
    name = "1st 180 days"
    
))
fig_zoom.add_trace(go.Scatter(
    x=result.seasonal.index[-180:],
    y=result.seasonal["seasonal_7"].iloc[-180:],
    mode="lines"
))
fig_zoom.update_layout(title="Weekly seasonality (zoomed, first 180 days)")
fig_zoom.show()

# %%
import pandas as pd
import plotly.express as px

year_mth_avg = df.groupby(["tour_year", "tour_month"])["headcount"].mean().reset_index()

# Make sure month order is correct (1-12), not alphabetical
year_mth_avg = year_mth_avg.sort_values(["tour_year", "tour_month"])

fig = px.line(
    year_mth_avg,
    x="tour_month",
    y="headcount",
    color="tour_year",  # <-- one line per year
    markers=True
)

fig.update_xaxes(
    tickmode="array",
    tickvals=list(range(1, 13)),
    ticktext=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
)

fig.update_layout(
    title="Seasonal pattern by year",
    xaxis_title="Month",
    yaxis_title="Average headcount",
    legend_title="Year"
)

fig.show()

# %%
from statsmodels.tsa.seasonal import MSTL
import plotly.express as px

df["headcount"] = df["headcount"].fillna(0)  # or .interpolate(), depending on what missing means

mstl = MSTL(df["headcount"], periods=[7, 365])
result = mstl.fit()

# Weekly pattern
fig1 = px.line(result.seasonal["seasonal_7"].iloc[:60], title="Weekly seasonality (first 60 days)")
fig1.show()

# Yearly pattern
fig2 = px.line(result.seasonal["seasonal_365"], title="Yearly seasonality")
fig2.show()
