from plotly.subplots import make_subplots
import plotly.graph_objects as go
import copy
import numpy as np
import json
import os
import pandas as pd
import keras

def tool_readCSVFile(filePath, numeric_table=False):
	headers = []
	selectedHeader = ""

	csv_header_1 = pd.read_csv(filePath, sep=";", decimal=",", index_col=0, nrows=0)
	csv_header_2 = pd.read_csv(filePath, index_col=0, nrows=0)
	if numeric_table:
		try:
			csv_reader = pd.read_csv(filePath, sep=";", decimal=",", dtype=np.float32) if csv_header_1.columns.__len__() >= csv_header_2.columns.__len__() else pd.read_csv(filePath,decimal=",", dtype=np.float32)
		except:
			csv_reader = pd.read_csv(filePath, sep=";",  dtype=np.float32) if csv_header_1.columns.__len__() >= csv_header_2.columns.__len__() else pd.read_csv(filePath,dtype=np.float32)
	else:
		csv_reader = pd.read_csv(filePath, sep=";", decimal=",") if csv_header_1.columns.__len__() >= csv_header_2.columns.__len__() else pd.read_csv(filePath)
	return csv_reader


def generate_prediction_dashboard(model_path,error_model_path, inputfile_path, current_varname, oil_varname, winding_varname, sheet_name=0):
	
	mse_varname = "mse"
	std_varname = "sem"
	
	filename, file_extension = os.path.splitext(inputfile_path)

	if file_extension == ".csv":
		df = tool_readCSVFile(inputfile_path)
	elif (file_extension == ".xls" or  file_extension == ".xlsx"):
		df = pd.read_excel(inputfile_path,sheet_name=sheet_name)
	else:
		df = pd.read_excel(inputfile_path,sheet_name=sheet_name)

	input_current = copy.deepcopy(np.array(df[current_varname], "float32"))
	input_winding_temp = copy.deepcopy(np.array(df[winding_varname], "float32"))
	input_oil_temp = copy.deepcopy(np.array(df[oil_varname], "float32"))

	input_data = np.vstack((input_current.flatten(), input_oil_temp.flatten())).transpose()
	reference_data = input_winding_temp.flatten()[:, np.newaxis]
	model = keras.models.load_model(model_path)

	error_filename, error_file_extension = os.path.splitext(error_model_path)
	if error_file_extension == ".npy":
		model_error = np.load(error_model_path, allow_pickle=True).item()
	elif error_file_extension == ".json":
		with open(error_model_path) as f:
			model_error = json.load(f)
	elif error_file_extension == ".csv":
		model_error = tool_readCSVFile(error_model_path, numeric_table=True)


	output_data = model.predict(input_data)


	test_prediction = copy.deepcopy(reference_data.flatten())
	test_reference = copy.deepcopy(output_data.flatten())


	test_reference_upper_threshold = test_reference + float(np.sqrt(model_error[mse_varname]+2*model_error[std_varname]))
	test_reference_lower_threshold = test_reference - float(np.sqrt(model_error[mse_varname]+2*model_error[std_varname]))
	min_ref = np.nanmin((test_reference,test_prediction,test_reference_lower_threshold))
	max_ref = np.nanmax((test_reference,test_prediction,test_reference_lower_threshold))
	test_reference_upper_threshold[np.isnan(test_reference)] = -9999*np.abs(min_ref)
	test_reference_lower_threshold[np.isnan(test_reference)] = -9999*np.abs(min_ref)


	test_prediction_good =  copy.deepcopy(test_prediction)
	test_prediction_unknown =  copy.deepcopy(test_prediction)
	test_prediction_out_all =  copy.deepcopy(test_prediction)
	test_prediction_out =  np.array([None]*len(test_prediction))

	test_prediction_good[test_prediction>test_reference_upper_threshold] = None #test_prediction_good[np.logical_or(test_prediction<test_reference_lower_threshold,test_prediction>test_reference_upper_threshold)] = None
	test_prediction_unknown[np.logical_not(np.isnan(test_reference))] = None
	mask_out_numeric = np.where(test_prediction>test_reference_upper_threshold)[0] #np.where(np.logical_not(np.logical_and(test_prediction>test_reference_lower_threshold,test_prediction<test_reference_upper_threshold)))[0]
	mask_out_numeric = np.hstack([mask_out_numeric,mask_out_numeric+1,mask_out_numeric-1])
	mask_out_numeric = mask_out_numeric[np.logical_and(mask_out_numeric>=0, mask_out_numeric<len(test_prediction))]#mask_out[np.logical_and(mask_out>0, mask_out<len(test_prediction))]
	mask_out = np.array([False]*len(input_current))
	mask_out[mask_out_numeric]  = True
	test_prediction_out[mask_out] = test_prediction_out_all.flatten()[mask_out]

	mask_out_simple = np.array([False]*len(test_prediction))
	mask_out_simple[mask_out_numeric] = True

	samples_out_threshold = test_reference
	samples_out_threshold[np.square(test_prediction-test_reference)>float(model_error[mse_varname]+2*model_error[std_varname])] = None
	x_vector = np.arange(len(test_reference))

	indicator_percentages = np.array([0.5,0.3,0.2])
	indicator_ranges = [range(int(len(input_current)*np.sum(indicator_percentages[:i])),int(len(input_current)*np.sum(indicator_percentages[:i+1]))) for i in range(len(indicator_percentages))]
	indicator_values = [[np.sum(np.array(mask_out_simple)[indicator_ranges[i]]),indicator_ranges[i].__len__()]  for i in range(indicator_ranges.__len__())]
	indicator_values.append([np.sum(np.array(mask_out_simple)), mask_out.__len__()])
	indicator_names = ["Old Past","Mid Past","Near Past"] #[f"{int(np.sum(indicator_percentages[:i])*100)}%-{int(np.sum(indicator_percentages[:i+1])*100)}%"  for i in range(indicator_ranges.__len__())]
	indicator_names.append("Total")
	color_vbox = ["#594B46","#F2C230", "#D9AE79" ]

	fig = make_subplots(rows=4, cols=5, shared_xaxes=True, subplot_titles=('Current [A]','Oil Temperature [ºC]',None,None,'Winding Temperature [ºC]', "Test Winding Temperature [ºC]",None,None),
						specs=[[{"type": "xy", "rowspan": 2, "colspan": 2},None, {"type": "xy", "rowspan": 2, "colspan": 2},None,{"type": "domain"}],
							   [None,None,None,None,{"type": "domain"}],
							   [{"type": "xy", "rowspan": 2, "colspan": 2},None, {"type": "xy", "rowspan": 2, "colspan": 2},None,{"type": "domain"}],
							   [None, None,None,None,{"type": "domain"}]],
						)


	fig.add_trace(go.Scatter(x=x_vector, y=test_reference_lower_threshold,fill=None,mode='lines',line_color='rgba(0,0,0,0)',  hoverinfo='skip'),row=3, col=3)
	fig.add_trace(go.Scatter(x=x_vector, y=test_reference_upper_threshold,fill='tonexty',mode='lines', line_color='rgba(33,44,85,0)',  hoverinfo='skip'),row=3, col=3)
	fig.add_trace(go.Scatter(x=x_vector, y=test_prediction_good,marker=dict(color='#3DD862'), name="Good"),row=3, col=3)
	fig.add_trace(go.Scatter(x=x_vector, y=test_prediction_unknown,marker=dict(color='#FEE241'),name="Unknow"),row=3, col=3)
	fig.add_trace(go.Scatter(x=x_vector, y=test_prediction_out,marker=dict(color='#FF433D'),name="Warning"),row=3, col=3)

	#fig.add_trace(go.Scatter(x=x_vector, y=test_reference, marker=dict(color="#212C55")), row=2, col=2)
	#fig.add_trace(go.Scatter(x=x_vector, y=test_prediction, marker=dict(color="#212C55")), row=2, col=2)

	fig.add_trace(go.Scatter(x=x_vector, y=input_current, marker=dict(color="#212C55"),name=""), row=1, col=1)
	fig.add_trace(go.Scatter(x=x_vector, y=input_oil_temp, marker=dict(color="#212C55"),name=""), row=1, col=3)
	fig.add_trace(go.Scatter(x=x_vector, y=input_winding_temp, marker=dict(color="#212C55"),name=""), row=3, col=1)

	[fig.add_vrect(x0=indicator_ranges[i][0], x1=indicator_ranges[i][-1],
				  annotation_text=indicator_names[i], annotation_position="top left",
				  fillcolor=color_vbox[i], opacity=0.25, line_width=0, row=3, col=3) for i in range(indicator_names.__len__()-1)]


	for i in range(indicator_ranges.__len__()+1):
		fig.add_trace(go.Pie(labels=["Anomalous", "Correct"],values=[indicator_values[i][0], indicator_values[i][1]], name="", marker_colors=["#F21113", "#212C55"]),row=i+1, col=5)

	fig.update_yaxes( range=[min_ref-np.abs(min_ref)*.02, max_ref+np.abs(max_ref)*.02], row=3, col=3)

	fig.update_xaxes(matches='x', showticklabels=True)

	fig.layout['xaxis3']['title']='Samples'
	fig.layout['xaxis4']['title']='Samples'
	fig.layout["yaxis3"]["matches"] = "y3"
	fig.layout["yaxis4"]["matches"] = "y3"

	fig.update_layout(showlegend=False)
	#fig.update_layout( annotations=[dict(text=indicator_names[i], x=0.96, y=0.9-0.87/(indicator_ranges.__len__())*i, font_size=20, showarrow=False, xanchor  ="left", xref='paper', yref='paper') for i in range(indicator_ranges.__len__()+1)])
	[fig._layout["annotations"].append(dict(text=indicator_names[i], x=0.96, y=0.95-0.9/(indicator_ranges.__len__())*i, font_size=20, showarrow=False, xanchor  ="left", xref='paper', yref='paper')) for i in range(indicator_ranges.__len__()+1)]
	fig.update_layout(annotations=fig._layout["annotations"])
	fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text}</b>') if (a["xanchor"]!='left' or a["xref"]!='paper') else True)

	fig.write_html("./static\\results_condition_monitoring\\" + "condition_monitoring.html")


	template_head = open("./static\\resources/template_head.html", 'r').read()

	logo_header ='<img src="../resources/logo.png" alt="Logo_attest" style="position:absolute;top: 20px;left: 20px; z-index: 1;" height="55">'
	with open("./static\\results_condition_monitoring\\" + "condition_monitoring.html", 'w') as file:
		file.write( fig.to_html().replace("<body>", "<body>" +logo_header))



