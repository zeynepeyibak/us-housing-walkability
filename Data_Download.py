"""Download the raw data.

Sources
- Zillow ZHVI by zip code and number of bedrooms (1-5)
- CPI for all urban consumers (CPIAUCSL) from FRED
- Walk, transit and bike scores per city, scraped from walkscore.com
- ACS 2021 5-year estimates at ZCTA level from the Census API:
  S2502 (characteristics of occupied housing units) and B08303 (travel time to work).
  The Census API requires a free key (https://api.census.gov/data/key_signup.html),
  read from the environment variable CENSUS_API_KEY.

Output: Data/raw/{Zillow,CPI,Walk,Census,Commute}.csv
"""
import os
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

RAW = Path("Data/raw")

# Zillow changes these URLs from time to time. If a download fails, copy the
# current link from https://www.zillow.com/research/data/
ZILLOW_URL = (
    "https://files.zillowstatic.com/research/public_csvs/zhvi/"
    "Zip_zhvi_bdrmcnt_{n}_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
)
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"
WALKSCORE_URL = "https://www.walkscore.com/{state}"
CENSUS_URL = "https://api.census.gov/data/2021/acs/acs5{table}"

STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL",
    "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
    "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]

# ACS variables we keep (labels checked against api.census.gov, 2021 ACS5)
DEMOGRAPHICS = {
    "S2502_C02_003E": "pct_black",       # householder Black or African American
    "S2502_C02_011E": "pct_younger_35",  # householder under 35 years
    "S2502_C02_018E": "pct_less_HS",     # householder less than high school
    "S2502_C02_021E": "pct_bsc_higher",  # householder bachelor's degree or higher
}
COMMUTE = [f"B08303_{i:03d}E" for i in range(1, 14)]  # 001 = total, 002-013 = bins


def get(url, **kwargs):
    response = requests.get(url, timeout=120, **kwargs)
    response.raise_for_status()
    return response


def download_zillow():
    frames = []
    for n in range(1, 6):
        df = pd.read_csv(StringIO(get(ZILLOW_URL.format(n=n)).text))
        df["Bedroom"] = n
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def download_cpi():
    return pd.read_csv(StringIO(get(FRED_URL).text))


def download_walkscore():
    frames = []
    for state in STATES:
        html = get(WALKSCORE_URL.format(state=state), headers={"User-Agent": "Mozilla/5.0"}).text
        for table in pd.read_html(StringIO(html)):
            if "City" in table.columns and "Walk Score" in table.columns:
                table["State"] = state
                frames.append(table)
    return pd.concat(frames, ignore_index=True)


def download_acs(table, variables):
    """Query one ACS table for all ZCTAs. The API returns a list of rows, header first."""
    key = os.environ.get("CENSUS_API_KEY")
    if not key:
        raise SystemExit(
            "Set CENSUS_API_KEY first. A free key is available at "
            "https://api.census.gov/data/key_signup.html"
        )
    params = {
        "get": ",".join(["NAME", *variables]),
        "for": "zip code tabulation area:*",
        "key": key,
    }
    response = get(CENSUS_URL.format(table=table), params=params)
    try:
        rows = response.json()
    except ValueError:
        raise SystemExit(f"Census API did not return data: {response.text[:300]}")
    return pd.DataFrame(rows[1:], columns=rows[0])


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    # Census first: it fails fast without a key, before the slower downloads
    download_acs("/subject", list(DEMOGRAPHICS)).to_csv(RAW / "Census.csv", index=False)
    download_acs("", COMMUTE).to_csv(RAW / "Commute.csv", index=False)
    download_zillow().to_csv(RAW / "Zillow.csv", index=False)
    download_cpi().to_csv(RAW / "CPI.csv", index=False)
    download_walkscore().to_csv(RAW / "Walk.csv", index=False)


if __name__ == "__main__":
    main()
