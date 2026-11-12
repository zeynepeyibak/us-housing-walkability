# US house prices and walkability

Joint project by Claudine Schwarzenbach and Zeynep Eyibak (2023).

We estimate how walkability, bikeability and commute times relate to house prices at the zip-code level in the US, controlling for the number of bedrooms.

## Data

- Zillow Home Value Index by zip code and bedroom count (1–5), converted to constant dollars with CPI-U (FRED, CPIAUCSL)
- Walk, Bike and Transit Scores per city, scraped from walkscore.com and matched on city and state
- Census ACS 2021 (5-year) at ZCTA level from the Census API: householder characteristics (S2502) and travel time to work (B08303)

## Pipeline (Snakemake)

1. `Data_Download.py`: downloads and scrapes the raw data
2. `Data_Preparation.py`: cleans the data and merges it into one file at the zip code × bedroom level
3. `Data_Exploration.py`: descriptive plots
4. `Analysis.py`: log home value on Walk and Bike Scores, commute shares and neighbourhood characteristics, with bedroom and state fixed effects; standard errors clustered by city
5. `Output/Output.tex`: compiles the tables and figures into a report

## Run

```
pip install -r requirements.txt
snakemake --cores 1
```

The Zillow download URL changes from time to time. If the download fails, update it in `Data_Download.py`.
