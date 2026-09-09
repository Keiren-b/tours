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
def load_clean_data(data):
    return pd.read_csv(data)

clean_df = load_clean_data(config.PROCESSED_DATA_DIR / "morning.csv")
clean_df.head(10)
