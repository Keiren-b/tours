import logging
import sys

import pandas as pd

from tours import config
from tours.dataset import cutoff_series, fill_closed, load_clean_data, long_history, split_data
from tours.evaluate import evaluate
from tours.models import LONG_HISTORY_MODELS, MODELS, forecast
from tours.splits import assert_no_leakage, expanding_window_folds

logger = logging.getLogger(__name__)


def main(model_names=None):
    """Cross-validate the named models (default: all of them) on the dev period."""
    model_names = model_names or [*MODELS, *LONG_HISTORY_MODELS]
    df = cutoff_series(load_clean_data())
    dev_df, _ = split_data(df)  # the test period is never touched here

    actuals = dev_df["headcount"]  # NaN on closed days, so they're left out of the scores
    model_input = fill_closed(actuals)  # models need a complete series
    long_input = long_history(df)  # from 2018, covid gap left missing

    folds = expanding_window_folds(
        len(actuals), config.CV_INITIAL_WINDOW, config.FORECAST_HORIZON, config.CV_STEP
    )
    logger.info("%d folds from %s", len(folds), actuals.index[folds[0][0]].date())

    fold_rows, pred_rows = [], []
    for fold, (train_end, test_end) in enumerate(folds):
        y_train = model_input.iloc[:train_end]
        y_test = actuals.iloc[train_end:test_end]

        for name in model_names:
            if name in LONG_HISTORY_MODELS:
                train = long_input.loc[: y_train.index[-1]]  # same origin, more history
            else:
                train = y_train
            assert_no_leakage(train.index, y_test.index)
            try:
                preds = forecast(name, train, config.FORECAST_HORIZON)
            except Exception as e:
                logger.warning("fold %d, %s failed: %s", fold, name, e)
                continue

            scores = evaluate(
                preds, y_test, train_series=actuals.iloc[:train_end], season_length=7
            )
            fold_rows.append({"fold": fold, "model": name, "origin": y_test.index[0], **scores})
            pred_rows.append(
                pd.DataFrame(
                    {
                        "fold": fold,
                        "model": name,
                        "h": range(1, len(preds) + 1),
                        "date": preds.index,
                        "actual": y_test.to_numpy(),
                        "pred": preds.to_numpy(),
                    }
                )
            )

    per_fold = pd.DataFrame(fold_rows)
    summary = (
        per_fold.groupby("model")
        .agg(
            mase=("mase", "mean"),
            mase_sd=("mase", "std"),
            mae=("mae", "mean"),
            rmse=("rmse", "mean"),
            bias=("bias", "mean"),
        )
        .sort_values("mase")
    )
    logger.info("Model comparison (bias = pred - actual, positive = over-forecast):\n%s", summary)

    config.RESULTS_DIR.mkdir(exist_ok=True)
    per_fold.to_csv(config.RESULTS_DIR / "comparison_per_fold.csv", index=False)
    pd.concat(pred_rows).to_csv(config.RESULTS_DIR / "comparison_predictions.csv", index=False)
    summary.to_csv(config.RESULTS_DIR / "comparison_summary.csv")
    return summary


if __name__ == "__main__":
    # e.g. python -m tours.run_comparison prophet prophet_2018
    main(sys.argv[1:] or None)
