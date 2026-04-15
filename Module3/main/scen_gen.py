import copy
import os

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def update_table(path_ref_file,path_conf_file, years,var_list,var_time,var_name, asset_name):

	csv_header_1 = pd.read_csv(path_ref_file, sep=";")
	csv_header_2 = pd.read_csv(path_ref_file)

	ref_table = pd.read_csv(path_ref_file, sep=";") if len(csv_header_1.columns) >= len(
		csv_header_2.columns) else pd.read_csv(path_ref_file)

	#ref_table = pd.read_csv(path_ref_file, sep=',', header=0)
	conf_table = pd.read_csv(path_conf_file, sep=',', header=0)

	periods = np.arange(0,years,5)+5
	n_periods = years/5

	ref_values_updated = {}
	variable_list = np.array(conf_table["variables"])
	function_list = np.array(conf_table["function"])
	factor_list = np.array(conf_table["factor"])

	operation = {"exponential": exponential, "linear": linear, "incremental": incremental}

	ref_filename = path_ref_file.split('/')[-1] if len(path_ref_file.split('/')) != 0 else path_ref_file.split('\\')[-1]
	saved_path = os.path.join('../Result/future_scen', asset_name)
	os.makedirs(saved_path, exist_ok=True)
	saved_ref_path = os.path.join(saved_path, ref_filename)
	ref_table.to_csv(f'{os.path.splitext(saved_ref_path)[0]}.csv', index=False)

	for i, year in enumerate(periods):
		ref_values_updated[year] = {var_name: list(ref_table[var_name])}
		if var_time:
			ref_values_updated[year].update({var_time: list(ref_table[var_time]+year)})
			ref_values_updated[year].update({var: operation[function_list[variable_list==var][0]](np.array(ref_table[var]), year,n_periods, factor_list[variable_list == var][0])[i] for var in var_list})
		else:
			ref_values_updated[year].update({var: operation[function_list[variable_list==var][0]](np.array(ref_table[var]), year,n_periods, factor_list[variable_list == var][0])[i] for var in var_list})

		pd.DataFrame.from_dict(ref_values_updated[year]).to_csv(f'{os.path.splitext(saved_ref_path)[0]}_{year}.csv', index=False)

	return ref_values_updated


def exponential(init_values, years,n_periods, factor, iterations=100, variability = 1000):
	indexes = [np.array(np.random.randint(0,variability,iterations)) for i in init_values]

	x_0s = np.log(1-init_values)/factor

	x = np.array([np.linspace(x_0, x_0+years,variability) for x_0 in x_0s])
	y = np.sort(np.array([1-np.exp(factor*x[i])[indexes[i]] for i in range(len(indexes))]))

	year_ranges = np.linspace(0,iterations,int(n_periods)+1).astype(int)
	y = np.array([np.round(np.mean(y[:,year_ranges[i]:year_ranges[i+1]],axis=1),3) for i in range(len(year_ranges)-1)])

	return y


def linear(init_values, years,n_periods, factor, iterations=100, variability = 1000):

	indexes = np.array([np.random.randint(0,variability,iterations) for i in init_values])

	transition = np.linspace(1, factor, variability)

	var = np.sort(init_values[:,np.newaxis]*transition[indexes])

	year_ranges = np.linspace(0, iterations, int(n_periods) + 1).astype(int)
	var = np.array([np.round(np.mean(var[:, year_ranges[i]:year_ranges[i + 1]], axis=1),3) for i in range(len(year_ranges) - 1)])

	return var

def incremental(init_values, years, *args):
	return np.array(init_values + years).astype(init_values.dtype)



