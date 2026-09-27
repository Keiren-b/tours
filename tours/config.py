from pathlib import Path
import sys
from dotenv import load_dotenv
import logging
import datetime as dt
from dataclasses import dataclass
import pandas as pd

# Load environment variables from .env file if it exists
load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# logger.info(f"PROJ_ROOT path is: {PROJECT_ROOT}")

# FEATURE_TABLE = PROJECT_ROOT / "data" / "processed" / "features.parquet"
RESULTS_DIR = PROJECT_ROOT / "results"

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

MODELS_DIR = PROJECT_ROOT / "models"

REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

DATE_COL = "tour_date"
START_DATE = pd.Timestamp("2018-01-01")
CUTOFF_DATE = pd.Timestamp("2026-08-01")

POST_COVID_START = pd.Timestamp("2022-10-18")

# development: all model comparison and tuning (cross-validation folds live in here)
# test: held back, used once on the final chosen model
DEV_RANGE = [POST_COVID_START, pd.Timestamp("2026-01-31")]
TEST_RANGE = [pd.Timestamp("2026-02-01"), CUTOFF_DATE]

# rolling-origin cross-validation within the dev period
FORECAST_HORIZON = 30  # days forecast from each origin
CV_INITIAL_WINDOW = 806  # days in the first training window
CV_STEP = 30  # days the origin moves forward each fold

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

def setup_logging(level=logging.INFO):
    root = logging.getLogger()
    if root.handlers:  # already configured, don't duplicate handlers
        return

    root.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(LOG_DIR / "tours.log")
    file_handler.setFormatter(formatter)

    root.addHandler(console_handler)
    root.addHandler(file_handler)

setup_logging()