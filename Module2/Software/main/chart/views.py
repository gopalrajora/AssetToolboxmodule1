from django.shortcuts import render
from django.core.cache import cache
import sys
import shutil
import os
import json
import numpy as np
from django.http import HttpResponse
# Create your views here.
from chart.lib.main_cluster_maker import *
from chart.lib.lib_cluster_maker import *
from pathlib import Path
from threading import Timer

def main(request):

    if os.path.isfile("./static/results_condition_characterization/main_life_assessment.html"):
        main_url = "results_condition_characterization/main_life_assessment.html"
    elif os.path.isfile("./static/results_condition_characterization/main_economic_impact.html"):
        main_url = "results_condition_characterization/main_economic_impact.html"
    elif os.path.isfile("./static/results_condition_characterization/main_maintenance_strategy.html"):
        main_url = "results_condition_characterization/main_maintenance_strategy.html"
    else:
        main_url = "results_condition_characterization/main_life_assessment.html"

    return render(request,main_url)


def main_la(request):
    return render(request,"results_condition_characterization/main_life_assessment.html")

def main_ei(request):
    return render(request,"results_condition_characterization/main_economic_impact.html")

def main_ms(request):
    return render(request,"results_condition_characterization/main_maintenance_strategy.html")

def restore_main_la(request):
    dimension_name = "life_assessment"
    dirContents = [file for file in os.listdir("./static/results_condition_characterization/restore_files") if dimension_name in file]
    [shutil.copy("./static/results_condition_characterization/restore_files/"+file,"./static/results_condition_characterization/"+file) for file in dirContents]
    return render(request,f"results_condition_characterization/main_{dimension_name}.html")

def restore_main_ei(request):
    dimension_name = "economic_impact"
    dirContents = [file for file in os.listdir("./static/results_condition_characterization/restore_files") if dimension_name in file]
    [shutil.copy("./static/results_condition_characterization/restore_files/"+file,"./static/results_condition_characterization/"+file) for file in dirContents]
    return render(request,f"results_condition_characterization/main_{dimension_name}.html")


def restore_main_ms(request):
    dimension_name = "maintenance_strategy"
    dirContents = [file for file in os.listdir("./static/results_condition_characterization/restore_files") if dimension_name in file]
    [shutil.copy("./static/results_condition_characterization/restore_files/"+file,"./static/results_condition_characterization/"+file) for file in dirContents]
    return render(request,f"results_condition_characterization/main_{dimension_name}.html")


def filter_main_la(request):
    cache.clear()
    return render(request,"results_condition_characterization/filter_life_assessment.html")

def filter_main_ei(request):
    cache.clear()
    return render(request,"results_condition_characterization/filter_economic_impact.html")

def filter_main_ms(request):
    cache.clear()
    return render(request,"results_condition_characterization/filter_maintenance_strategy.html")


def compute_graph(request):
    types_standard = {'Economic Impact':"economic_impact", 'Maintenance Strategy':"maintenance_strategy",'Life Assessment':"life_assessment"} ## NOT MODIF

    filter_val = request.POST["filter_value"]
    filter_conf = json.loads(filter_val)

    output_path = 'static/results_condition_characterization/'

    data_path = f"static/results_condition_characterization/store_vars/{filter_conf['assessment_type']}_chart_vars.json"

    with open(data_path) as fp:
        data = json.load(fp)

    filter_path = f"static/results_condition_characterization/store_vars/{filter_conf['assessment_type']}_loaded_filter_conf.json"

    with open(filter_path, "w") as fp:
        json.dump(filter_val, fp)

    data_values = pd.DataFrame.from_dict(data["data_x_no_norm"])

    filter_array = np.array([True] * data_values.__len__())

    for var_name in data_values.columns:
        filter_array = np.logical_and(filter_array, filtering_numerical(data_values, var_name, filter_conf))

    for var_name in data_values.columns:
        filter_array = np.logical_and(filter_array, filtering_categorical(data_values, var_name, filter_conf))

    filter_array = filter_array if filter_conf["mode"] == "include" else np.logical_not(filter_array)

    filtered_values = np.array(["nasset"] * data_values.__len__())
    filtered_values[filter_array] = "Filter"

    data["classifier_var"] = "Filtered Assets"
    data["asset_type_list"] = filtered_values
    # file_name = output_path + 'store_vars/' + assessment_type + '_chart_vars.json'


    fig = compute_map_preloaded(output_path, data)
    fig.write_html(output_path + "main_" + filter_conf['assessment_type'] + ".html")

    types_included = [Path("static/results_condition_characterization/main_"+file+".html").is_file() for file in types_standard.values()]

    include_main_button(output_path, filter_conf['assessment_type'], filter_conf['assessment_type'],list(types_standard.values()),types_included, data["asset_type_default"])

    cache.clear()
    return render(request, "results_condition_characterization/main_" + filter_conf['assessment_type'] + ".html")


def close_app(request):

    pid = os.getpid()
    t = Timer(5.0,kill_process,[pid])
    t.start()
    return render(request, "resources/template_close_page.html")


def kill_process(id):
    print(f"App with {id} disconnected")
    os.kill(id,-1)


def filtering_numerical(data, var_name, filter_conf):
    filter_variable = [filter for filter in filter_conf["numerical"] if filter["name"] == var_name]
    if filter_variable != []:
        filter_variable = filter_variable[0]
        valid_values = True

        try:
            if filter_variable["mode"] == "btw":
                np.float(filter_variable["value"][0])
                np.float(filter_variable["value"][1])
            else:
                np.float(filter_variable["value"][0])
        except:
            valid_values = False

        if filter_variable["mode"] == "gr" and valid_values:
            mask_filter = np.array(data[var_name] >= np.float(filter_variable["value"][0]))
        elif filter_variable["mode"] == "lo" and valid_values:
            mask_filter = np.array(data[var_name] <= np.float(filter_variable["value"][0]))
        elif filter_variable["mode"] == "eq" and valid_values:
            mask_filter = np.array(data[var_name] == np.float(filter_variable["value"][0]))
        elif filter_variable["mode"] == "btw" and valid_values:
            mask_filter = np.logical_and(np.array(data[var_name] >= np.float(filter_variable["value"][0])),
                                         np.array(data[var_name] <= np.float(filter_variable["value"][1])))
        else:
            mask_filter = np.array([True] * data[var_name].__len__())
    else:
        mask_filter = np.array([True] * data[var_name].__len__())

    return mask_filter

def filtering_categorical(data, var_name, filter_conf):

    filter_variable = [filter for filter in filter_conf["categorical"] if filter["name"] == var_name]
    if filter_variable != []:
        filter_variable = filter_variable[0]
        filter_values = filter_variable['value']
        if filter_values != []:
            values = np.array(data[var_name])
            mask_filter = np.array([value in filter_values for value in values])
        else:
            mask_filter = np.array([True] * data[var_name].__len__())
    else:
        mask_filter = np.array([True] * data[var_name].__len__())
    return mask_filter

