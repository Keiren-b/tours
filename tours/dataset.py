from pathlib import Path
import pandas as pd
import logging
from tqdm import tqdm
from tours import config




def load_clean_data():
    df = pd.read_csv(
        config.PROCESSED_DATA_DIR / "morning.csv",
        parse_dates=[config.DATE_COL],
    )
    df = df.sort_values(config.DATE_COL).set_index(config.DATE_COL, drop=True)
    return df.asfreq("D")

def cutoff_series(df):
    df = df.loc[:config.CUTOFF_DATE]
    assert df.index.max() == config.CUTOFF_DATE, f"data ends {df.index.max()}, expected {config.CUTOFF_DATE}"    
    return df


