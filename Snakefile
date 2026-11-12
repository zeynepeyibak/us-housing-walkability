RAW = ["Zillow", "CPI", "Walk", "Census", "Commute"]
PLOTS = ["Prices", "Expensive", "Cheap", "Walk_Bike", "Walk_Price", "Bike_Price"]
TABLES = ["summary_1", "summary_2", "summary_3"]


rule all:
    input:
        "Output.pdf"


rule download_data:
    input:
        "Data_Download.py"
    output:
        expand("Data/raw/{dataset}.csv", dataset=RAW)
    shell:
        "python Data_Download.py"


rule prepare_data:
    input:
        "Data_Preparation.py",
        expand("Data/raw/{dataset}.csv", dataset=RAW)
    output:
        "Data/clean/Data.csv"
    shell:
        "python Data_Preparation.py"


rule explore_data:
    input:
        "Data_Exploration.py",
        "Data/clean/Data.csv"
    output:
        expand("Plots/{plot}.png", plot=PLOTS)
    shell:
        "python Data_Exploration.py"


rule analyze_data:
    input:
        "Analysis.py",
        "Data/clean/Data.csv"
    output:
        expand("Tables/{table}.tex", table=TABLES)
    shell:
        "python Analysis.py"


rule report:
    input:
        "Output/Output.tex",
        expand("Plots/{plot}.png", plot=PLOTS),
        expand("Tables/{table}.tex", table=TABLES)
    output:
        "Output.pdf"
    shell:
        "pdflatex -interaction=nonstopmode Output/Output.tex"
