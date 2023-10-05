DATA = ['Zillow', 'CPI', 'Walk', 'Census', 'Commute']

rule explore_data:
    input:
        file = 'Data/clean/Data.csv'

rule prepare_data:
    input:
        expand('Data/raw/{dataset}.csv', dataset=DATA)
    output:
        file = 'Data/clean/Data.csv'

rule download_data:
    input:
        script = 'Data_Download.py'
    output:
        file = 'Data/raw/{dataset}.csv'
    shell:
        'python {input.script}'