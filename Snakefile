rule analyze_data:
    input:
        file = 'Data/clean/Sample.csv'

rule explore_data:
    input:
        file = 'Data/clean/Data.csv'
    output:
        file = 'Data/clean/Sample.csv'
    shell:
        'python Data_Exploration.py'


DATA = ['Zillow', 'CPI', 'Walk', 'Census', 'Commute']

rule prepare_data:
    input:
        expand('Data/raw/{dataset}.csv', dataset=DATA)
    output:
        file = 'Data/clean/Data.csv'
    shell:
        'python Data_Preparation.py'


rule download_data:
    input:
        script = 'Data_Download.py'
    output:
        file = 'Data/raw/{dataset}.csv'
    shell:
        'python {input.script}'