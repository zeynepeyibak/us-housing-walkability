#Import Packages
import pandas as pd
import requests
import io
from io import StringIO
import zipfile

# To get multiple outputs at once
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"


### Zillow Data: Data is downloaded from here:https://www.zillow.com/research/data/ However, url to download the file changes often. If the url doesn't exist, update the path before running the

# Create an empty list to store dataframes
house_prices_list = []

#download the data from Zillow website
for number in range(1, 6):
    url_zillow = f'https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_bdrmcnt_{number}_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv?t=1696158077'
    response = requests.get(url_zillow)
    data = pd.read_csv(StringIO(response.text))
    #add a 'number of bedrooms' column 
    data['Bedroom'] = number
    
    # Append the dataframe to the list
    house_prices_list.append(data)

# Concatenate the dataframes in the list
house_prices = pd.concat(house_prices_list, ignore_index=True)
# Save the data
house_prices.to_csv('Data/raw/Zillow.csv')

### CPI Data from FRED

# Download CPI from fed
url_CPI = "https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1318&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=CPIAUCSL&scale=left&cosd=1947-01-01&coed=2023-08-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Monthly&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2023-09-26&revision_date=2023-09-26&nd=1947-01-01"
CPI = pd.read_csv(url_CPI)
# Save the data
CPI.to_csv('Data/raw/CPI.csv')

### Walk/Transit/Bike Score: We scrape the data from walkscore.com

state= [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY",
    "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", 
    "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

#Initialize an empty data frame
walk_score = []

for st in state:
    url = f"https://www.walkscore.com/{st}"
    tables= pd.read_html(url)
    walk_score += [pd.DataFrame(table) for table in tables]
    for table in tables:
        table['State'] = st

walk_score = pd.concat(walk_score)

# save data
walk_score.to_csv('Data/raw/Walk.csv')

### Census Data
url_census_demog = "https://data.census.gov/api/access/table/download?download_id=0e22908ebd288452ea74e7450c2625aba74cace52e17cd1431542d638249e4f9"
zip_file = "ACSST5Y2021.S2502_2023-10-02T031911.zip"

response = requests.get(url_census_demog)

with open(zip_file, "wb") as file:
    file.write(response.content)
csv_file_in_zip = "ACSST5Y2021.S2502-Data.csv"

with zipfile.ZipFile(zip_file, "r") as zip_ref:
    with zip_ref.open(csv_file_in_zip) as file_in_zip:
        csv_data = file_in_zip.read()
demographics = pd.read_csv(io.BytesIO(csv_data))
# save the data
demographics.to_csv('Data/raw/Census.csv')

## Census commute data
url_census_commute = "https://data.census.gov/api/access/table/download?download_id=278c69b8e17a5e52ae49ed6323c631452c762747b6ea30c1d39e6ab4e4681fe6"
zip_file = "ACSDT5Y2021.B08303_2023-10-02T063015.zip"

response = requests.get(url_census_commute)


with open(zip_file, "wb") as file:
    file.write(response.content)
csv_file_in_zip = "ACSDT5Y2021.B08303-Data.csv"

with zipfile.ZipFile(zip_file, "r") as zip_ref:
    with zip_ref.open(csv_file_in_zip) as file_in_zip:
        csv_data = file_in_zip.read()
commute = pd.read_csv(io.BytesIO(csv_data))

commute.to_csv('Data/raw/Commute.csv')
