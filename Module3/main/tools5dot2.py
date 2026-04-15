import pandas as pd
import numpy as np
import os

def read_file1(path, col_name):
    csv_header_1 = pd.read_csv(path, sep=";")
    csv_header_2 = pd.read_csv(path)

    df = pd.read_csv(path, sep=";", index_col=col_name) if len(csv_header_1.columns) >= len(
        csv_header_2.columns) else pd.read_csv(path, index_col=col_name)

    #df = pd.read_csv(path, index_col=col_name)
    df= df.select_dtypes(include=np.number)
    NormalizeData= lambda x: (x- x.min(axis=0)) / (x.max(axis=0) - x.min(axis=0))
    data = df.apply(NormalizeData)
    return data

def sum(weight, dataset, column_name):
    weights = pd.Series(weight, index=dataset.columns)
    new_data = dataset * weights
    new_data = new_data.sum(axis=1)
    sum_data = pd.DataFrame(new_data, columns=[column_name])
    return sum_data

def tool5dot2_calculate(config, file_name, years, save_results_to):
    periods = np.arange(0,years,5)+5
    n_periods = years/5

    data = pd.DataFrame()
    for i, cfg in enumerate(config):
        dataset = read_file1(cfg['path'], cfg['index'])

        if i == 0:
            data = sum([float(weight) for weight in cfg['weights']], dataset[cfg['variables']], cfg['config'].upper())
        else:
            data[cfg['config'].upper()] = sum([float(weight) for weight in cfg['weights']], dataset[cfg['variables']], cfg['config'].upper())

    data['total indicator'.upper()] = data.sum(axis=1)/len(data.columns)
    data = data.round(decimals=3)

    if not os.path.exists(save_results_to):
        os.makedirs(save_results_to)

    data.to_csv(f'{save_results_to}/{file_name}.csv')

    for i, year in enumerate(periods):
        data.to_csv(f'{save_results_to}/{file_name}_{year}.csv')

    data.sort_values('total indicator'.upper(), inplace=True, ascending=False)


    return data

