# som_iris.py
# SOM for Iris dataset
# Anaconda3 5.2.0 (Python 3.6.5)

# ==================================================================

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import minisom as MiniSom # Library edited
import re
import os
import shutil
from copy import deepcopy

import scipy
import scipy.cluster.vq
import scipy.spatial.distance
from scipy.signal import argrelextrema
dst = scipy.spatial.distance.euclidean


from plotly.subplots import make_subplots
import plotly.io as pio
import plotly.graph_objects as go

from sklearn.cluster import KMeans
from yellowbrick.cluster import KElbowVisualizer # Library edited


from PIL import Image

import json






def closest_node(data, t, map, m_rows, m_cols):
    """
Returns the index of the closest centroid to data[t]
    :param data: input data in vector format of shape(T,V)
    :param t: index of input vector [0;T-1]
    :param map: centroid values of shape(m_rows*m_cols,V)
    :param m_rows: Number of rows of the SOM
    :param m_cols: Number of columns of the SOM
    :return: Return the index (x,y) of the closest centroid to data[t]
    """
    # (row,col) of map node closest to data[t]
    result = (0, 0)
    small_dist = 1.0e20
    for i in range(m_rows):
        for j in range(m_cols):
            ed = euc_dist(map[i][j], data[t])
            if ed < small_dist:
                small_dist = ed
                result = (i, j)
    return result


def euc_dist(v1, v2):
    """
Computes the euclidean distance between two vectors with the same dimension
    :return: Euclidean distance between V1 and V2
    """
    return np.linalg.norm(v1 - v2)


def manhattan_dist(r1, c1, r2, c2):
    """
Computes the manhattan distance between two coordinates (r1,c1) and (r2,c2)
    :param r1: x coordinate of point A
    :param c1: y coordinate of point A
    :param r2: x coordinate of point B
    :param c2: y coordinate of point B
    :return: Manhattan Distance
    """
    return np.abs(r1 - r2) + np.abs(c1 - c2)




def color_gradient(steps, list_of_colors = [(0,30,97), (5, 83, 96)]):
    """
Computes a gradient of size(steps) between two colors
    :param steps: Size of the gradient
    :param list_of_colors: List with the two colors of the gradient in RGB (255,255,255)
    :return:
    """
    r = np.arange(list_of_colors[0][0],list_of_colors[1][0],(list_of_colors[1][0]-list_of_colors[0][0])/steps).astype(int) if list_of_colors[1][0]!=list_of_colors[0][0] else np.array([list_of_colors[1][0]]*steps)
    g = np.arange(list_of_colors[0][1],list_of_colors[1][1],(list_of_colors[1][1]-list_of_colors[0][1])/steps).astype(int) if list_of_colors[1][1]!=list_of_colors[0][1] else np.array([list_of_colors[1][1]]*steps)
    b = np.arange(list_of_colors[0][2],list_of_colors[1][2],(list_of_colors[1][2]-list_of_colors[0][2])/steps).astype(int) if  list_of_colors[1][2]!=list_of_colors[0][2] else np.array([list_of_colors[1][2]]*steps)

    color_hex_range = ['#%02x%02x%02x' % (r[i], g[i], b[i]) for i in range(steps)]

    return color_hex_range

def set_color_on_background(color):
    """
Determines the color (black or white) that has a better contrast for a particular background color.
    :param color: Background color to compute the maximum contrast.
    :return: Black or White in hex. format.
    """
    color_hex = color.strip("#")
    r, g, b = tuple(int(color_hex[i:i + 2], 16) for i in (0, 2, 4))
    return "#000000" if (r*0.299 + g*0.587 + b*0.114) > 180  else "#ffffff"


def build_table_html(assets, class_id_vars,title, template_path, output_path, assessment_type):
    """
Computes a table in html format to fill the pattern file: "template_table.html"
    :param assets: Table with assets as rows
    :param class_id_vars:  Name of the variables included in the assessment
    :param title: Header of the table
    :param template_path: Path of the file "template_table.html"
    :param output_path: Path to save the new html with the table
    :param assessment_type: Dimension of the asset management
    """
    tag_template_styles = '/*$$$COMPONENTS_STYLES$$$*/'
    tag_template_table = '<!--$$$TABLE$$$-->'
    tag_template_title = "<!--$$$NEURON_INFO_TITLE$$$-->"
    tag_template_main_file = "<!--$$$MAIN_FILE_TITLE$$$-->"

    if class_id_vars[0] in assets.columns:
        asset_types = np.unique(assets[class_id_vars[0]]) if class_id_vars[0] in assets.columns else "Asset"
        asset_type_id = range(len(asset_types))
        asset_colors = color_gradient(len(asset_types))
    else:
        asset_types = ["name"]
        asset_type_id = ["0"]
        asset_colors = color_gradient(1)

    types_html = ""
    for i in range(len(asset_type_id)):
        types_html += f"""
    tr.style_{asset_type_id[i]} th {{
      background: {asset_colors[i]};
      color: {set_color_on_background(asset_colors[i])};
    }}
    """

    assets_list_html = ""
    for i in range(len(asset_types)):

        headers = ''.join([f"<th onclick=sortTable({iii+1},{i})>{var_name}</th>" for iii,var_name in enumerate(class_id_vars[1:])]) #The first element of var_names is the id of the assets
        if i == 0:
            assets_list_html += f"""
            <thead>
                <tr class="style_{asset_type_id[i]}" id="TD">
                  <th>{asset_types[i] if asset_types[i] != 'nasset' else 'Others'}</th>
                  {headers}
                </tr>
            </thead>
            <tbody id="TB{i}">
            """

        else:
            assets_list_html += f"""
            <thead>
            <tr class="style_{asset_type_id[i]}">
                <th>{asset_types[i] if asset_types[i] != 'nasset' else 'Others'}</th>
                {headers}
            </tr>
            </thead>
            <tbody id="TB{i}">
            """

        if class_id_vars:
            assets_details = assets[assets[class_id_vars[0]] == asset_types[i]] if class_id_vars[0] in assets.columns else assets
            for ii in range(len(assets_details)):
                component_info = ''.join([f"<td>{assets_details.iloc[ii][var_name]}</td>" for var_name in class_id_vars[1:]])
                component_info = "<td></td>"+component_info
                assets_list_html += f"""
                <tr>
                    {component_info}
                </tr>
                """
        else:
            assets_details = assets[assets[class_id_vars[0]] == asset_types[i]] if class_id_vars[0] in assets.columns else assets
            for ii in range(len(assets_details)):
                component_info = ''.join([f"<td>{assets_details.iloc[ii][var_name]}</td>" for var_name in class_id_vars[1:]])
                assets_list_html += f"""
                <tr>
                    {component_info}
                </tr>
                """

        assets_list_html += "</tbody>"

    fileTemp = open(template_path, 'r').read().replace(tag_template_styles, types_html)
    fileTemp = fileTemp.replace(tag_template_table, assets_list_html)
    fileTemp = fileTemp.replace(tag_template_title, title)
    fileTemp = fileTemp.replace(tag_template_main_file, "/main_"+assessment_type+".html")


    with open(output_path, 'w') as file:
        file.write(fileTemp)



# ==================================================================

def create_box_chart(data,matching_index,centroids,Rows,Cols,var_names, asset_type_list, assessment_type, asset_type_default=["Assets"]):
    """
Creates the Boxplot chart
    :param data: Table with the attributes of the assessts. Shape(Assets, Variables)
    :param matching_index: Index of the pattern to which each asset belongs. Shape(Rows, Columns)
    :param centroids: List with the values of the centroids of the patterns. Shape(Rows, Columns, Variables)
    :param Rows: Number of Rows of the Self-Organizing Map
    :param Cols: Number of Columns of the Self-Organizing Map
    :param var_names: Names of the Variables
    :param asset_type_list: List with the name or value of each asset. This parameter is used to filter assets of the same type
    :param assessment_type: Dimension of the asset management
    :return: Plotly figure
    """
    
    ommit_keyword = "nasset"
    
    if len(np.unique(asset_type_list)) == 1:
        asset_type_name_all =  asset_type_default[0]
    else:
        asset_type_name_all = "All assets"

    if assessment_type:
        assessment_name = assessment_type
    else:
        assessment_name = "asset_management"

    scales_max =np.max(np.vstack([data.max(axis=0),np.max(np.vstack(centroids),axis=0)]),axis=0)
    scales_min =np.min(np.vstack([data.min(axis=0),np.min(np.vstack(centroids),axis=0)]),axis=0)
    counter = np.array([[np.sum(np.logical_and(matching_index[0]==row, matching_index[1]==col)) for col in range(Cols)] for row in range(Rows)]).flatten()
    counter = np.array([f"Title {idx}" for idx in range(len(counter))])
    scales_min[scales_max.astype(np.float16)==scales_min.astype(np.float16)] = 0


    color_vector_dark = ["#004367","#B48110","#8B1812","#6CA12E", "#3F2E88", "#B35D17", "#025C66", "#4E5359" , "#27348B"]
    color_vector_light = ["#7EC3E8","#FAD679","#F28E7D","#E3ECBC", "#918BC3", "#FBDEBF", "#7DBDC3", "#D1D0D1", "#7EC3E8"]

    if len(var_names) > len(color_vector_dark):
        color_vector_dark = np.tile(color_vector_dark, np.ceil(len(var_names)/len(color_vector_dark)).astype(np.int))
        color_vector_light = np.tile(color_vector_light, np.ceil(len(var_names)/len(color_vector_light)).astype(np.int))

    axis_names = ["y"+str(i+2) for i in range(len(var_names)-1)]
    asset_types = np.unique(asset_type_list)

    fig = make_subplots(rows=int(Rows), cols=int(Cols), start_cell="bottom-left",
                        specs=[[{'type': 'bar',}]*Cols]*Rows,
                        vertical_spacing=0.2,
                        horizontal_spacing=0.1,
                        subplot_titles=counter
                        )

    domain_y = np.array([fig["layout"][f"yaxis{i+1}"]["domain"] for i in range(Cols*Rows)])
    domain_x = np.array([fig["layout"][f"xaxis{i+1}"]["domain"] for i in range(Cols*Rows)])
    scales_max = np.append(scales_max,1)
    scales_min = np.append(scales_min,0)
    number_yaxis = len(var_names)+1

    for row in range(Rows):
        for col in range(Cols):
            title = np.tile((var_names),5)
            detail = np.repeat((["_min", "_Q1", "_med", "_Q3", "_max"]),len(var_names))
            title_detail = [title[i] + detail[i] for i in range(len(title))]

            empty_value_asset_vector = np.array([str(asset_type) for asset_type in asset_types]) != ommit_keyword

            for i,var_name in enumerate(var_names):
                fig.add_trace(go.Box(
                    meta = {"name_id":"box_opaque_all"},
                    x = np.array([var_name]*np.sum(np.logical_and(matching_index[0]==row,matching_index[1]==col))),
                    y = data[np.logical_and(matching_index[0]==row,matching_index[1]==col)][:,i],
                    xaxis=f"x{row*Cols+col+1}" if row*Cols+col+1 > 1 else "x",
                    boxmean=True,
                    quartilemethod = "linear",
                    fillcolor = color_vector_light[i],
                    line= {"color":color_vector_dark[i]},
                    name = var_name),
                    row=row+1, col=col+1)

                fig.add_trace(go.Box(
                    meta={"name_id": "box_all_faded"},
                    x=np.array([var_name] * np.sum(np.logical_and(matching_index[0] == row, matching_index[1] == col))),
                    xaxis=f"x{row * Cols + col + 1}" if row * Cols + col + 1 > 1 else "x",
                    y=data[np.logical_and(matching_index[0] == row, matching_index[1] == col)][:, i],
                    visible=False,
                    #boxmean=True,
                    boxpoints=False,
                    quartilemethod="linear",
                    fillcolor=color_vector_light[i],
                    opacity=0.3,
                    line={"color": color_vector_dark[i]},
                    name=var_name,
                    hoverinfo='skip'),
                    row=row + 1, col=col + 1)

                if len(asset_types) > 1:
                    for asset_type in asset_types[empty_value_asset_vector]:
                        fig.add_trace(go.Box(
                            meta={"name_id": "box_opaque_"+str(asset_type)},
                            x=np.array([var_name] * np.sum(np.logical_and(matching_index[0] == row, matching_index[1] == col))),
                            xaxis=f"x{row * Cols + col + 1}" if row * Cols + col + 1 > 1 else "x",
                            y=data[np.logical_and.reduce((matching_index[0] == row, matching_index[1] == col, asset_type_list == asset_type))][:, i],
                            visible=False,
                            boxmean=True,
                            quartilemethod="linear",
                            fillcolor=color_vector_light[i],
                            line={"color": color_vector_dark[i]},
                            name=var_name),
                            row=row + 1, col=col + 1)

                fig.add_trace(go.Scatter(
                    meta = {"name_id":"centroid"},
                    mode='markers',
                    x = [var_name],
                    xaxis=f"x{row * Cols + col + 1}" if row * Cols + col + 1 > 1 else "x",
                    y=np.array([centroids[row, col][i]]),
                    marker=dict(color='#B84AFF',size=12,
                                line=dict(color='#622582',width=3)),
                    name=var_name),

                    row=row + 1, col=col + 1)

            fig.add_trace(go.Scatter(
                meta={"name_id": "empty_signal"},
                mode='markers',
                x=[var_names[-1]],
                xaxis=f"x{row * Cols + col + 1}" if row * Cols + col + 1 > 1 else "x",
                y=np.array([20]),
                yaxis=f"y{(row*Cols+col)*number_yaxis+ number_yaxis}",
                marker=dict(color='#2758F5', size=0.001,
                            line=dict(color='#2758F5', width=0.001)),
                name=var_names[-1],
                hoverinfo='skip'),
                row=row + 1, col=col + 1)
            #data= [quantile_4,quantile_3,quantile_2,quantile_1,quantile_0]

    ### Custom annotation:
    annotations_all   = fig['layout']['annotations']

    for asset_type_id in range(len(asset_types[empty_value_asset_vector])):
        exec(f"annotations_{asset_type_id} = deepcopy(fig['layout']['annotations'])")


    counter_all = np.array([[np.sum(np.logical_and(matching_index[0]==row, matching_index[1]==col)) for col in range(Cols)] for row in range(Rows)]).flatten()

    for asset_type_id in range(len(asset_types[empty_value_asset_vector])):
        counter_array = np.array([[np.sum(np.logical_and.reduce((matching_index[0] == row, matching_index[1] == col, asset_type_list == asset_types[empty_value_asset_vector][asset_type_id]))) for col in range(Cols)] for row in range(Rows)]).flatten()
        exec(f"counter_{asset_type_id} = counter_array")
    #counter_trafos = np.array([[np.sum(np.logical_and.reduce((matching_index[0] == row, matching_index[1] == col, asset_type_list == 'trafo'))) for col in range(Cols)] for row in range(Rows)]).flatten()
    #counter_lines = np.array([[np.sum(np.logical_and.reduce((matching_index[0] == row, matching_index[1] == col, asset_type_list == 'line'))) for col in range(Cols)] for row in range(Rows)]).flatten()

    for i in range(len(counter)):
        if "Title" in annotations_all[i]["text"]:
            annotations_all[i]['text']= f"<a target='_self' href='{{%static 'results_condition_characterization/{assessment_name}_n{i+1}.html' %}}' style='color:black'>"+f"<b>Pattern {i+1}<br>Assets: {counter_all[i]}, % "+str("{:.2f}".format(counter_all[i]/np.sum(counter_all)*100))+'</b></a>'

        for asset_type_id in range(len(asset_types[empty_value_asset_vector])):
            asset_counter = eval(f"counter_{asset_type_id}[i]")
            format_str = eval(f"counter_{asset_type_id}[i]/np.sum(counter_{asset_type_id})*100")
            html_string = f"<a target='_self' href='{{%static 'results_condition_characterization/{assessment_name}_n{i+1}.html' %}}' style='color:black'>"+f"<b>Pattern {i+1}<br>Assets: {asset_counter}, %:"+str('{:.2f}'.format(format_str))+'</b></a>'
            exec(f"""
if "Title" in annotations_{asset_type_id}[i]["text"]:
    annotations_{asset_type_id}[i]['text']= html_string
""")

        #if "Title" in annotations_lines[i]["text"]:
        #	annotations_lines[i]['text']= f'<a target="_self" href="./Assets_n{i}.html" style="color:black">'+f"<b>Pattern {i+1}, Lines: {counter_lines[i]}, % "+str("{:.2f}".format(counter_lines[i]/np.sum(counter_lines)*100))+"</b></a>"


        list_dicts = list([dict(label=asset_type_name_all if asset_type_name_all != ommit_keyword else "All assets" ,
                      method='update',
                      args=[{'visible': np.logical_or.reduce((
                          np.array([data['meta']['name_id'] for data in fig['data']]) == "box_opaque_all",
                          np.array([data['meta']['name_id'] for data in fig['data']]) == "empty_signal",
                          np.array([data['meta']['name_id'] for data in fig['data']]) == "centroid"))},
                          {'annotations': annotations_all},
                      ])])
        if len(asset_types) > 1:
            for asset_type_id in range(len(asset_types[empty_value_asset_vector])):
                annotations = eval(f"annotations_{asset_type_id}")
                list_dicts.append(dict(label=str(asset_types[empty_value_asset_vector][asset_type_id]),
                              method='update',
                              args=[{'visible': np.logical_or.reduce((
                                    np.array([data['meta']['name_id'] for data in fig['data']]) == "box_all_faded",
                                    np.array([data['meta']['name_id'] for data in fig['data']]) == f"box_opaque_{asset_types[empty_value_asset_vector][asset_type_id]}",
                                    np.array([data['meta']['name_id'] for data in fig['data']]) == "centroid",
                                    np.array([data['meta']['name_id'] for data in fig['data']]) == "empty_signal"))},
                                    {'annotations': annotations}
                                    ],
                              ))

        list_dicts.append(dict(label='Centroids',
                      method='update',
                      args=[{'visible': np.logical_or.reduce((
                          np.array([data['meta']['name_id'] for data in fig['data']]) == "empty_signal",
                          np.array([data['meta']['name_id'] for data in fig['data']]) == "centroid"))},
                          {'annotations': annotations_all}
                      ]))

    updatemenus = list([
        dict(#type="buttons",
             active=0,
             buttons=list_dicts)
    ])




    for i in np.arange(0, Rows * Cols):
        for ii in range(number_yaxis):
            exec(f"""
fig.update_layout(
    yaxis{i * number_yaxis + ii + 1}=dict(autorange=False, range=[scales_min[{ii}], scales_max[{ii}]], gridcolor = "#29235C", gridwidth = 2, domain=domain_y[{i}], anchor="x{i + 1}", showticklabels=False, showgrid=False))
            """)

    for i in range(Rows * Cols):
            fig["layout"][f"yaxis{i * number_yaxis + number_yaxis}"]["showticklabels"] = True
            fig["layout"][f"yaxis{i * number_yaxis + number_yaxis}"]["showgrid"] = True
            fig["layout"][f"yaxis{i * number_yaxis + number_yaxis}"]["visible"] = True


    elements_per_axis = len(np.unique([fig["data"][i]["meta"]["name_id"] for i in range(len(fig["data"]))]))-1 #Empty_signal does not count
    hidden_element_counter = 0
    for i in range(Rows * Cols):
        for ii in range(len(var_names)):
            for iii in range(elements_per_axis):
                fig["data"][i*len(var_names)*elements_per_axis +  ii*elements_per_axis + iii +hidden_element_counter]["yaxis"] = f"y{i*len(var_names)+ii+1+hidden_element_counter}"
        hidden_element_counter += 1
        fig["data"][i*len(var_names)*elements_per_axis +  ii*elements_per_axis + iii +hidden_element_counter]["yaxis"] = f"y{i*len(var_names)+len(var_names)+hidden_element_counter}"


    for i in np.arange(0, Rows * Cols):
        fig["layout"][f"xaxis{i + 1}"]["anchor"] = f"y{i* number_yaxis+ 1}"

    fig.update_layout(
        showlegend = False,
        plot_bgcolor = "#DADADA",
        updatemenus = updatemenus,
        paper_bgcolor= "rgba(0, 0, 0, 0)",
    )



    for i in range(Rows * Cols):
        for ii in range(number_yaxis-1):
                fig["layout"][f"yaxis{i*number_yaxis+ii+1}"]["overlaying"] = f"y{i*number_yaxis+number_yaxis}"

    # fig.add_layout_image(
    #     dict(
    #         source=Image.open("static/resources/logo.png"),
    #         xref="paper", yref="paper",
    #         x=-0.1, y=1.18,
    #         sizex=0.2, sizey=0.2,
    #         xanchor="left", yanchor="top"
    #     )
    # )

    # if asset_type_default != "Assets" and asset_type_default:
    #     fig.update_layout(
    #         title={
    #             'text': f"<span style=\"font-size: 40px;\">{asset_type_default}</span>",
    #             "xref" : "container", "yref" : "container",
    #             'y': 0.95,
    #             'x': 0.5,
    #             'xanchor': 'right',
    #             'yanchor': 'top'})

    return fig

def include_main_button(output_path, assessment_input_type, input_type, types_standard, types_included, asset_types_default=["Assets"]):
    """
Configures the menu button according to the Dimensions loaded.
    :param main_file_path: path of the template
    :param input_type:
    :param types_standard:
    :param types_included:
    """
    main_file_path = output_path+"main_" + assessment_input_type + ".html"

    fileTemp = open(main_file_path, 'r').read()

    template_head = open("./static/resources/template_head.html", 'r').read()
    template_body = open("./static/resources/template_body.html", 'r').read()
    fileTemp = re.sub(r"<head>.*</head>", template_head, fileTemp)

    standard_input_types = types_standard.copy()
    reference_to_input_file_names = [f"main_{standard_input_types[i]}.html" for i in range(len(standard_input_types))]
    type_active = ["-active" if input_type == type_list_element else "" for type_list_element in standard_input_types]
    type_active = [type_active[i] if types_included[i] else  "-disabled" for i in range(len(standard_input_types))]
    reference_to_input_file_names = [reference_to_input_file_names[i] if types_included[i] else  "main" for i in range(len(standard_input_types))]

    icon_names = [f"static/resources/icon_{standard_input_types[i]}.png" for i in range(len(standard_input_types))]



    template =f"""
   <ul id="menu" class="mfb-component--bl mfb-zoomin" data-mfb-toggle="hover">
      <li class="mfb-component__wrap">
        <a href="#" class="mfb-component__button--main">
           <i class="mfb-component__main-icon--resting"><img src="static/resources/icon_plus.png"  width="20px" style="; margin-top: 18px;"></i>
          <i class="mfb-component__main-icon--active"><img src="static/resources/icon_attest.png"  width="30px" style="margin-right:6px; margin-top: 12px;"></i>
        </a>
        <ul class="mfb-component__list">
          <li>
            <a href="{reference_to_input_file_names[0]}" data-mfb-label="Economic Impact" class="mfb-component__button--child{type_active[0]}">
              <img src="{icon_names[0]}"  width="38px" style="margin-left:10px; margin-top: 14px;">
            </a>
          </li>
          <li>
            <a href="{reference_to_input_file_names[1]}" data-mfb-label="Maintenance Strategy" class="mfb-component__button--child{type_active[1]}">
             <img src="{icon_names[1]}"  width="38px" style="margin-left:8px; margin-top: 8px"></i>
            </a>
          </li>

          <li>
            <a href="{reference_to_input_file_names[2]}" data-mfb-label="Life Assessment" class="mfb-component__button--child{type_active[2]}">
             <img src="{icon_names[2]}"  width="38px" style="margin-left:8px; margin-top: 12px"></i>
            </a>
        </ul>
      </li>
    </ul>
"""
    template_body = template_body.replace("<!--$$$DIMENSION_FILTER_MAIN_HTML$$$-->", f"filter_{assessment_input_type}.html")
    template_body = template_body.replace("<!--$$$DIMENSION_RESTORE_MAIN_HTML$$$-->", f"restore_main_{assessment_input_type}.html")
    fileTemp = fileTemp.replace("</body>",template+template_body)
    fileTemp = fileTemp.replace("<html>", "{% load static %}\n<html>")
    fileTemp = fileTemp.replace("<!--$$$ASSET_TYPE_CLASS$$$-->", asset_types_default[0])

    with open(main_file_path, 'w') as file:
        file.write(fileTemp)

    if not os.path.exists(output_path+"/restore_files/main_" + assessment_input_type + ".html"):
        shutil.copy(main_file_path, output_path+"/restore_files/main_" + assessment_input_type + ".html")


def gap_stat(data, refs=None, nrefs=10, ks=range(2, 11)):
    """
    Compute the Gap statistic for an nxm dataset in data.

    Either give a precomputed set of reference distributions in refs as an (n,m,k) scipy array,
    or state the number k of reference distributions in nrefs for automatic generation with a
    uniformed distribution within the bounding box of data.

    :param data: Input data
    :param refs: Reference distributions with shape ()
    :param nrefs:
    :param ks:
    :return:


        """
    seed = 2
    shape = data.shape
    if refs == None:
        tops = data.max(axis=0)
        bots = data.min(axis=0)
        dists = scipy.matrix(np.diag(tops-bots))
        np.random.seed(seed)

        rands = np.random.random_sample(size=(shape[0], shape[1], nrefs))
        for i in range(nrefs):
            rands[:, :, i] = rands[:, :, i] * dists + bots
    else:
        rands = refs

    gaps = np.zeros((len(ks),))
    for (i, k) in enumerate(ks):
        (kmc, kml) = scipy.cluster.vq.kmeans2(data, k, minit="points")
        seed_alter = seed
        #while len(np.unique(kml)) != k:
        ##while len(np.unique(kml)) != k and seed_alter < 20:
        #    if seed_alter == seed:
        #        print(f"Kmeans with empty clusters. Reinitializing kmeans of size {k}")

        #    seed_alter += 1
        #    np.random.seed(seed_alter)
        #    (kmc, kml) = scipy.cluster.vq.kmeans2(data, k)

        np.random.seed(seed)

        disp = sum([dst(data[m, :], kmc[kml[m], :]) for m in range(shape[0])])

        refdisps = np.zeros((rands.shape[2],))
        for j in range(rands.shape[2]):
            (kmc, kml) = scipy.cluster.vq.kmeans2(rands[:, :, j], k, minit="points")
            refdisps[j] = sum([dst(rands[m, :, j], kmc[kml[m], :]) for m in range(shape[0])])


        gaps[i] = np.log(np.mean(refdisps)) - np.log(disp)

    np.random.seed()
    return gaps

def periods_length (values_vector, mask_vector):
    if np.nansum(mask_vector) != 0:
        cumsum_vector = np.nancumsum(values_vector * mask_vector)
        if np.nansum(np.logical_not(mask_vector)) > 0:
            delta_cumsum_vector = cumsum_vector[np.logical_not(mask_vector)]
            delta_cumsum_vector = np.hstack([delta_cumsum_vector[0], delta_cumsum_vector[1:] - delta_cumsum_vector[:-1]])
            cumsum_vector = deepcopy(values_vector)
            cumsum_vector[np.logical_not(mask_vector)] = -delta_cumsum_vector

        cumsum_vector = np.nancumsum(cumsum_vector)
        return cumsum_vector
    else:
        return values_vector


def optimalK(data, nrefs=5, maxClusters=23, save_results={'save':False,'path':None}):
    """
    Calculates KMeans optimal K using Gap Statistic from Tibshirani, Walther, Hastie
    Params:
        data: ndarry of shape (n_samples, n_features)
        nrefs: number of sample reference datasets to create
        maxClusters: Maximum number of clusters to test for
    Returns: (gaps, optimalK)
    """
    max_elbow_gap_discrepancy = 6
    seed = 2
    np.random.seed(seed)
    if len(np.unique(data,axis=0)) != 1:
        if len(np.unique(data,axis=0)) <= maxClusters:
            maxClstrs = len(np.unique(data,axis=0))
        else:
            maxClstrs = maxClusters

        if maxClstrs > 3:
            model = KElbowVisualizer(KMeans(), k=maxClstrs)
            model.fit(data)

            while model.elbow_value_ == None and maxClstrs < maxClusters:
                maxClstrs += 2
                model = KElbowVisualizer(KMeans(), k=maxClstrs)
                model.fit(data)
            optimum_elbow = model.elbow_value_
            elbow_values = np.array([model.k_values_, model.k_scores_])


        else:
            optimum_elbow = maxClstrs
            elbow_values = np.array([np.arange(np.min([2,maxClstrs]),maxClstrs+1), np.ones(np.max([maxClstrs-1,1]))])

        if optimum_elbow != None:
            k_range = range(2,int(min(maxClstrs+1,optimum_elbow+max_elbow_gap_discrepancy+1)))
        else:
            optimum_elbow = maxClstrs
            k_range = range(2,maxClstrs+1)

        gaps=gap_stat(data, nrefs=nrefs, ks=k_range)

        if len(argrelextrema(gaps, np.greater)[0]) != 0:
            optimum_gap_idx = np.array([np.min(argrelextrema(gaps, np.greater)[0])])
        else:
            optimum_gap_idx = np.array([len(gaps)-1])

        if len(optimum_gap_idx) == 0:
            optimum_gap = None
            extra_info = "Not Found"
        else:
            contrast_k_size = np.array(k_range)[optimum_gap_idx]>=optimum_elbow
            arg_min = np.argmin(optimum_gap_idx) #nearest: np.argmin(np.abs(np.array(k_range)[optimum_gap_idx]-optimum_elbow))  # minimum: np.min(optimum_gap_idx)

            if np.array(k_range)[optimum_gap_idx][arg_min]>=optimum_elbow:
                extra_info = ""
                optimum_gap_idx = optimum_gap_idx[arg_min]
                optimum_gap = k_range[optimum_gap_idx]
            else:
                extra_info = " Below Elbow"
                optimum_gap_idx = optimum_gap_idx[arg_min]
                optimum_gap = k_range[optimum_gap_idx]

        if optimum_elbow != None and optimum_gap != None:
            opt_final = np.min([int(optimum_gap), int(optimum_elbow)]) if np.abs(optimum_gap - optimum_elbow)<=6 or optimum_gap < optimum_elbow else  optimum_elbow
        elif optimum_elbow == None and optimum_gap != None:
            opt_final = optimum_gap
        elif optimum_elbow != None and optimum_gap == None:
            opt_final = optimum_elbow
        else:
            opt_final = np.max((2,int(maxClusters/3)))

        layout = op_layout(opt_final)

        if layout[0] == 1 and opt_final > 4:
            opt_final -= 1

        print(f"Optimum clusters: \n - Elbow:{optimum_elbow}\n - Gap Stat.:{optimum_gap} {extra_info}\n - Final:{opt_final}")

        ##################################### PLOT
        if save_results['save']:
            fig, ax1 = plt.subplots()
            fig.suptitle('Optimum number of clusters', fontsize=20, y=0.95)
            ax1.set_xlabel('k', fontsize = 16)
            ax1.set_ylabel('distortion [Elbow]', color="#034C8C", fontsize = 16)
            ax1.plot(elbow_values[0,:optimum_elbow + max_elbow_gap_discrepancy-1], elbow_values[1, :optimum_elbow + max_elbow_gap_discrepancy-1], marker="D", color="#034C8C")
            ax1.scatter(optimum_elbow,elbow_values[1,optimum_elbow-2],marker="X",s=[200], color="#730707", zorder=9, edgecolors="#FFC5A6", linewidths=2)

            ax2 = ax1.twinx()
            ax2.set_ylabel('Gap Statistic (k)', color="#38024D", fontsize = 16, labelpad = 15)
            #if through_decreasing_trend:
            #	ax2.plot(optimum_gap_trend_idxs+1, gaps[:optimum_elbow + max_elbow_gap_discrepancy][optimum_gap_trend_idxs], marker="s", color="#F27E63", markersize=10)

            ax2.plot(k_range, gaps, marker="s", color="#38024D")
            ax2.scatter(optimum_gap,gaps[optimum_gap_idx],marker="X",s=[200], color="#730707", zorder=9, edgecolors="#FFC5A6", linewidths=2)

            ax1.grid(b=None)
            ax2.grid(b=None)
            ax1.xaxis.grid()

            newax = fig.add_axes([0.02, 0.8, 0.2, 0.2], anchor='NW', zorder=-1)
            newax.imshow(Image.open("./static/resources/logo.png"))
            newax.axis('off')

            try:
                fig.savefig(save_results['path']+ "number_clusters.pdf")
            except:
                print("The results of the process to determine the optimal number of clusters could not be saved")
    else:
        if save_results['save']:
            fig, ax1 = plt.subplots()
            fig.suptitle('Optimum number of clusters', fontsize=20, y=0.95)
            ax1.set_xlabel('k', fontsize=16)
            ax1.set_ylabel('distortion [Elbow]', color="#034C8C", fontsize=16)
            ax1.plot([1],[0], marker="D", color="#034C8C")
            ax1.scatter([1],[0], marker="X", s=[200], color="#730707", zorder=9,
                        edgecolors="#FFC5A6", linewidths=2)

            ax2 = ax1.twinx()
            ax2.set_ylabel('Gap Statistic (k)', color="#38024D", fontsize=16, labelpad=15)
            # if through_decreasing_trend:
            #	ax2.plot(optimum_gap_trend_idxs+1, gaps[:optimum_elbow + max_elbow_gap_discrepancy][optimum_gap_trend_idxs], marker="s", color="#F27E63", markersize=10)

            ax2.plot([1],[0], marker="s", color="#38024D")
            ax2.scatter([1],[0], marker="X", s=[200], color="#730707", zorder=9,
                        edgecolors="#FFC5A6", linewidths=2)

            ax1.grid(b=None)
            ax2.grid(b=None)
            ax1.xaxis.grid()

            newax = fig.add_axes([0.02, 0.8, 0.2, 0.2], anchor='NW', zorder=-1)
            newax.imshow(Image.open("./static/resources/logo.png"))
            newax.axis('off')
        opt_final = 1

    return opt_final

def prime_factors(k):
    primfac = []
    d = 2
    while d * d <= k:
        while (k % d) == 0:
            primfac.append(d)  # supposing you want multiple factors repeated
            k //= d
        d += 1
    if k > 1:
        primfac.append(k)

    primfac = primfac[::-1]  # Sort in descending values
    return primfac


def op_layout(k):
    if k > 1:
        primfac = prime_factors(k)

        dim_2 = primfac[0] if len(primfac) > 0 else primfac
        dim_1 = 1
        if len(primfac) >= 2 and k>=4:
            dim_1 = primfac[1]
            for i in range(len(primfac)-2):
                if dim_1 < dim_2:
                    dim_1 = dim_1 * primfac[i+2]
                else:
                    dim_2 = dim_2 * primfac[i+2]
        elif len(primfac) == 1 and k == 3:
            dim_1 = 1
            dim_2 = 3
        elif len(primfac) == 1 and k == 2:
            dim_1 = 1
            dim_2 = 2
        else:
            dim_2 = k
    else:
        dim_1 = 1
        dim_2 = 1

    return int(min(dim_1,dim_2)),int(max(dim_1, dim_2))

# ==================================================================
def compute_map(file_path,file_vars, asset_types_default, output_path,  assessment_type = False, classifier_var = False, tag_var = "name", best_of = 1, saving_configuration = {"assessment": True, "clustering": False,
						"training": False}, load_stored_map = False):
    if not load_stored_map:
        if len(file_path)>1:
            csv_header_1 = pd.read_csv(file_path[0], sep=";", index_col=0, nrows=0)
            csv_header_2 = pd.read_csv(file_path[0], index_col=0, nrows=0)
            data_file = pd.read_csv(file_path[0], sep=";") if csv_header_1.columns.__len__() >= csv_header_2.columns.__len__() else pd.read_csv(file_path[0])

            for i in range(1, len(file_path)):
                csv_header_1 = pd.read_csv(file_path[i], sep=";",  index_col=0, nrows=0)
                csv_header_2 = pd.read_csv(file_path[i], index_col=0, nrows=0)
                data_file_info_aux = pd.read_csv(file_path[i], sep=";") if csv_header_1.columns.__len__() >= csv_header_2.columns.__len__() else pd.read_csv(file_path[i])

                if classifier_var == tag_var[1]:
                    classifier_var =  tag_var[0]

                data_file_info_aux.rename(columns={tag_var[1]: tag_var[0]}, inplace=True)
                auxiliary_vars = list(data_file_info_aux.columns.difference(data_file.columns))+[tag_var[0]]

                data_file = data_file.merge(data_file_info_aux[auxiliary_vars],  on=tag_var[0], how='outer')
                auxiliary_vars.remove(tag_var[0])

        else:
            auxiliary_vars = None
            csv_header_1 = pd.read_csv(file_path[0], sep=";", index_col=0, nrows=0)
            csv_header_2 = pd.read_csv(file_path[0], index_col=0, nrows=0)
            data_file = pd.read_csv(file_path[0], sep=";") if csv_header_1.columns.__len__() >= csv_header_2.columns.__len__() else pd.read_csv(file_path[0])

        filter_input_template_path = "./static/resources/template_filter.html"
        filter_output_template_path = "./static/results_condition_characterization/filter_"+assessment_type+".html"
        filter_categorical_files_path = "./static/results_condition_characterization/filter_files/"

        try:
            os.mkdir(filter_categorical_files_path)
        except:
            pass

        file_name = output_path + 'store_vars/' + assessment_type + '_chart_vars.json'
        if not os.path.exists(os.path.dirname(file_name)):
            try:
                os.makedirs(os.path.dirname(file_name))
            except OSError as exc:  # Guard against race condition
                print(exc)

        filter_files_output_path = output_path + 'filter_files/'
        if not os.path.exists(os.path.dirname(filter_files_output_path)):
            try:
                os.makedirs(os.path.dirname(filter_files_output_path))
            except OSError as exc:  # Guard against race condition
                print(exc)

        compute_filter_page(data_file, filter_input_template_path, filter_output_template_path,
                            filter_categorical_files_path, assessment_type)

        data_x = np.array(data_file[file_vars])
        data_x_no_norm = data_x
        min_data_x = data_x_no_norm.min(axis=0)
        min_data_x[min_data_x==data_x_no_norm.max(axis=0)] = 0
        divider =(data_x_no_norm.max(axis=0)-min_data_x)
        divider[divider==0] = 1
        data_x = (data_x-min_data_x) / (data_x_no_norm.max(axis=0)-min_data_x)

        data_y = np.array(data_file[file_vars])

        asset_type_list = np.array([asset_types_default[0]] * len(data_x)) if classifier_var == False else np.array(data_file[classifier_var])

        if np.issubdtype(asset_type_list.dtype, np.number):
            min_value = asset_type_list.min()
            max_value = asset_type_list.max()
            q1_value = np.quantile(asset_type_list,0.25)
            mean_value = np.quantile(asset_type_list,0.5)
            q3_value = np.quantile(asset_type_list,0.75)
            array_unique_values = np.unique([min_value,q1_value,mean_value,q3_value,max_value])
            new_array_unique_values = np.array([None] * len(asset_type_list), dtype = np.object)
            if len(array_unique_values) > 1:
                for i in range(len(array_unique_values)-2):
                    for ii in range(1,5): #Round numbers
                        number_1 = np.around(array_unique_values[i],ii)
                        number_2 = np.around(array_unique_values[i+1], ii)
                        if number_1 != number_2:
                            number_1 = np.abs(np.around(array_unique_values[i]-5.0/(10**(ii+2)), ii+1))*np.sign(array_unique_values[i])
                            number_2 = np.abs(np.around(array_unique_values[i + 1]+5.0/(10**(ii+2)), ii+1))*np.sign(array_unique_values[i+1])
                            break
                    if i==0:
                        new_array_unique_values[np.logical_and(asset_type_list >= array_unique_values[i] , asset_type_list <= array_unique_values[i+1])] = f"{classifier_var}: [{number_1} ; {number_2}]"
                    else:
                        new_array_unique_values[np.logical_and(asset_type_list > array_unique_values[i] , asset_type_list <= array_unique_values[i+1])] = f"{classifier_var}: [{number_1} ; {number_2}]"


                for ii in range(1, 5):
                    number_1 = np.around(array_unique_values[len(array_unique_values) - 2],ii)
                    number_2 = np.around(array_unique_values[len(array_unique_values) - 1],ii)
                    if number_1 != number_2:
                        number_1 = np.abs(np.around(array_unique_values[len(array_unique_values) - 2]-5.0/(10**(ii+2)),ii+1))*np.sign(len(array_unique_values) - 2)
                        number_2 = np.abs(np.around(array_unique_values[len(array_unique_values) - 1]+5.0/(10**(ii+2)),ii+1))*np.sign(len(array_unique_values) - 1)
                        break

                new_array_unique_values[np.logical_and(asset_type_list >= array_unique_values[len(array_unique_values)-2] , asset_type_list <= array_unique_values[len(array_unique_values)-1])] = f"{classifier_var}: [{number_1};{number_2}]"
                asset_type_list = new_array_unique_values

        if classifier_var:
            classifier_var = classifier_var+"_filter"

            data_file[classifier_var] = asset_type_list

        k = optimalK(data_x, nrefs=10, save_results = {'save': saving_configuration["clustering"],'path':output_path+"clustering_graphs/"+assessment_type+"_"} )
        Rows, Cols = op_layout(k)
        # np.random.seed(1)
        LearnMax = .05
        StepsMax = 30000


        som = MiniSom.MiniSom(Rows, Cols, data_x.shape[1], sigma=0.35, learning_rate=LearnMax, neighborhood_function='gaussian')
        som.train_batch(data_x, StepsMax, verbose=True)

        if saving_configuration["training"]:
            fig, ax1 = plt.subplots()
            plt.plot(som.iteration_error[0][1:],som.iteration_error[1][1:])
            newax = fig.add_axes([0.02, 0.8, 0.2, 0.2], anchor='NW', zorder=-1)
            newax.imshow(Image.open("./static/resources/logo.png"))
            newax.axis('off')
            ax1.set_xlabel('Epoch', fontsize=16)
            ax1.set_ylabel('Dispersion value', color="#034C8C", fontsize=16)
            ax1.set_title('Clustering Training process\n'+assessment_type.replace("_", " "), fontsize=24)
            try:
                fig.savefig(output_path+"clustering_graphs/"+assessment_type+"_clustering_process.pdf")
            except:
                print("The results of the clustering process could not be saved")

        if Rows * Cols == len(np.unique(data_x,axis=0)):
            som._weights = np.reshape(np.unique(data_x, axis=0),som._weights.shape)

        centroids = som.get_weights()
        mapping = np.array([som.winner(x) for x in data_x]).T

        failed_iterations = 0

        while(Rows*Cols != np.unique(mapping,axis=1).shape[1]):
            failed_iterations += 1
            if Rows*Cols > 2 and failed_iterations >= 2:
                failed_iterations = 0
                k = k - 1
                Rows, Cols = op_layout(k)
                while ((Rows == 1) and (Rows*Cols > 4)):
                    k = k - 1
                    Rows, Cols = op_layout(k)

                print(f"Number of optimal Patterns reduced to {Rows*Cols}")

            som = MiniSom.MiniSom(Rows, Cols, data_x.shape[1], sigma=0.35, learning_rate=LearnMax,
                                  neighborhood_function='gaussian')
            som.train_batch(data_x, StepsMax, verbose=True)
            mapping = np.array([som.winner(x) for x in data_x]).T

        ## Best of
        list_som = np.array([[None,None]]*best_of, dtype=np.object)

        list_som[0][0] = som.quantization_error(data_x)
        list_som[0][1] = som

        for i in range(best_of-1):
            print(f"Computing best of {best_of}: {i+2}")
            som = MiniSom.MiniSom(Rows, Cols, data_x.shape[1], sigma=0.35, learning_rate=LearnMax,
                            neighborhood_function='gaussian')
            som.train_batch(data_x, StepsMax, verbose=True)
            list_som[i+1][0] = som.quantization_error(data_x)
            list_som[i+1][1] = som

        som = list_som[np.argmin(list_som[:, 0], axis=0)][1]
        centroids = som.get_weights()
        centroids = (centroids) * (data_x_no_norm.max(axis=0)-min_data_x) + min_data_x
        mapping = np.array([som.winner(x) for x in data_x]).T

        quantiles = np.zeros([Rows, Cols, 5, len(file_vars)])
        ## Compute quartiles
        for row in range(Rows):
            for col in range(Cols):
                quantiles[row][col][0] = np.quantile(data_x[np.logical_and(mapping[0] == row ,mapping[1] == col)], 0, axis=0)
                quantiles[row][col][1] = np.quantile(data_x[np.logical_and(mapping[0] == row ,mapping[1] == col)], 0.25, axis=0)
                quantiles[row][col][2] = np.quantile(data_x[np.logical_and(mapping[0] == row ,mapping[1] == col)], 0.5, axis=0)
                quantiles[row][col][3] = np.quantile(data_x[np.logical_and(mapping[0] == row ,mapping[1] == col)], 0.75, axis=0)
                quantiles[row][col][4] = np.quantile(data_x[np.logical_and(mapping[0] == row ,mapping[1] == col)], 1.0, axis=0)

        data_x_no_norm_dict = {}
        for column in list(data_file.columns)+auxiliary_vars if auxiliary_vars != None else list(data_file.columns):
            data_x_no_norm_dict[column] = np.ndarray.tolist(np.array(data_file[column]))



        var_list = {"data_x_no_norm": data_x_no_norm_dict,
                    "mapping": np.ndarray.tolist(mapping),
                    "centroids": np.ndarray.tolist(centroids),
                    "Rows": Rows,
                    "Cols": Cols,
                    "file_vars": file_vars,
                    "asset_type_list": np.ndarray.tolist(asset_type_list),
                    "assessment_type": assessment_type,
                    "classifier_var": classifier_var,
                    "auxiliary_vars": auxiliary_vars,
                    "tag_var_0": tag_var[0],
                    "asset_type_default": asset_types_default}


        with open(file_name, "w") as fp:
            json.dump(var_list,fp)


        data_x_no_norm_array = np.zeros([var_list["data_x_no_norm"][file_vars[0]].__len__(),file_vars.__len__()], dtype=np.float)
        for i, column in enumerate(file_vars) :
            data_x_no_norm_array[:,i] = var_list["data_x_no_norm"][column]

        var_list["data_x_no_norm"] = data_x_no_norm_array
        var_list["mapping"] = np.array(var_list["mapping"])
        var_list["centroids"] = np.array(var_list["centroids"])
        var_list["asset_type_list"] = np.array(var_list["asset_type_list"])

    else:

        file_name = output_path + 'store_vars/' + assessment_type + '_chart_vars.json'
        with open(file_name) as fp:
            var_list = json.load(fp)

        data_x_no_norm_array = np.zeros([var_list["data_x_no_norm"][file_vars[0]].__len__(),file_vars.__len__()], dtype=np.float)
        for i, column in enumerate(file_vars) :
            data_x_no_norm_array[:,i] = var_list["data_x_no_norm"][column]

        var_list["data_x_no_norm"] = data_x_no_norm_array
        var_list["mapping"] = np.array(var_list["mapping"])
        var_list["centroids"] = np.array(var_list["centroids"])
        var_list["asset_type_list"] = np.array(var_list["asset_type_list"])

    fig = create_box_chart(var_list['data_x_no_norm'], var_list['mapping'], var_list['centroids'], var_list['Rows'], var_list['Cols'],
                           var_list['file_vars'], var_list['asset_type_list'], var_list['assessment_type'], var_list["asset_type_default"])

    template_path = './static/resources/template_table.html'

    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print("Directory ", output_path, " Created ")

    if classifier_var == False:
        data_file["asset_classifier"] = asset_type_list
        classifier_var = "asset_classifier"

    for row in range(Rows):
        for col in range(Cols):
            title = f"ASSETS in PATTERN {row * Cols + col + 1}"
            build_table_html(data_file[np.logical_and(mapping[0] == row, mapping[1] == col)],
                             [classifier_var] + [tag_var[0]] + file_vars + var_list["auxiliary_vars"] if var_list["auxiliary_vars"] != None else [classifier_var] + [tag_var[0]] + file_vars,
                             title, template_path, output_path + f"{assessment_type}_n{row * Cols + col+1}.html", assessment_type)

            if not os.path.exists(output_path + "restore_files/" + f"{assessment_type}_n{row * Cols + col+1}.html"):
                shutil.copy(output_path + f"{assessment_type}_n{row * Cols + col+1}.html",
                            output_path + "restore_files/" + f"{assessment_type}_n{row * Cols + col+1}.html")

    return fig


def compute_map_preloaded(output_path, var_list):

    Rows = var_list["Rows"]
    Cols = var_list["Cols"]
    mapping = np.array(var_list["mapping"])
    assessment_type = var_list["assessment_type"]
    asset_type_list = var_list["asset_type_list"]
    file_vars = var_list["file_vars"]
    data_file = pd.DataFrame.from_dict(var_list["data_x_no_norm"])
    classifier_var = var_list["classifier_var"]
    tag_var_0 = var_list["tag_var_0"]

    data_file[classifier_var] = var_list["asset_type_list"]

    data_x_no_norm_array = np.zeros([var_list["data_x_no_norm"][file_vars[0]].__len__(), file_vars.__len__()],
                                    dtype=np.float)

    for i, column in enumerate(file_vars):
        data_x_no_norm_array[:, i] = var_list["data_x_no_norm"][column]

    var_list["data_x_no_norm"] = data_x_no_norm_array
    var_list["mapping"] = np.array(var_list["mapping"])
    var_list["centroids"] = np.array(var_list["centroids"])
    var_list["asset_type_list"] = np.array(var_list["asset_type_list"])


    fig = create_box_chart(data_x_no_norm_array, var_list['mapping'], var_list['centroids'], var_list['Rows'],
                           var_list['Cols'], var_list['file_vars'], var_list['asset_type_list'], var_list['assessment_type'], var_list["asset_type_default"])

    template_path = './static/resources/template_table.html'

    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print("Directory ", output_path, " Created ")

    if classifier_var == False:
        data_file["asset_classifier"] = asset_type_list
        classifier_var = "asset_classifier"


    for row in range(Rows):
        for col in range(Cols):
            title = f"ASSETS in PATTERN {row * Cols + col + 1}"
            build_table_html(data_file[np.logical_and(mapping[0] == row, mapping[1] == col)],
                             [classifier_var] + [tag_var_0] + file_vars + var_list["auxiliary_vars"] if var_list["auxiliary_vars"] != None else [classifier_var] + [tag_var_0] + file_vars,
                             title, template_path, output_path + f"{assessment_type}_n{row * Cols + col+1}.html", assessment_type)

            if not os.path.exists(output_path + "restore_files/" + f"{assessment_type}_n{row * Cols + col+1}.html"):
                shutil.copy(output_path + f"{assessment_type}_n{row * Cols + col+1}.html",
                            output_path + "restore_files/" + f"{assessment_type}_n{row * Cols + col+1}.html")

    return fig

def compute_filter_page(dataset, template_path, template_output_path, filter_categorical_files_path, assessment_type):
    var_list_isnum = [np.issubdtype(type, np.number) for type in dataset.dtypes]
    var_list = [f"var_{i}" if is_num else f"catvar_{i}" for i, is_num in enumerate(var_list_isnum)]

    numerical_var_list = ""
    categorical_var_list = ""
    for i, is_num in enumerate(var_list_isnum):
        if is_num:
            ## Write numerical header
            if numerical_var_list == "":
                numerical_var_list += """
    <table class="scroll" id="table_numerical" >
    <thead>
    <tr>
    <th scope="col" colspan="1" style="width:200px">Variable name</th>
    <th scope="col" style="width:80px">Enable Filter</th>
    <th scope="col" style="width:70px">Filter mode</th>
    <th scope="col" style="width:410px">Filter value</th>
    </tr>
    </thead>
    <tbody>
    """
            numerical_var_list += template_var_numrical(i, dataset)
        else:
            # Write categorical header
            if categorical_var_list == "":
                categorical_var_list += """
    <table class="scroll" id="table_categorical" >
    <thead>
    <tr>
    <th scope="col" colspan="1" style="width:200px">Variable name</th>
    <th scope="col" style="width:80px">Enable Filter</th>
    <th scope="col" style="width:560px">Filter</th>
    </tr>
    </thead>
    <tbody>
    """
            categorical_var_list += template_var_categorical(i, dataset, filter_categorical_files_path+"filter_"+assessment_type+"_")

    if numerical_var_list != "":
        numerical_var_list += "</tbody></table>"

    if categorical_var_list != "":
        categorical_var_list += "</tbody></table>"

    tag_categorical = "<!--$$$FILTER_CATEGORICAL$$$-->"
    tag_numerical = "<!--$$$FILTER_NUMERICAL$$$-->"
    tag_title = "<!--$$$FILTER_DIMENSION_TYPE$$$-->"
    tag_assessment_type_var = "<!--$$$ASSESSMENT_TYPE_CODE$$$-->"
    tag_main_file = "<!--$$$MAIN_FILE_TITLE$$$-->"

    fileTemp = open(template_path, 'r').read().replace(tag_numerical, numerical_var_list)
    fileTemp = fileTemp.replace(tag_categorical, categorical_var_list)
    fileTemp = fileTemp.replace(tag_assessment_type_var, f"<script> var assessment_type =\"{assessment_type}\" </script>")

    types_standard = {"economic_impact": 'Economic Impact', "maintenance_strategy": 'Maintenance Strategy',
                          "life_assessment": 'Life Assessment'}  ## NOT MODIF

    fileTemp = fileTemp.replace(tag_title, types_standard[assessment_type])
    fileTemp = fileTemp.replace(tag_main_file, "main_"+assessment_type+".html")


    with open(template_output_path, 'w') as file:
        file.write(fileTemp)



def template_var_numrical(index, dataset):
    var_text = f"""
<tr id="var_{index}">
<td id="text_var_{index}" style="text-align: right">{dataset.columns[index]}</td>
<td><label class="checkbox bounce">
	        <input type="checkbox" id="check_var_{index}">
	        <svg viewBox="0 0 21 21">
	            <polyline points="5 10.75 8.5 14.25 16 6"></polyline>
	        </svg>
	    </label>
	</td>
<td><select data-menu id="select_var_{index}"></select></td>
<td id="input_select_var_{index}" style="text-align:left"></td>
</tr>
"""

    return var_text

def template_var_categorical(index, dataset, output_path):
    var_text = f"""
<tr id="var_{index}">
<td id="text_var_{index}" style="text-align: right">{dataset.columns[index]}</td>
<td><label class="checkbox bounce">
	        <input type="checkbox" id="check_var_{index}">
	        <svg viewBox="0 0 21 21">
	            <polyline points="5 10.75 8.5 14.25 16 6"></polyline>
	        </svg>
	    </label>
	</td>
<td><body class="ej2-new">
 <div class="control-wrapper">
        <input type="text" id="catvar_{index}">
    </div>
</td>
</tr>
"""

    dataset[dataset.columns[index]].drop_duplicates().to_json(output_path+f"catvar_{index}.json", orient="values")
    return var_text