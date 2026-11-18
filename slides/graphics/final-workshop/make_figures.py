"""Figures for the opening talk of the RESILIENT final workshop.

Run from anywhere with ``uv run --with matplotlib --with cartopy make_figures.py``.
"""

import csv
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patheffects
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

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
YLABEL = "Gas price (€/MWh), daily"

# Curve is drawn up to these dates in the four build steps.
CUTOFFS = [date(2023, 3, 31), date(2026, 11, 20)]

PHASES = {
    "Proposal": (date(2022, 9, 14), date(2023, 7, 31)),
    "RESILIENT project": (date(2023, 12, 1), date(2026, 11, 30)),
}

# (date, label, colour, build step, label height in EUR/MWh, text alignment)
EVENTS = [
    (date(2022, 2, 24), "Russia’s full-scale\ninvasion of Ukraine", WAR, 1, 305, "right"),
    (date(2022, 9, 26), "Nord Stream\ndestroyed", WAR, 1, 262, "left"),
    (date(2023, 10, 8), "Baltic Sea pipeline\nand cable damaged", WAR, 2, 205, "left"),
    (date(2024, 6, 21), "Balkan\nblackout", WAR, 2, 72, "center"),
    (date(2024, 5, 21), "EU electricity\nmarket reform", POLICY, 2, 150, "right"),
    (date(2024, 12, 12), "Dunkelflaute:\nStrom 936 €/MWh", INK, 2, 290, "right"),
    (date(2025, 1, 20), "Trump administration\ntakes office", POLICY, 2, 322, "left"),
    (date(2025, 4, 28), "Iberian\nblackout", WAR, 2, 272, "left"),
    (date(2025, 10, 17), "US sinks maritime\ndecarbonisation plan", POLICY, 2, 255, "left"),
    (date(2026, 1, 3), "Berlin\nblackout", WAR, 2, 212, "left"),
    (date(2026, 1, 26), "EU bans Russian\ngas by 2027", POLICY, 2, 168, "left"),
    (date(2026, 2, 28), "Strait of\nHormuz", WAR, 2, 124, "left"),
    (date(2026, 11, 9), "Italy refunds\ngas plants", POLICY, 2, 305, "right"),
]

# Price peaks: (date, EUR/MWh, label, step, vertical alignment).
PEAKS = [
    (date(2022, 8, 26), 339, "339 €/MWh", 1, "center"),
    (date(2026, 10, 30), 104, "104\n€/MWh", 2, "top"),
]


def read_prices() -> tuple[list[date], list[float]]:
    """Read the daily Dutch TTF front-month gas price in EUR/MWh.

    Returns
    -------
    tuple[list[date], list[float]]
        Trading days and closing prices.
    """
    with open(HERE / "data" / "gas_price_ttf_daily.csv") as f:
        rows = list(csv.DictReader(f))
    return [date.fromisoformat(r["date"]) for r in rows], [float(r["eur_per_mwh"]) for r in rows]


def price_at(day: date, days: list[date], prices: list[float]) -> float:
    """Interpolate the price linearly at a given day."""
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
    """Name the three label colours in a column under the time axis, left of the phases."""
    entries = [(INK, "prices"), (WAR, "war, sabotage, outages"), (POLICY, "policy")]
    handles = [Line2D([], [], ls="", marker="o", ms=3.5, color=c) for c, _ in entries]
    legend = ax.legend(handles, [n for _, n in entries], loc="upper left", bbox_to_anchor=(0, -0.13),
                       frameon=False, handletextpad=0.2, labelspacing=0.3, borderaxespad=0,
                       borderpad=0)
    for text, (colour, _) in zip(legend.get_texts(), entries):
        text.set_color(colour)


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

    for day, value, label, first, va in PEAKS:
        if first > step:
            continue
        ax.plot(day, value, "o", color=INK, ms=2.2)
        y = value if va == "center" else value - 30
        ax.text(day + pad, y, label, color=INK, ha="left", va=va, fontweight="bold")

    # Gazprom-linked storage sites stayed nearly empty through the 2021 injection season.
    ax.plot([date(2021, 4, 1), date(2021, 10, 31)], [130, 130], color=WAR, lw=0.8)
    ax.text(date(2021, 1, 5), 134, "Rehden, Germany's\nlargest gas storage\nnearly empty", color=WAR,
            ha="left", va="bottom")

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
        Build step, 1 or 2.
    """
    days, prices = read_prices()
    fig, ax = plt.subplots(figsize=(5.9, 2.6))
    shown = [(d, p) for d, p in zip(days, prices) if d <= CUTOFFS[step - 1]]
    x, y = zip(*shown)
    ax.fill_between(x, y, color="#E2E2E2", lw=0)
    ax.plot(x, y, color=INK, lw=0.7)
    ax.set_xlim(date(2021, 1, 1), date(2027, 4, 15))
    ax.set_ylim(0, 360)
    ax.set_yticks([0, 100, 200, 300])
    ax.set_ylabel(YLABEL)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    draw_phases(ax)
    draw_legend(ax)
    draw_events(ax, step, days, prices)

    fig.savefig(HERE / f"timeline-step{step}.pdf")
    plt.close(fig)


def smspp_benchmark() -> None:
    """Save solving times with and without SMS++ against the number of demand scenarios."""
    with open(HERE / "data" / "smspp_scenario_scaling_20_nodes.csv") as f:
        rows = list(csv.DictReader(f))
    # solver option: (label, colour, label offset in points, alignment)
    runs = {
        "gurobi-default": ("PyPSA + Gurobi", INK, (-5, 6), "right"),
        "smspp-tssb-ib-par": ("SMS++ IB + Gurobi", WAR, (5, -8), "left"),
    }
    fig, ax = plt.subplots(figsize=(3.6, 2.3))
    for option, (name, colour, offset, ha) in runs.items():
        run = [r for r in rows if r["solver_options"] == option and float(r["scenarios"]) <= 100]
        x = [int(float(r["scenarios"])) for r in run]
        y = [float(r["runtime_s"]) for r in run]
        ax.plot(x, y, "o-", color=colour, lw=1.2, ms=3)
        ax.annotate(f"{y[-1] / 3600:.2f} h", (x[-1], y[-1]), xytext=(5, 0), textcoords="offset points",
                    va="center", color=colour, fontweight="bold")
        ax.annotate(name, (x[2], y[2]), xytext=offset, textcoords="offset points", ha=ha,
                    va="center", color=colour)
    ax.set_yscale("log")
    ax.minorticks_off()
    ax.set_xticks([10, 20, 50, 100])
    ax.set_yticks([1000, 3000, 10000, 20000], labels=["1000", "3000", "10000", "20000"])
    ax.set_xlim(0, 120)
    ax.set_ylim(700, 25000)
    ax.set_xlabel("Number of scenarios")
    ax.set_ylabel("Solving time [s]")
    fig.savefig(HERE / "smspp-benchmark.pdf")
    plt.close(fig)


# Participant types from the registration sheet, grouped by the first type given.
GROUPS = {
    "University/research": ("Universities and research institutes", "#0072B2"),
    "TSO": ("TSOs", "#E69F00"),
    "Utility/developer": ("Utilities and industry", "#CC79A7"),
    "Consulting": ("Consultancies", "#009E73"),
}
OTHER = ("Public sector, NGOs, other", "#999999")
ORDER = [*GROUPS.values(), OTHER]

# Organisations named on the map: label text and offset from the dot centre in points.
# Only the largest site of an organisation is labelled.
LABELS = {
    "Chalmers": ("Chalmers", (-8, 0)),
    "KTH": ("KTH", (0, 7)),
    "Statkraft": ("Statkraft", (-6, 0)),
    "DTU": ("DTU", (-12, 4)),
    "Ramboll": ("Ramboll", (0, -8)),
    "Danish Energy Agency": ("DEA", (7, 0)),
    "50Hertz": ("50Hertz", (14, -9)),
    "Agora Energiewende": ("Agora", (0, 7)),
    "Amprion": ("Amprion", (8, 0)),
    "RWE": ("E.ON, RWE", (-10, -12)),
    "TenneT": ("TenneT", (0, -8)),
    "ČEPS": ("ČEPS", (7, 0)),
    "TransnetBW": ("TransnetBW", (-6, -8)),
    "Siemens": ("Siemens", (0, -8)),
    "IIASA": ("IIASA", (0, -8)),
    "ENTSO-E": ("ENTSO-E", (-10, 0)),
    "EDF": ("EDF", (-9, 2)),
    "IEA": ("IEA", (-7, -7)),
    "RTE international": ("RTE", (8, -6)),
    "Imperial College London": ("Imperial", (-7, 0)),
    "SSEN Transmission": ("SSEN", (-9, 0)),
    "Terna": ("Terna", (6, 0)),
    "EDP Renewables": ("EDP Renewables", (6, 0)),
}
AREA = 6  # marker area in pt^2 per participant
PAD = 0.6  # gap between neighbouring dots in points


def read_organisations() -> list[tuple[str, float, float, int, tuple[str, str]]]:
    """Count 2025 workshop participants per organisation site.

    Returns
    -------
    list[tuple[str, float, float, int, tuple[str, str]]]
        Name, longitude, latitude, participants and (group name, colour), largest first.
    """
    with open(HERE / "data" / "organisation_locations.csv") as f:
        places = {r["organisation"]: r for r in csv.DictReader(f)}
    with open(HERE / "data" / "workshop_participants_2025.csv") as f:
        rows = list(csv.DictReader(f))
    groups: dict[tuple[str, float, float], Counter] = {}
    for row in rows:
        place = places[row["Organisation or company"].strip()]
        key = (place["name"], float(place["lon"]), float(place["lat"]))
        group = GROUPS.get(row["Type"].split(",")[0].strip(), OTHER)
        groups.setdefault(key, Counter())[group] += 1
    orgs = [(*key, c.total(), c.most_common(1)[0][0]) for key, c in groups.items()]
    return sorted(orgs, key=lambda o: -o[3])


def pack(sites: np.ndarray, radii: np.ndarray) -> np.ndarray:
    """Move circles off their sites until none overlap, placing the largest first.

    Parameters
    ----------
    sites : np.ndarray
        Preferred centres in points, one row per circle, sorted by decreasing radius.
    radii : np.ndarray
        Circle radii in points, including padding.

    Returns
    -------
    np.ndarray
        Centres in points.
    """
    angles = np.linspace(0, 2 * np.pi, 36, endpoint=False)
    ring = np.column_stack([np.cos(angles), np.sin(angles)])
    placed = np.empty((0, 2))
    for site, r in zip(sites, radii):
        for step in np.arange(0, 60, 0.25):
            candidates = site + step * ring if step else site[None, :]
            gaps = np.hypot(*(candidates[:, None, :] - placed[None, :, :]).transpose(2, 0, 1))
            free = (gaps >= r + radii[: len(placed)]).all(axis=1)
            if free.any():
                placed = np.vstack([placed, candidates[free.argmax()]])
                break
    return placed


def participant_map() -> None:
    """Save a map of 2025 workshop participants, one dot per organisation site."""
    orgs = read_organisations()
    fig = plt.figure(figsize=(5.67, 3.0), layout="none")
    geo = ccrs.PlateCarree()
    proj = ccrs.LambertAzimuthalEqualArea(central_longitude=10, central_latitude=52)
    ax = fig.add_axes((0, 0, 0.64, 1), projection=proj)
    ax.set_extent((-7.5, 29.6, 38.6, 60.8), crs=geo)
    ax.add_feature(cfeature.NaturalEarthFeature("cultural", "admin_0_countries", "50m"),
                   facecolor="#E8E8E8", edgecolor="white", lw=0.4)
    ax.spines["geo"].set_visible(False)
    ax.apply_aspect()
    x0, x1 = ax.get_xlim()
    metres_per_pt = (x1 - x0) / (ax.get_position().width * fig.get_figwidth() * 72)

    lon, lat = np.array([o[1] for o in orgs]), np.array([o[2] for o in orgs])
    sites = proj.transform_points(geo, lon, lat)[:, :2] / metres_per_pt
    sizes = AREA * np.array([o[3] for o in orgs])
    centres = pack(sites, np.sqrt(sizes) / 2 + PAD / 2) * metres_per_pt
    ax.scatter(centres[:, 0], centres[:, 1], s=sizes, c=[o[4][1] for o in orgs], lw=0, zorder=3)

    halo = [patheffects.withStroke(linewidth=1.5, foreground="white")]
    named = set()
    for (name, *_), centre, size in zip(orgs, centres, sizes):
        if name not in LABELS or name in named:
            continue
        named.add(name)
        text, (dx, dy) = LABELS[name]
        radius = np.sqrt(size) / 2
        leader = dict(arrowstyle="-", lw=0.3, color=MUTE, shrinkA=0, shrinkB=radius)
        ax.annotate(text, centre, xytext=(dx, dy), textcoords="offset points",
                    ha="left" if dx > 0 else "right" if dx < 0 else "center", va="center",
                    fontsize=5.5, color=INK, path_effects=halo, zorder=5,
                    arrowprops=leader if np.hypot(dx, dy) > radius + 5 else None)

    key = fig.add_axes((0.67, 0.08, 0.33, 0.62))
    key.set_axis_off()
    key.set_xlim(0, 1)
    key.set_ylim(0, 1)
    for k, (name, colour) in enumerate(ORDER):
        y = 0.95 - 0.12 * k
        key.scatter(0.03, y, s=AREA * 5, color=colour, lw=0)
        key.text(0.08, y, name, va="center")
    for k, n in enumerate((1, 5, 10)):
        key.scatter(0.03 + 0.1 * k, 0.3, s=AREA * n, color=MUTE, lw=0)
        key.text(0.03 + 0.1 * k, 0.22, str(n), ha="center", va="top", color=MUTE)
    key.text(0.36, 0.3, "participants per\norganisation", va="center", color=MUTE)
    fig.savefig(HERE / "participant-map.pdf")
    plt.close(fig)


if __name__ == "__main__":
    for step in (1, 2):
        timeline(step)
    smspp_benchmark()
    participant_map()
