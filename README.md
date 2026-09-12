# tours

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

a prediciton model for walking tour attendance

## Project Organization
REPLACE THIS FOLDER STRUCTURE

config.py — settings. Paths, split dates, seasonal periods, forecast horizons, the guide capacity. No logic, no functions, just values. The rule: if you catch yourself typing a date or a filepath anywhere else, it belongs here. Everything imports it; it imports nothing.

data.py — get the series into memory in a usable shape. Read the parquet or CSV your SQL produced, parse dates, set a proper daily index, pull out the target column. Also the guards: assert there are no missing days or duplicates. It does not clean — cleaning already happened in SQL.

splits.py — cut history into pieces. The three-way train/validation/test cut, and the rolling-origin folds for backtesting. Plus assert_no_leakage, which checks every fold's training window ends before its evaluation window starts. Small file, disproportionately important.

models.py — the candidates, all behind one interface: fit(history) then predict(horizon). Naive, seasonal naive, ARIMA. Plus the registry mapping names to model recipes. This is the file both entry points share, which is why it's central.

metrics.py — scoring functions. MAE, RMSE, MASE. And the staffing ones: days understaffed, days overstaffed, wasted guide-days. Pure functions — give them actuals and predictions, get a number. They know nothing about models.

evaluate.py — one model, one fold, one score. Build a fresh model, fit on the training slice, forecast forward, score against what happened, return a row of results. Also the summarising: average across folds, compare against baseline.

plots.py — figures. Forecast vs actual, error by horizon, the seasonal decomposition, model comparison. Every function takes data and returns or saves a figure. Keeping them here means the same chart looks the same everywhere and gets regenerated identically.

run_comparison.py — entry point one. Load, split, loop over models and folds calling evaluate, write the results file. Has main(). This is the experiment.

run_forecast.py — entry point two, written after you've picked a winner. Load everything up to today, fit the chosen model, forecast the next 30 days, write out the numbers and the guide counts. This is the product.

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         tours and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── tours   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes tours a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------

