#Import Packages
import pandas as pd
import requests
import io
from io import StringIO
import zipfile
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


# load the data
house_prices = pd.read_csv('Data/raw/Zillow.csv')
CPI = pd.read_csv('Data/raw/CPI.csv')
walk_score = pd.read_csv('Data/raw/Walk.csv')
demographics = pd.read_csv('Data/raw/Census.csv')

### Zillow data
#Rename RegionName to zip
house_prices=house_prices.rename(columns={'RegionName': 'zip'})
#Adjust house prices by yearly inflation
for col in house_prices.columns:
    #Extract the first 7 characters of house_prices data frame
    first7chr = col[:7]
    #Find the columns from CPI that has the same first 7 ch
    if first7chr in CPI.columns:
        #Divide the corresponding house prices column to CPI and multip by 100 to adjust for inflation
        #house_prices_CPI=house_prices.copy()
        house_prices[col] = (house_prices[col] / CPI[first7chr].iloc[0]) * 100 

#Understand the missing data
house_prices['2023-08-31'].isna().sum() #no missing in 2023 august
house_prices['2023-07-31'].isna().sum()
house_prices['2023-06-30'].isna().sum()


#Create variables based on past house prices (potentially to be used for regression)

##Create yearly average house prices variables
for year in range(2021, 2024):
    year_columns = [col for col in house_prices.columns if col.startswith(str(year))]
    house_prices[f'Average_{year}'] = house_prices[year_columns].mean(axis=1)
    
## Growth of house prices
for year in range(2022, 2024):
    previous_year = year - 1
    
    # Calculate the percentage growth from the previous year to the current year
    house_prices[f'Growth_{previous_year}_to_{year}'] = (
        house_prices[f'Average_{year}'] / house_prices[f'Average_{previous_year}'] - 1
    )


#Drop the columns we don't need
## Drop columns from 2000 to 2018
#pattern = r'^(2000|2001|2002|2003|2004|2005|2006|2007|2008|2009|2010|2011|2012|2013|2014|2015|2016|2017|2018|2019|2020|2021|2022)'

#columns_to_drop = house_prices.filter(regex=pattern)
#house_prices.drop(columns=columns_to_drop.columns, inplace=True)

#drop other unnecessary columns
columns_to_drop = ['RegionID', 'RegionType', 'StateName', 'Metro']

# Drop the specified columns
house_prices.drop(columns=columns_to_drop, inplace=True)


### Walk Index
##Get rid of the extra info with () at the end of some cities 
walk_score['City'] = walk_score['City'].str.replace(r'\s*\([^)]*\)', '', regex=True)

## Drop unnecessary variables:
walk_score = walk_score.drop(columns=['Population', 'Zip Code'])

#Merge Walk Index to Zillow
house_prices = pd.merge(house_prices, walk_score, on=['City'], how='left')


###Census Data
#Organize the data
demographics = demographics.drop(0).reset_index(drop=True)
demographics = demographics.rename(columns={'NAME': 'zip'})

demographics = demographics[["S2502_C02_011E", "S2502_C02_003E", "S2502_C02_018E", "S2502_C02_021E", "zip"]]
demographics['zip'] = demographics['zip'].str[6:]

demographics = demographics.rename(columns={
    'S2502_C02_011E': 'pct_younger_35',
    'S2502_C02_003E': 'pct_black',
    'S2502_C02_018E': 'pct_less_HS',
    'S2502_C02_021E': 'pct_bsc_higher'})

#Join the demographics data into house prices data
house_prices['zip'] = house_prices['zip'].astype(str)
demographics['zip'] = demographics['zip'].astype(str)

house_prices= pd.merge(house_prices, demographics, on='zip', how='left')

## Commute data
#Organize the data
commute = commute.drop(0).reset_index(drop=True)
commute = commute.rename(columns={'NAME': 'zip'})
commute['zip'] = commute['zip'].str[6:]

# Rename the columns to remove special characters
commute.rename(columns={
    'B08303_003E': 'Less than 5 min',
    'B08303_004E': '5 to 9 min',
    'B08303_005E': '10 to 14 min',
    'B08303_006E': '15 to 19 min',
    'B08303_007E': '20 to 24 min',
    'B08303_008E': '25 to 29 min',
    'B08303_009E': '30 to 34 min',
    'B08303_010E': '35 to 39 min',
    'B08303_011E': '40 to 44 min',
    'B08303_012E': '45 to 59 min',
    'B08303_013E': '60 to 89 min'
}, inplace=True)

relevant_columns=['Less than 5 min', '5 to 9 min', '10 to 14 min', '15 to 19 min',
                    '20 to 24 min', '25 to 29 min', '30 to 34 min', '35 to 39 min',
                    '40 to 44 min', '45 to 59 min', '60 to 89 min']
commute=commute[['zip'] + relevant_columns]

commute['Total'] = commute[relevant_columns].sum(axis=1)
commute['Total'].replace(0, np.nan, inplace=True)

for col in relevant_columns:
    commute[col] = pd.to_numeric(commute[col], errors='coerce')
    
commute['Total'].replace(0, np.nan, inplace=True)
commute['Total'] = pd.to_numeric(commute['Total'], errors='coerce')
commute['Short Commute'] = (commute['Less than 5 min'] + commute['5 to 9 min'] + commute['10 to 14 min']) / commute['Total'] * 100
commute['Moderate Commute'] = (commute['15 to 19 min'] + commute['20 to 24 min'] + commute['25 to 29 min'] + commute['30 to 34 min'] + commute['35 to 39 min']) / commute['Total'] * 100
commute['Long Commute'] = (commute['45 to 59 min'] + commute['60 to 89 min'] + commute['40 to 44 min']) / commute['Total'] * 100

commute=commute[['Short Commute', 'Moderate Commute', 'Long Commute', 'zip']]

house_prices= pd.merge(house_prices, commute, on='zip', how='left')

##save the clean data
house_prices.to_csv('Data/clean/Data.csv')