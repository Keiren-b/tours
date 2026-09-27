"""Figures. Each function takes data and returns a plotly figure.

    python -m tours.plots                    # every model in results/comparison_predictions.csv
    python -m tours.plots prophet lightgbm   # just these models

Charts are saved to reports/figures/models/ as .html (interactive) and .png (static).
"""

import logging
import sys

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from tours import config

logger = logging.getLogger(__name__)
for noisy in ("kaleido", "choreographer"):  # the PNG exporter logs every step
    logging.getLogger(noisy).setLevel(logging.WARNING)

MODEL_NAMES = {
    "naive": "Same as yesterday",
    "seasonal_7d_naive": "Same weekday last week",
    "seasonal_365d_naive": "Same day last year",
    "sarima": "SARIMA",
    "auto_arima": "AutoARIMA",
    "arimax": "ARIMAX",
    "autoets": "AutoETS",
    "mstl": "MSTL",
    "lightgbm": "LightGBM",
    "prophet": "Prophet",
    "lightgbm_2018": "LightGBM (trained from 2018)",
    "prophet_2018": "Prophet (trained from 2018)",
}
ACTUAL_COLOUR, FORECAST_COLOUR, GUIDE_COLOUR = "#636EFA", "#EF553B", "grey"  # plotly defaults


def plot_forecast_vs_actual(predictions, model):
    """Daily forecast vs actual over time (left) and forecast against actual per day (right).

    predictions: rows of (model, date, actual, pred), as in comparison_predictions.csv.
    Christmas Day (closed) is left as a gap.
    """
    p = predictions[predictions["model"] == model].copy()
    if p.empty:
        raise ValueError(f"no predictions for model {model!r}")
    p["date"] = pd.to_datetime(p["date"])
    p = p.sort_values("date").set_index("date")
    xmas = (p.index.month == 12) & (p.index.day == 25)
    p.loc[xmas, ["actual", "pred"]] = None
    name = MODEL_NAMES.get(model, model)
    mae = (p["pred"] - p["actual"]).abs().mean()
    top = max(p["actual"].max(), p["pred"].max()) * 1.05

    fig = make_subplots(
        rows=1,
        cols=2,
        column_widths=[0.7, 0.3],
        horizontal_spacing=0.08,
        subplot_titles=("Forecast vs actual, by day", "Each dot is one day"),
    )

    # left: over time
    fig.add_trace(
        go.Scatter(
            x=p.index,
            y=p["actual"],
            name="Actual",
            line=dict(color=ACTUAL_COLOUR),
            hovertemplate="%{x|%a %d %b %Y}<br>actual %{y:.0f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=p.index,
            y=p["pred"],
            name=f"{name} forecast",
            line=dict(color=FORECAST_COLOUR),
            hovertemplate="%{x|%a %d %b %Y}<br>forecast %{y:.0f}<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # right: forecast against actual; dots on the dashed line are perfect forecasts
    fig.add_trace(
        go.Scatter(
            x=p["actual"],
            y=p["pred"],
            mode="markers",
            marker=dict(color=ACTUAL_COLOUR, opacity=0.5, size=6),
            customdata=p.index.strftime("%a %d %b %Y"),
            hovertemplate="%{customdata}<br>actual %{x:.0f}, forecast %{y:.0f}<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=[0, top],
            y=[0, top],
            mode="lines",
            line=dict(color=GUIDE_COLOUR, dash="dash", width=1),
            name="Perfect forecast",
            hoverinfo="skip",
        ),
        row=1,
        col=2,
    )

    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="People per day", rangemode="tozero", row=1, col=1)
    fig.update_xaxes(title_text="Actual people per day", range=[0, top], row=1, col=2)
    fig.update_yaxes(title_text="Forecast people per day", range=[0, top], row=1, col=2)
    fig.update_layout(
        template="plotly_white",
        title=dict(
            text=f"{name}: forecast vs actual bookings<br><sup>10:30am tour, "
            f"{p.index.min():%b %Y} to {p.index.max():%b %Y}. Average error {mae:.1f} people "
            "a day. Each 30-day stretch forecast using only the data before it.</sup>"
        ),
        hovermode="closest",
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="left", x=0),
        height=540,
        width=1300,
        margin=dict(t=110, b=110),
    )
    return fig


def save_figure(fig, stem):
    """Write fig to <stem>.html (interactive) and, if kaleido can run, <stem>.png."""
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(stem.with_suffix(".html"), include_plotlyjs="cdn")
    try:
        fig.write_image(stem.with_suffix(".png"), scale=2)
    except Exception as e:  # kaleido needs Chrome; the html is still saved
        logger.warning("PNG not saved for %s (%s); the .html version was", stem.name, e)


def main(models=None):
    predictions = pd.read_csv(config.RESULTS_DIR / "comparison_predictions.csv")
    models = models or list(predictions["model"].unique())
    out_dir = config.FIGURES_DIR / "models"
    for model in models:
        save_figure(plot_forecast_vs_actual(predictions, model), out_dir / model)
    logger.info("Saved %d charts to %s", len(models), out_dir.relative_to(config.PROJECT_ROOT))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
