#import packages
import numpy as np
import pandas as pd
import statsmodels as sm
import statsmodels.formula.api as smf
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant
from statsmodels.iolib.summary2 import summary_col
from linearmodels.panel import PanelOLS

#load data
data = pd.read_csv('Data/clean/Sample.csv')

#drop unnecessary columns
columns_to_drop = ['Unnamed: 0.1', 'Unnamed: 0', 'Unnamed: 0_x']
# Drop the specified columns
data.drop(columns=columns_to_drop, inplace=True)                   

#change format of data to long
data = data.melt(id_vars=['SizeRank', 'zip','State', 'City', 'CountyName',
       'Bedroom', 'Average_2021', 'Average_2022', 'Average_2023',
       'Growth_2021_to_2022', 'Growth_2022_to_2023', 'Unnamed: 0_y',
       'Walk Score', 'Transit Score', 'Bike Score', 'pct_younger_35',
       'pct_black', 'pct_less_HS', 'pct_bsc_higher', 'Short Commute',
       'Moderate Commute', 'Long Commute'])

#rename columns
data = data.rename(columns={
    'variable': 'date',
    'value': 'price',
    'Walk Score': 'walk_score',
    'Bike Score': 'bike_score',
    'Transit Score': 'transit_score',
    'Short Commute': 'short_commute',
    'Long Commute': 'long_commute'})


#simple regression
reg1 = smf.ols('price ~ Bedroom', data=data)
results1 = reg1.fit(cov_type='HC1') 


reg2 = smf.ols('price ~ Bedroom + walk_score', data=data)
results2 = reg2.fit(cov_type='HC1') 

reg3 = smf.ols('price ~ Bedroom + walk_score + bike_score', data=data)
results3 = reg3.fit(cov_type='HC1') 

#create table with results
info_dict={'R-squared' : lambda x: "{:.2f}".format(x.rsquared),
           'No. observations' : lambda x: "{0:d}".format(int(x.nobs))}

results_table_1 = summary_col(results=[results1,results2, results3],
                            float_format='%0.2f',
                            stars = True,
                            model_names=['Model 1',
                                         'Model 2',
                                         'Model 3'],
                            info_dict=info_dict,
                            regressor_order=['Bedroom',
                                             'walk_score',
                                             'bike_score',
                                             'const'])

results_table_1.add_title('Simple OLS Regressions')



with open('Tables/summary_1.tex', 'w') as file_handle:
    file_handle.write(results_table_1.as_latex())



#Including additional covariates
reg4 = smf.ols('price ~ Bedroom + walk_score + bike_score + short_commute', data=data)
results4 = reg4.fit(cov_type='HC1') 

reg5 = smf.ols('price ~ Bedroom + walk_score + bike_score + short_commute + long_commute', data=data)
results5 = reg5.fit(cov_type='HC1') 

reg6 = smf.ols('price ~ Bedroom + walk_score + bike_score + short_commute + long_commute + Growth_2022_to_2023', data=data)
results6 = reg6.fit(cov_type='HC1') 

#create table
results_table_2 = summary_col(results=[results4,results5, results6],
                            float_format='%0.2f',
                            stars = True,
                            model_names=['Model 4',
                                         'Model 5',
                                         'Model 6'],
                            info_dict=info_dict,
                            regressor_order=['Bedroom',
                                             'walk_score',
                                             'bike_score',
                                             'short_commute',
                                             'long_commute',
                                             'Growth_2022_to_2023',
                                             'const'])

results_table_2.add_title('Regressions Including Additional Covariates')


with open('Tables/summary_2.tex', 'w') as file_handle:
    file_handle.write(results_table_2.as_latex())


## Include fixed effects
## create a year variable
year = []
for i in range(0,len(data.date)):
    x = data.date[i][0:4]
    year.append(int(x))
data['Year'] = year

#run FE regression
data_index = data[['City', 'Year']]
data_index = pd.MultiIndex.from_frame(data_index)
data= data.set_index(data_index )

model = PanelOLS(data.price, data[['Bedroom', 'walk_score', 'bike_score']], entity_effects=True)

results = model.fit(cov_type='clustered', cluster_entity=True)

with open('Tables/summary_3.tex', 'w') as file_handle:
    file_handle.write(results.summary.as_latex().replace("\\toprule", "").replace('\\bottomrule', '').replace('\\midrule', ''))


