import pandas as pd
import requests
from io import StringIO

# Zillow Data
# Create an empty list to store dataframes
house_prices_list = []

# Download the data from Zillow website
for number in range(1, 6):
    url = f'https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_bdrmcnt_{number}_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv'
    response = requests.get(url)
    data = StringIO(response.text)
    df = pd.read_csv(data)
    # Add a 'number of bedrooms' column 
    df['Bedroom'] = number
    
    # Append the dataframe to the list
    house_prices_list.append(df)

# Concatenate the dataframes in the list
house_prices = pd.concat(house_prices_list, ignore_index=True)
print(house_prices)