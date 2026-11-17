"""Figures for the opening talk of the RESILIENT final workshop.

Run from anywhere with ``uv run --with matplotlib make_figures.py``.
"""

import csv
from datetime import date, timedelta
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

HERE = Path(__file__).parent

plt.style.use(HERE / "plots.mplstyle")
# The style is sized for print; slide figures are shown at about 15 cm width.
# Type 3 fonts embed the OpenType font cleanly for pdflatex.
SMALL = 6.5
plt.rcParams.update(
    {
        "font.size": SMALL,
        "axes.labelsize": SMALL,
        "xtick.labelsize": SMALL,
        "ytick.labelsize": SMALL,
        "pdf.fonttype": 3,
    }
)

# Okabe-Ito colours from the style's cycle.
WAR = "#D55E00"  # war, sabotage, outages
POLICY = "#0072B2"
INK = "#222222"  # prices
MUTE = "#777777"

# Curve is drawn up to these dates in the four build steps.
CUTOFFS = [date(2023, 3, 31), date(2024, 12, 31), date(2025, 12, 31), date(2026, 11, 20)]

PHASES = {
    "Proposal": (date(2022, 9, 14), date(2023, 7, 31)),
    "RESILIENT project": (date(2023, 12, 1), date(2026, 11, 30)),
}

# (date, label, colour, build step, label height in EUR/MWh, text alignment)
EVENTS = [
    (date(2022, 2, 24), "Russia invades\nUkraine", WAR, 1, 215, "right"),
    (date(2022, 9, 26), "Nord Stream\ndestroyed", WAR, 1, 262, "left"),
    (date(2023, 10, 8), "Baltic Sea pipeline\nand cable damaged", WAR, 2, 205, "left"),
    (date(2024, 6, 21), "Balkan\nblackout", WAR, 2, 72, "center"),
    (date(2024, 11, 6), "Ampel-Aus", POLICY, 2, 150, "right"),
    (date(2024, 12, 12), "Dunkelflaute:\nStrom 936 €/MWh", INK, 2, 290, "right"),
    (date(2025, 1, 20), "US energy emergency,\nParis exit", POLICY, 3, 322, "left"),
    (date(2025, 4, 28), "Iberian\nblackout", WAR, 3, 272, "left"),
    (date(2025, 10, 17), "US sinks shipping's\ndecarbonisation plan", POLICY, 3, 222, "left"),
    (date(2026, 1, 3), "Berliner\nStromausfall", WAR, 4, 180, "left"),
    (date(2026, 2, 28), "Hormuz\nclosed", WAR, 4, 138, "left"),
    (date(2026, 11, 9), "Italy refunds\ngas plants;\nGasreserve", POLICY, 4, 290, "right"),
]

# Daily records of the TTF front-month contract: (date, EUR/MWh, label, step, alignment).
PEAKS = [
    (date(2022, 8, 26), 339, "339 €/MWh\ndaily record", 1, "left"),
    (date(2026, 10, 30), 104, "104 €/MWh", 4, "right"),
]


def read_prices() -> tuple[list[date], list[float]]:
    """Read the monthly European gas price in EUR/MWh.

    Returns
    -------
    tuple[list[date], list[float]]
        Mid-month dates and prices.
    """
    with open(HERE / "data" / "gas_price_europe_monthly.csv") as f:
        rows = list(csv.DictReader(f))
    days = [date.fromisoformat(r["month"] + "-15") for r in rows]
    return days, [float(r["eur_per_mwh"]) for r in rows]


def price_at(day: date, days: list[date], prices: list[float]) -> float:
    """Interpolate the monthly price linearly at a given day."""
    if day >= days[-1]:
        return prices[-1]
    i = next(k for k, d in enumerate(days) if d > day)
    w = (day - days[i - 1]) / (days[i] - days[i - 1])
    return prices[i - 1] + w * (prices[i] - prices[i - 1])


def draw_phases(ax: Axes) -> None:
    """Mark the proposal and project periods as lines under the time axis."""
    below = ax.get_xaxis_transform()
    for name, (start, end) in PHASES.items():
        ax.plot([start, end], [-0.17, -0.17], transform=below, color=MUTE, lw=1.4,
                solid_capstyle="butt", clip_on=False)
        ax.text(start + (end - start) / 2, -0.2, name, transform=below, ha="center", va="top",
                color=MUTE, fontsize=6)


def draw_legend(ax: Axes) -> None:
    """Name the three label colours in the empty top-left corner."""
    entries = [(INK, "prices"), (WAR, "war, sabotage, outages"), (POLICY, "policy")]
    for k, (colour, name) in enumerate(entries):
        y = 345 - 30 * k
        ax.plot(date(2021, 5, 15), y, "o", color=colour, ms=2.2)
        ax.text(date(2021, 6, 20), y, name, color=colour, va="center")


def draw_events(ax: Axes, step: int, days: list[date], prices: list[float]) -> None:
    """Draw event markers, leader lines and labels up to a build step."""
    pad = timedelta(days=12)
    for day, label, colour, first, height, ha in EVENTS:
        if first > step:
            continue
        base = price_at(day, days, prices)
        ax.plot([day, day], [base, height], color=colour, lw=0.5)
        ax.plot(day, base, "o", color=colour, ms=2.2)
        x = {"left": day + pad, "right": day - pad, "center": day}[ha]
        va = "bottom" if ha == "center" else "center"
        ax.text(x, height + (4 if ha == "center" else 0), label, color=colour, ha=ha, va=va)

    for day, value, label, first, ha in PEAKS:
        if first > step:
            continue
        # Daily records lie above the monthly average; a stem ties them to the curve.
        ax.plot([day, day], [price_at(day, days, prices), value], color=INK, lw=0.5)
        ax.plot(day, value, "o", color=INK, ms=2.2)
        x = day + pad if ha == "left" else day - pad
        ax.text(x, value, label, color=INK, ha=ha, va="center", fontweight="bold")

    if step >= 2:
        # German electricity and gas price brakes applied through 2023.
        ax.plot([date(2023, 1, 1), date(2023, 12, 31)], [92, 92], color=POLICY, lw=0.8)
        ax.text(date(2023, 1, 1), 96, "Strom- und\nGaspreisbremse", color=POLICY, ha="left",
                va="bottom")
        day = date(2024, 12, 25)  # Baltic Sea power cable
        ax.plot(day, price_at(day, days, prices), "o", color=WAR, ms=2.2)

    end = min(CUTOFFS[step - 1], date(2026, 11, 20))
    ax.plot([date(2022, 3, 1), end], [6, 6], color=WAR, lw=1.6, solid_capstyle="butt")
    if step >= 2:
        ax.text(date(2023, 2, 1), 11, "Russian attacks on Ukraine's energy system", color=WAR,
                ha="left", va="bottom", fontstyle="italic")


def timeline(step: int) -> None:
    """Save one build step of the gas price timeline with events.

    Parameters
    ----------
    step : int
        Build step from 1 to 4.
    """
    days, prices = read_prices()
    fig, ax = plt.subplots(figsize=(5.9, 2.6))
    shown = [(d, p) for d, p in zip(days, prices) if d <= CUTOFFS[step - 1]]
    x, y = zip(*shown)
    ax.fill_between(x, y, color="#E2E2E2", lw=0)
    ax.plot(x, y, color=INK, lw=1.0)
    ax.set_xlim(date(2021, 4, 1), date(2027, 3, 1))
    ax.set_ylim(0, 360)
    ax.set_yticks([0, 100, 200, 300])
    ax.set_ylabel("Gas price (€/MWh), monthly")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    draw_phases(ax)
    draw_legend(ax)
    draw_events(ax, step, days, prices)

    fig.savefig(HERE / f"timeline-step{step}.pdf")
    plt.close(fig)


def smspp_benchmark() -> None:
    """Save the solving-time comparison of PyPSA and SMS++ (UNIPI, January 2026)."""
    regions = [2, 5, 10, 20, 30, 50]
    seconds = {
        "PyPSA": [24.5, 523.0, 930.3, 1400.4, 7834.3, 15071.9],
        "PyPSA with SMS++": [65.4, 190.4, 319.8, 1003.5, 1955.1, 3165.4],
    }
    fig, ax = plt.subplots(figsize=(3.6, 2.2))
    for (name, values), colour in zip(seconds.items(), [MUTE, WAR]):
        minutes = [v / 60 for v in values]
        ax.plot(regions, minutes, "o-", color=colour, lw=1.2, ms=3)
        ax.text(51.5, minutes[-1], name, color=colour, va="center", fontweight="bold")
    ax.set_xlim(0, 68)
    ax.set_ylim(0, 270)
    ax.set_xticks(regions)
    ax.set_xlabel("Regions in the European electricity model")
    ax.set_ylabel("Solving time (minutes)")
    fig.savefig(HERE / "smspp-benchmark.pdf")
    plt.close(fig)


if __name__ == "__main__":
    for step in range(1, 5):
        timeline(step)
    smspp_benchmark()
