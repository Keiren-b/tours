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


# %%
def load_clean_data():
    df = pd.read_csv(
        config.PROCESSED_DATA_DIR / "morning.csv",
        parse_dates=[config.DATE_COL],
    )
    df = df.sort_values(config.DATE_COL).set_index(config.DATE_COL, drop=True)
    return df.asfreq("D")
x = load_clean_data()


# %%
def cutoff_series(df):
    df = df.loc[:config.CUTOFF_DATE]
    assert df.index.max() == config.CUTOFF_DATE, f"data ends {df.index.max()}, expected {config.CUTOFF_DATE}"    
    return df
x = cutoff_series(x)
x
