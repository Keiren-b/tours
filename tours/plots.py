"""Figures. Each function takes data and returns a figure (and saves it if given a path).

python -m tours.plots                 # prophet, from results/comparison_predictions.csv
python -m tours.plots lightgbm        # any model in that file
"""

import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from tours import config  # noqa: E402

# colours: validated two-series palette (categorical slots 1 and 2) + neutral inks
SURFACE, INK, QUIET, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
ACTUAL_COLOUR, FORECAST_COLOUR = "#2a78d6", "#eb6834"

MODEL_NAMES = {"prophet": "Prophet", "lightgbm": "LightGBM", "mstl": "MSTL", "arimax": "ARIMAX"}


def _style(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, colors=QUIET)


def plot_forecast_vs_actual(predictions, model="prophet", out_path=None):
    """Daily forecast vs actual over time, plus a forecast-vs-actual scatter.

    predictions: rows of (model, date, actual, pred), as in comparison_predictions.csv.
    Christmas Day (closed) is left out.
    """
    p = predictions[predictions["model"] == model].copy()
    if p.empty:
        raise ValueError(f"no predictions for model {model!r}")
    p["date"] = pd.to_datetime(p["date"])
    p = p.sort_values("date").set_index("date")
    xmas = (p.index.month == 12) & (p.index.day == 25)
    p.loc[xmas, ["actual", "pred"]] = float("nan")
    name = MODEL_NAMES.get(model, model)
    mae = (p["pred"] - p["actual"]).abs().mean()
    top = max(p["actual"].max(), p["pred"].max())
    limit = (int(top // 50) + 1) * 50

    fig = plt.figure(figsize=(14, 5.6), facecolor=SURFACE)
    grid = fig.add_gridspec(
        1, 2, width_ratios=[2.5, 1], wspace=0.14, left=0.05, right=0.98, top=0.8, bottom=0.12
    )
    ax, sc = fig.add_subplot(grid[0]), fig.add_subplot(grid[1])
    fig.text(
        0.05,
        0.94,
        f"{name} forecast vs actual bookings",
        fontsize=15,
        fontweight="bold",
        color=INK,
    )
    fig.text(
        0.05,
        0.895,
        f"Bookings per day for the 10:30am tour, {p.index.min():%b %Y} to {p.index.max():%b %Y}. "
        f"Each forecast used only the data before it. Average error {mae:.1f} people a day. "
        "Christmas Day (closed) left out.",
        fontsize=10,
        color=QUIET,
    )

    # left: over time
    _style(ax)
    ax.plot(p.index, p["actual"], color=ACTUAL_COLOUR, linewidth=1.6, label="Actual bookings")
    ax.plot(p.index, p["pred"], color=FORECAST_COLOUR, linewidth=1.6, label=f"{name} forecast")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.set_ylim(0, limit)
    ax.set_xlim(p.index.min(), p.index.max() + pd.Timedelta(days=2))
    ax.set_ylabel("People per day", color=QUIET)
    ax.legend(
        loc="upper center", ncol=2, frameon=False, labelcolor=INK, bbox_to_anchor=(0.5, 1.06)
    )
    busiest = p["actual"].idxmax()
    on_right = busiest > p.index.min() + (p.index.max() - p.index.min()) / 2
    ax.annotate(
        f"Busiest day: forecast {p.loc[busiest, 'pred']:.0f}, actual {p.loc[busiest, 'actual']:.0f}",
        xy=(busiest, p.loc[busiest, "actual"]),
        xytext=(-12 if on_right else 12, -4),
        textcoords="offset points",
        ha="right" if on_right else "left",
        fontsize=9,
        color=QUIET,
    )

    # right: one dot per day
    _style(sc)
    days = p.dropna(subset=["actual", "pred"])
    sc.scatter(
        days["actual"],
        days["pred"],
        s=16,
        color=ACTUAL_COLOUR,
        alpha=0.55,
        edgecolors=SURFACE,
        linewidths=0.5,
    )
    sc.plot([0, limit], [0, limit], color=MUTED, linewidth=1, linestyle="--")
    sc.text(
        limit * 0.75,
        limit * 0.81,
        "perfect forecast",
        rotation=41,
        color=MUTED,
        fontsize=9,
        ha="center",
    )
    sc.text(limit * 0.95, limit * 0.1, "under-forecast", color=QUIET, fontsize=9, ha="right")
    sc.text(limit * 0.06, limit * 0.75, "over-forecast", color=QUIET, fontsize=9)
    sc.set_xlim(0, limit)
    sc.set_ylim(0, limit)
    sc.set_aspect("equal")
    sc.set_xlabel("Actual people per day", color=QUIET)
    sc.set_ylabel("Forecast people per day", color=QUIET)
    sc.set_title("Each dot is one day", fontsize=10, color=QUIET, loc="left")

    if out_path:
        fig.savefig(out_path, dpi=160, facecolor=SURFACE)
    return fig


def main(model="prophet"):
    predictions = pd.read_csv(config.RESULTS_DIR / "comparison_predictions.csv")
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out = config.FIGURES_DIR / f"{model}_actual_vs_forecast.png"
    plot_forecast_vs_actual(predictions, model, out)
    print(out.relative_to(config.PROJECT_ROOT))


if __name__ == "__main__":
    main(*sys.argv[1:2])
