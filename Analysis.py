"""Regressions of home values on walkability, bikeability and commute times.

Unit of observation: zip code x number of bedrooms, in the latest month of the Zillow data.
Dependent variable: log home value. All models include bedroom fixed effects.
Walk and bike scores vary at the city level, so standard errors are clustered by city.

Output: Tables/summary_{1,2,3}.tex
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col

from Data_Preparation import date_columns

TABLES = Path("Tables")
SCORES = ["walk_score", "bike_score"]
COMMUTE = ["short_commute", "long_commute"]  # omitted category: 15 to 39 minutes
DEMOGRAPHICS = ["pct_bsc_higher", "pct_younger_35"]
ORDER = SCORES + COMMUTE + DEMOGRAPHICS
LABELS = {
    "walk\\_score": "Walk Score",
    "bike\\_score": "Bike Score",
    "short\\_commute": "Short commute (\\%)",
    "long\\_commute": "Long commute (\\%)",
    "pct\\_bsc\\_higher": "Bachelor's or higher (\\%)",
    "pct\\_younger\\_35": "Householder under 35 (\\%)",
}


def cross_section():
    data = pd.read_csv("Data/clean/Data.csv", dtype={"zip": str})
    latest = date_columns(data)[-1]
    data = data.loc[data[latest] > 0].copy()
    data["log_price"] = np.log(data[latest])
    data["city"] = data["City"] + ", " + data["State"]
    return data


def fit(data, regressors, state_fe=False):
    """OLS with bedroom (and optionally state) fixed effects, SEs clustered by city."""
    sample = data.dropna(subset=["log_price", "city", *regressors])
    fixed_effects = ["C(Bedroom)"] + (["C(State)"] if state_fe else [])
    formula = "log_price ~ " + " + ".join(regressors + fixed_effects)
    groups = pd.factorize(sample["city"])[0]
    result = smf.ols(formula, data=sample).fit(cov_type="cluster", cov_kwds={"groups": groups})
    result.state_fe = state_fe
    result.n_clusters = len(set(groups))
    return result


def write_table(results, title, path):
    info = {
        "Bedroom FE": lambda r: "Yes",
        "State FE": lambda r: "Yes" if r.state_fe else "No",
        "Cities": lambda r: f"{r.n_clusters:,}",
        "Observations": lambda r: f"{int(r.nobs):,}",
    }
    table = summary_col(
        results,
        float_format="%0.4f",
        stars=True,
        model_names=[f"({i})" for i in range(1, len(results) + 1)],
        info_dict=info,
        regressor_order=[v for v in ORDER if any(v in r.params for r in results)],
        drop_omitted=True,
    )
    table.add_title(title)
    latex = table.as_latex()
    for name, label in LABELS.items():
        latex = latex.replace(name, label)
    path.write_text(latex)


def main():
    TABLES.mkdir(exist_ok=True)
    data = cross_section()

    write_table(
        [fit(data, ["walk_score"]), fit(data, ["bike_score"]), fit(data, SCORES)],
        "Log home value on Walk and Bike Scores",
        TABLES / "summary_1.tex",
    )
    write_table(
        [fit(data, SCORES + COMMUTE), fit(data, SCORES + COMMUTE + DEMOGRAPHICS)],
        "Adding commute times and neighbourhood characteristics",
        TABLES / "summary_2.tex",
    )
    write_table(
        [fit(data, SCORES, state_fe=True), fit(data, SCORES + COMMUTE + DEMOGRAPHICS, state_fe=True)],
        "Within-state comparisons (state fixed effects)",
        TABLES / "summary_3.tex",
    )


if __name__ == "__main__":
    main()
