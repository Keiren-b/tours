from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
import datetime as dt
from dataclasses import dataclass
import pandas as pd

# Load environment variables from .env file if it exists
load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
logger.info(f"PROJ_ROOT path is: {PROJECT_ROOT}")

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

TRAIN_RANGE = [START_DATE, "2023-12-31"]
VAL_RANGE = ["2024-01-01", "2025-04-30"]
TEST_RANGE = ["2025-05-01", CUTOFF_DATE]

# If tqdm is installed, configure loguru with tqdm.write
# https://github.com/Delgan/loguru/issues/135
try:
    from tqdm import tqdm

    logger.remove(0)
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)
except ModuleNotFoundError:
    pass
