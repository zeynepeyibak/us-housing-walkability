#Import Packages
import pandas as pd
import requests
import io
from io import StringIO
import zipfile
#import matplotlib.pyplot as plt
#import seaborn as sns
#import numpy as np

# To get multiple outputs at once
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

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