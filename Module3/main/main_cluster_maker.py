import sys, os
if sys.executable.endswith('pythonw.exe'):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.path.join(os.getenv('TEMP'), 'stderr-{}'.format(os.path.basename(sys.argv[0]))), "w")
import webbrowser
from lib_cluster_maker import *
import numpy as np

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
	


def input_data_2(data_file_path):
    
    csv_files = [file for file in os.listdir(data_file_path) if file.endswith('.csv')]

    folder_name = data_file_path.split('/')[-1] if len(data_file_path.split('/')) != 0 else data_file_path.split('\\')[-1]

    for file in csv_files:
        print('path to track', (os.path.join(data_file_path, file)))
        data = pd.read_csv(os.path.join(data_file_path, file), index_col=0)
        NormalizeData = lambda x: (x - x.min(axis=0)) / (x.max(axis=0) - x.min(axis=0))
        data = data.apply(NormalizeData)

        
        file_name = file.split('.')[0]
        print(file_name)
        
        types_standard = {'Clustering':"clustering"} ## NOT MODIF
        
        assessment_input_types = 'Clustering'
        vars_list = data.columns.values.tolist()
        data['name'] = data.index.values
        asset_types_default = ["Assets"]
        index_tag = "name"
        filter_index_tag = [""]
        
        include_extra_info_file = [False]
        asset_filter_var_name = False
        
        print('Varlist to track', vars_list)
        
		# Resuls saving options
        save_assessment = True
        save_number_clusters = True
        
        save_training_process = True
        saving_configuration = {"assessment":save_assessment,"clustering":save_number_clusters,"training":save_training_process}
        
        types_included = [file_type in assessment_input_types for  file_type in list(types_standard.values())]
        types_std = types_standard
        
        print("\nLoading data into memory \n")
        file_idx = 0
        
        output_path = f'../Result/Clustering and Table/{folder_name}/'

        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        class_id_vars = ['asset_classifier', index_tag] + vars_list
        title = "Assets"
        template_path = '../HTML_ASSETS/resources/template_table.html'
        assessment_type = 'total'
        data.sort_values(vars_list[-1], inplace=True, ascending=False)
        build_table_html(data.round(decimals=3), class_id_vars, title, template_path, output_path+f'assets_table_{file_name}.html', assessment_type)
        
        fig = compute_map(data, vars_list, asset_types_default, output_path,
								assessment_type=assessment_input_types, classifier_var=asset_filter_var_name, tag_var=[index_tag], saving_configuration = saving_configuration)
        
        fig.write_html(output_path+"main_" + assessment_input_types + f"_{file_name}.html")

def show(folder_path):
    html_filenames = [
        os.path.join(folder_path, filename)
        for filename in os.listdir(folder_path)
        if filename.startswith('assets_table') or filename.startswith('main')
    ]
    for html_filename in html_filenames:
        webbrowser.open(html_filename)
