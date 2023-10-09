#import packages
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# load clean data
house_prices = pd.read_csv('Data/clean/Data.csv')

### Zillow & CPI data
##################################
#analyze CPI adjusted house prices separately

dates = [col for col in house_prices if col.startswith('20')]
cols = ['SizeRank', 'zip', 'State', 'City', 'CountyName', *dates, 'Bedroom']
Zillow = house_prices[cols]

#Descriptive stats of house_prices
pd.set_option('display.float_format', '{:,.2f}'.format)
house_prices_descriptive=Zillow[['Bedroom','2023-06-30','2023-07-31','2023-08-31']].describe()
#house_prices_descriptive

#Make a time series plot of the house prices in the zip with most houses for sale: i.e. sizeRank=1
biggest_zip_rows=Zillow[Zillow['SizeRank'] == 1] #filter the rows where SizeRank=1
biggest_zip = biggest_zip_rows['zip'].iloc[0]
Zillow.Bedroom[Zillow['zip'] == biggest_zip] #there are no 1 bedroom houses for sale in this area

## Locate the state and the city of the zip with most houses for sale:
State_biggest_zip=Zillow.State[Zillow['zip'] == biggest_zip].iloc[0]
State_biggest_zip

City_biggest_zip=Zillow.City[Zillow['zip'] == biggest_zip].iloc[0]
City_biggest_zip

##Create the Plot
bedroom_counts = range(2, 6)

##Create subplots for bedrooms from 2 to 6 (there are no 1 bedroom houses listed in this zip)
fig, axes = plt.subplots(len(bedroom_counts), 1, figsize=(8, 6 * len(bedroom_counts)), gridspec_kw={'hspace': 0.5})

#Create a dataframe with 2-bedroom house prices in the biggest zip 
biggest_zip_2bedroom= Zillow[(Zillow['zip'] == biggest_zip) & (Zillow['Bedroom'] == 2)].iloc[:, 9:-1]

for i in bedroom_counts:
 #Select the df given bedroom count
    house_prices_values = Zillow[(Zillow['zip'] == biggest_zip) & (Zillow['Bedroom'] == i)].iloc[:, 9:-1]
    house_prices_values = house_prices_values.iloc[0].values
    
    dates = pd.to_datetime(biggest_zip_2bedroom.columns)
    current_date = datetime.datetime.now().strftime("%B %Y")

    axes[i - 2].plot(dates, house_prices_values, linestyle='-')  # Subtract 2 to match the index
    axes[i - 2].set_title(f'{i}-Bedroom House Prices in the Most Listed Zip Code')
    axes[i - 2].set_xlabel('Date')
    axes[i - 2].set_ylabel('House Prices (CPI adjusted, 1982-1984=100)')
    
    axes[i - 2].annotate(f"Note: Most listed zip code as of {current_date} is {biggest_zip} in the state {State_biggest_zip}, city {City_biggest_zip}", xy=(0.5, -0.2), xycoords="axes fraction", fontsize=9, ha="center")
#save the plot

plt.savefig('Plots/Prices.png')

plt.show()

#Bar Plot of the cities that contain the zip codes with most expensive 2-bedroom houses
two_bedroom_houses = Zillow[Zillow['Bedroom'] == 2]
sorted_top_10_prices = two_bedroom_houses.sort_values(by='2023-08-31', ascending=False).head(10)

# Select the top 10 cities and their corresponding house prices
top_10_city_zip = 'zip ' + sorted_top_10_prices['zip'].astype(str) + ' in ' + sorted_top_10_prices['City']
top_10_prices = sorted_top_10_prices['2023-08-31']

# Create a bar plot
plt.figure
plt.ticklabel_format(axis='y', style='plain') 
plt.bar(top_10_city_zip, top_10_prices)
plt.title('Zip Codes with the Most Expensive 2-Bedroom Houses')
plt.xlabel('Zip, City')
plt.ylabel('House Prices (CPI adjusted prices 1982=100)')
plt.xticks(rotation=90)

plt.savefig('Plots/Expensive.png')

plt.show()


#Bar Plot of the cities that contain the zip codes with cheapest 2-bedroom houses
two_bedroom_houses = Zillow[Zillow['Bedroom'] == 2]
sorted_bottom_10_prices = two_bedroom_houses.sort_values(by='2023-08-31', ascending=True).head(10)

# Select the top 10 cities and their corresponding house prices
bottom_10_city_zip = 'zip ' + sorted_bottom_10_prices['zip'].astype(str) + ' in ' + sorted_bottom_10_prices['City']
bottom_10_prices = sorted_bottom_10_prices['2023-08-31']

# Create a bar plot
plt.figure
plt.ticklabel_format(axis='y', style='plain') 
plt.bar(bottom_10_city_zip, bottom_10_prices)
plt.title('Zip Codes with the Leasy Expensive 2-Bedroom Houses')
plt.xlabel('Zip, City')
plt.ylabel('House Prices (CPI adjusted prices 1982=100)')
plt.xticks(rotation=90)

plt.savefig('Plots/Cheap.png')

plt.show()

### Walk Index
################################

#Scatter Plot of Walk vs Bike Score
plt.scatter(house_prices['Walk Score'], house_prices['Bike Score'], alpha=0.5) 
plt.ylabel('Bike Score')
plt.xlabel('Walk Score')
plt.title('Scatter Plot of Bike Score vs. Walk Score')

plt.savefig('Plots/Walk_Bike.png')

plt.show()

#Scatter Plot of House Prices and Walk Score
plt.scatter(house_prices['Walk Score'], house_prices['2023-08-31'], alpha=0.5)
plt.title('Scatter Plot of Walk Score vs. House Prices')
plt.xlabel('Walk Score')
plt.ylabel('House Prices at the Date 2023-08-31')

plt.show()
plt.savefig('Plots/Walk_Price.png')

#Scatter Plot of House Prices and Bike Score
plt.scatter(house_prices['Bike Score'], house_prices['2023-08-31'], alpha=0.5)
plt.title('Scatter Plot of Bike Score vs. House Prices')
plt.xlabel('Bike Score')
plt.ylabel('House Prices at the Date 2023-08-31')

plt.savefig('Plots/Bike_Price.png')

plt.show()

#Now create a subsample to do the analysis

#Drop the columns we don't need
## Drop columns from 2000 to 2018
pattern = r'^(2000|2001|2002|2003|2004|2005|2006|2007|2008|2009|2010|2011|2012|2013|2014|2015|2016|2017|2018)'

columns_to_drop = house_prices.filter(regex=pattern)
house_prices.drop(columns=columns_to_drop.columns, inplace=True)

house_prices.to_csv('Data/clean/Sample.csv')
