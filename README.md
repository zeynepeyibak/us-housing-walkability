# US house prices and walkability

Joint project by Claudine Schwarzenbach and Zeynep Eyibak (2023).

We estimate how walkability, bikeability and commute times relate to house prices at the zip-code level in the US, controlling for the number of bedrooms.

## Data

- Zillow Home Value Index by zip code and bedroom count (1–5)
- CPI (CPIAUCSL) from FRED
- Walk, bike and transit scores, scraped from walkscore.com for all 50 states
- Census ACS 2021 (5-year): demographics (S2502) and commute times (B08303)

## Pipeline (Snakemake)

1. `Data_Download.py`: downloads and scrapes the raw data
2. `Data_Preparation.py`: cleans the data and merges it into one zip-level panel
3. `Data_Exploration.py`: descriptive plots and the analysis sample
4. `Analysis.py`: OLS with robust standard errors, plus a city fixed-effects panel model with clustered standard errors
5. `Output/Output.tex`: compiles the tables and figures into a report

## Run

```
snakemake --cores 1
```

The Zillow download URL changes from time to time. If the download fails, update the URL in `Data_Download.py`.
