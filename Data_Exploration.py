"""Descriptive plots.

Output: Plots/{Prices,Expensive,Cheap,Walk_Bike,Walk_Price,Bike_Price}.png
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from Data_Preparation import date_columns

PLOTS = Path("Plots")


def load():
    return pd.read_csv("Data/clean/Data.csv", dtype={"zip": str})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(PLOTS / name, dpi=150)
    plt.close(fig)


def plot_prices_largest_zip(data, latest):
    """Real price over time, by bedroom count, in the zip code with the largest housing stock."""
    dates = date_columns(data)
    top = data.loc[data["SizeRank"] == data["SizeRank"].min()]
    zip_code, city, state = top.iloc[0][["zip", "City", "State"]]

    fig, ax = plt.subplots(figsize=(8, 5))
    for _, row in top.sort_values("Bedroom").iterrows():
        ax.plot(pd.to_datetime(dates), row[dates].to_numpy(dtype=float), label=f"{row['Bedroom']} bedroom" + ("s" if row["Bedroom"] > 1 else ""))
    ax.set_title(f"Home values in zip {zip_code} ({city}, {state})")
    ax.set_ylabel(f"Home value, {latest[:7]} dollars")
    ax.legend()
    save(fig, "Prices.png")


def plot_extremes(data, latest, n=10):
    """The n most and least expensive zip codes for 2-bedroom homes."""
    two_bed = data.loc[data["Bedroom"] == 2].dropna(subset=[latest])
    labels = lambda df: df["City"].fillna("") + ", " + df["State"] + " (" + df["zip"] + ")"

    for name, subset, title in [
        ("Expensive.png", two_bed.nlargest(n, latest), "Most expensive"),
        ("Cheap.png", two_bed.nsmallest(n, latest), "Least expensive"),
    ]:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(labels(subset), subset[latest])
        ax.invert_yaxis()
        ax.set_title(f"{title} zip codes for 2-bedroom homes, {latest[:7]}")
        ax.set_xlabel("Home value, dollars")
        ax.ticklabel_format(axis="x", style="plain")
        save(fig, name)


def plot_scores(data, latest):
    cities = data.dropna(subset=["walk_score", "bike_score"]).drop_duplicates(["City", "State"])
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(cities["walk_score"], cities["bike_score"], alpha=0.5)
    ax.set_xlabel("Walk Score")
    ax.set_ylabel("Bike Score")
    ax.set_title("Walk and Bike Scores across cities")
    save(fig, "Walk_Bike.png")

    two_bed = data.loc[data["Bedroom"] == 2].dropna(subset=[latest])
    for score, name in [("walk_score", "Walk_Price.png"), ("bike_score", "Bike_Price.png")]:
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.scatter(two_bed[score], np.log(two_bed[latest]), alpha=0.3, s=8)
        ax.set_xlabel(score.replace("_", " ").title())
        ax.set_ylabel("Log home value, 2-bedroom")
        ax.set_title(f"{score.replace('_', ' ').title()} and home values, {latest[:7]}")
        save(fig, name)


def main():
    PLOTS.mkdir(exist_ok=True)
    data = load()
    latest = date_columns(data)[-1]
    plot_prices_largest_zip(data, latest)
    plot_extremes(data, latest)
    plot_scores(data, latest)


if __name__ == "__main__":
    main()
