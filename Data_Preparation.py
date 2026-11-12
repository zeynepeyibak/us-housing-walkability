"""Clean the raw data and merge it into one file at the zip code x bedroom level.

- Zillow prices are converted to constant dollars of the latest month in the data (CPI-U).
- Walk scores are merged on city and state (city names alone are not unique).
- ACS demographics and commute shares are merged on the 5-digit zip code.

Output: Data/clean/Data.csv
"""
from pathlib import Path

import pandas as pd

RAW = Path("Data/raw")
CLEAN = Path("Data/clean")

ZILLOW_ID_COLS = ["zip", "State", "City", "CountyName", "SizeRank", "Bedroom"]
DEMOGRAPHICS = {
    "S2502_C02_003E": "pct_black",
    "S2502_C02_011E": "pct_younger_35",
    "S2502_C02_018E": "pct_less_HS",
    "S2502_C02_021E": "pct_bsc_higher",
}
COMMUTE_BINS = {
    "short_commute": ["B08303_002E", "B08303_003E", "B08303_004E"],  # under 15 min
    "moderate_commute": [f"B08303_{i:03d}E" for i in range(5, 10)],  # 15 to 39 min
    "long_commute": [f"B08303_{i:03d}E" for i in range(10, 14)],     # 40 min or more
}


def date_columns(df):
    return [c for c in df.columns if c[:2] in ("19", "20") and len(c) == 10]


def zip5(series):
    """Zip codes as 5-character strings; read as numbers, 02138 would become 2138."""
    return series.astype(str).str.extract(r"(\d+)", expand=False).str.zfill(5)


def load_cpi():
    cpi = pd.read_csv(RAW / "CPI.csv")
    date_col = "observation_date" if "observation_date" in cpi.columns else "DATE"
    cpi["month"] = pd.to_datetime(cpi[date_col]).dt.strftime("%Y-%m")
    return cpi.set_index("month")["CPIAUCSL"]


def prepare_zillow(cpi):
    zillow = pd.read_csv(RAW / "Zillow.csv")
    zillow = zillow.rename(columns={"RegionName": "zip"})
    zillow["zip"] = zip5(zillow["zip"])

    dates = [d for d in date_columns(zillow) if d[:7] in cpi.index]
    base = cpi[dates[-1][:7]]  # express all prices in dollars of the latest month
    for d in dates:
        zillow[d] = zillow[d] * base / cpi[d[:7]]

    return zillow[ZILLOW_ID_COLS + dates]


def prepare_walkscore():
    walk = pd.read_csv(RAW / "Walk.csv")
    walk["City"] = walk["City"].str.replace(r"\s*\([^)]*\)", "", regex=True).str.strip()
    walk = walk.rename(columns={
        "Walk Score": "walk_score",
        "Transit Score": "transit_score",
        "Bike Score": "bike_score",
    })
    scores = ["walk_score", "transit_score", "bike_score"]
    walk = walk[["City", "State"] + [s for s in scores if s in walk.columns]]
    for s in scores:
        if s in walk.columns:
            walk[s] = pd.to_numeric(walk[s], errors="coerce")
    return walk.drop_duplicates(subset=["City", "State"])


def read_acs(name):
    df = pd.read_csv(RAW / name, dtype=str)
    df["zip"] = zip5(df["zip code tabulation area"])
    return df


def prepare_demographics():
    df = read_acs("Census.csv").rename(columns=DEMOGRAPHICS)
    out = df[["zip", *DEMOGRAPHICS.values()]].copy()
    for col in DEMOGRAPHICS.values():
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def prepare_commute():
    df = read_acs("Commute.csv")
    counts = df.filter(like="B08303_").apply(pd.to_numeric, errors="coerce")
    total = counts["B08303_001E"].where(counts["B08303_001E"] > 0)
    out = pd.DataFrame({"zip": df["zip"]})
    for name, cols in COMMUTE_BINS.items():
        out[name] = counts[cols].sum(axis=1) / total * 100
    return out


def main():
    CLEAN.mkdir(parents=True, exist_ok=True)
    data = (
        prepare_zillow(load_cpi())
        .merge(prepare_walkscore(), on=["City", "State"], how="left", validate="m:1")
        .merge(prepare_demographics(), on="zip", how="left", validate="m:1")
        .merge(prepare_commute(), on="zip", how="left", validate="m:1")
    )
    data.to_csv(CLEAN / "Data.csv", index=False)


if __name__ == "__main__":
    main()
