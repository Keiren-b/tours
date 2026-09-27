# tours

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

A prediction model for walking tour attendance: daily bookings for the 10:30am Sydney Sights tour,
forecast a month ahead so guides can be rostered.

## Project organisation

```
├── Makefile                <- make compare / forecast / plots / lint / format
├── requirements.txt
├── pyproject.toml          <- package metadata and ruff settings
├── sql/
│   └── 00_clean.sql        <- raw spreadsheets -> cleaned daily table -> data/processed/morning.csv
├── data/
│   ├── raw/                <- original spreadsheets (not in git)
│   └── processed/
│       └── morning.csv     <- one row per day: headcount, covid_flag, xmas_flag, operating_status
├── notebooks/              <- exploration (paired with notebooks/scripts/ by jupytext)
│   ├── 01_eda.ipynb
│   ├── 02_arima_tests.ipynb
│   ├── 03_port_schedule.py <- cruise ship schedule scraper (not used by the models yet)
│   └── scripts/            <- .py versions of the notebooks
├── reports/figures/        <- saved charts
├── tours/                  <- the package (below)
├── results/                <- model comparison output (not in git)
└── forecasts/              <- monthly forecast output (not in git)
```

## The `tours` package

- **config.py**: settings only. Paths, the development/test dates, forecast horizon, fold sizes,
  Fourier settings, the forecast model and the guide split points. If you find yourself typing a
  date or a file path anywhere else, it belongs here.
- **dataset.py**: loads `morning.csv` into a daily series; cut-off and dev/test split; fills
  closed days for models that need a complete series; data checks.
- **features.py**: inputs known in advance: Christmas and New Year flags, yearly Fourier terms,
  and past values (lags) for LightGBM.
- **models.py**: every model, one function each, plus the `MODELS` list of names. Each takes a
  training series and a horizon and returns that many days of predictions.
- **splits.py**: the rolling-origin folds, and a check that training never overlaps evaluation.
- **metrics.py**: MAE, RMSE, bias and MASE. Pure functions of predictions and actuals.
- **evaluate.py**: all the metrics for one set of predictions.
- **run_comparison.py**: the experiment. Cross-validates every model on the development period
  and writes the scores and predictions to `results/`.
- **run_forecast.py**: the product. Trains the chosen model (Prophet) on all data up to the
  latest day and forecasts the next month, with guides needed, to `forecasts/`.
- **plots.py**: figures, e.g. a model's forecasts against actual bookings.

## How to run

1. Install: `make requirements` (on a Mac, LightGBM also needs OpenMP:
   `conda install -c conda-forge llvm-openmp` or `brew install libomp`).
2. Build the data: run `sql/00_clean.sql` in DuckDB to refresh `data/processed/morning.csv`.
3. Compare models: `make compare`. Pass model names to run only some:
   `python -m tours.run_comparison prophet lightgbm`.
4. Forecast: `make forecast`. Options: `--until 2026-10-31`, `--as-of 2026-07-31`,
   `--model lightgbm`.
5. Chart: `make plots`, or `python -m tours.plots lightgbm` for another model.
