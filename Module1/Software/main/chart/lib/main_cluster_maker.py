import sys, os
if sys.executable.endswith('pythonw.exe'):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.path.join(os.getenv('TEMP'), 'stderr-{}'.format(os.path.basename(sys.argv[0]))), "w")
    
from chart.lib.lib_cluster_maker import *


def input_data(data):

	types_standard = {'Economic Impact':"economic_impact", 'Maintenance Strategy':"maintenance_strategy",'Life Assessment':"life_assessment"} ## NOT MODIF


	assessment_input_types = [types_standard[e] for e in [d["config"] for d in data]]
	path_files = [d["path"] for d in data]
	aux_path_files = [d["path2"] for d in data]
	vars_list = [d["variables"] for d in data]

	asset_types_default = [data[0]["assestsType"]] if data[0]["assestsType"]!="" else ["Assets"]
	index_tag = [d["component1_field"] for d in data]
	filter_index_tag = [d["component2_field"] for d in data]

	include_extra_info_file = [d["path2"] != "" for d in data]

	asset_filter_var_name = [d["variables2"] if d["variables2"] != "" else False for d in data]


	# Resuls saving options
	save_assessment = True if 'Asset assessment' in data[0]["results"] else False
	save_number_clusters = True if 'Number of Clusters assessment' in data[0]["results"] else False
	save_training_process = True if 'Clustering Training process' in data[0]["results"] else False
	saving_configuration = {"assessment":save_assessment,"clustering":save_number_clusters,"training":save_training_process}

	types_included = [file_type in assessment_input_types for  file_type in list(types_standard.values())]
	types_std = types_standard

	print("\nLoading data into memory \n")
	file_idx = 0

	output_path = 'static/results_condition_characterization/'

	for i in range(data.__len__()):
		if include_extra_info_file[i]:

			fig = compute_map([path_files[i],aux_path_files[i]], vars_list[i], asset_types_default, output_path,
							  assessment_type=assessment_input_types[i], classifier_var=asset_filter_var_name[i], tag_var=[index_tag[i], filter_index_tag[i]], best_of=3, saving_configuration = saving_configuration)

			fig.write_html(output_path + "main_" + assessment_input_types[i] + ".html")
			# fig.show()
			# fig.add_trace(data= data,layout=layout row=row, col=col)
			include_main_button(output_path, assessment_input_types[i], assessment_input_types[i],
								list(types_standard.values()), types_included, asset_types_default)

		else:
			fig = compute_map([path_files[i]], vars_list[i], asset_types_default, output_path,
							  assessment_type=assessment_input_types[i], classifier_var=asset_filter_var_name[i], tag_var=[index_tag[i]], best_of= 3,saving_configuration = saving_configuration)

			fig.write_html(output_path+"main_" + assessment_input_types[i] + ".html")
			# fig.show()
			# fig.add_trace(data= data,layout=layout row=row, col=col)
			include_main_button(output_path, assessment_input_types[i], assessment_input_types[i],list(types_standard.values()), types_included, asset_types_default)

