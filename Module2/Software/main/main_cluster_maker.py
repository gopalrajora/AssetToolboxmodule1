import sys, os
if sys.executable.endswith('pythonw.exe'):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.path.join(os.getenv('TEMP'), 'stderr-{}'.format(os.path.basename(sys.argv[0]))), "w")
    
from lib_cluster_maker import *


def input_data(data: pd.DataFrame):

	types_standard = {'Clustering':"clustering"} ## NOT MODIF


	assessment_input_types = 'Clustering'
	
	vars_list = data.columns.values.tolist()
	data['name'] = data.index.values
	asset_types_default = ["Assets"]
	index_tag = "name"
	filter_index_tag = [""]

	include_extra_info_file = [False]

	asset_filter_var_name = False


	print(vars_list)

	




	# Resuls saving options
	save_assessment = True
	save_number_clusters = True
	save_training_process = True
	saving_configuration = {"assessment":save_assessment,"clustering":save_number_clusters,"training":save_training_process}

	types_included = [file_type in assessment_input_types for  file_type in list(types_standard.values())]
	types_std = types_standard

	print("\nLoading data into memory \n")
	file_idx = 0

	output_path = '../HTML_ASSETS/results/'

	class_id_vars = ['asset_classifier', index_tag] + vars_list
	title = "Assets"
	template_path = '../HTML_ASSETS/resources/template_table.html'
	assessment_type = 'total'
	data.sort_values(vars_list[-1], inplace=True, ascending=False)
	build_table_html(data, class_id_vars, title, template_path, output_path+'assets_table.html', assessment_type)



	fig = compute_map(data, vars_list, asset_types_default, output_path,
							  assessment_type=assessment_input_types, classifier_var=asset_filter_var_name, tag_var=[index_tag], saving_configuration = saving_configuration)

	fig.write_html(output_path+"main_" + assessment_input_types + ".html")
	# fig.show()
	# fig.add_trace(data= data,layout=layout row=row, col=col)
	# include_main_button(output_path+"main_" + assessment_input_types + ".html", assessment_input_types,list(types_standard.values()), types_included)
	

	

