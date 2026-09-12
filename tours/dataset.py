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
    df = df.loc[:config.CUTOFF_DATE]
    assert df.index.max() == config.CUTOFF_DATE, f"data ends {df.index.max()}, expected {config.CUTOFF_DATE}"    
    return df

def split_data(df):
    train_df = df.loc[config.TRAIN_RANGE[0]: config.TRAIN_RANGE[1]]
    val_df = df.loc[config.VAL_RANGE[0]: config.VAL_RANGE[1]]
    test_df = df.loc[config.TEST_RANGE[0]: config.TEST_RANGE[1]]

    logger.info("Train df runs from %s to %s", train_df.index[0], train_df.index[-1]) 
    logger.info("Val df runs from %s to %s", val_df.index[0], val_df.index[-1]) 
    logger.info("Test df runs from %s to %s", test_df.index[0], test_df.index[-1]) 


    return (train_df, val_df, test_df)

