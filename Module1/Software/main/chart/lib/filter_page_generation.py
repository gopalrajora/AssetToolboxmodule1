import pandas as pd
import numpy as np

dataset = pd.read_csv("Spain_LA_supports.csv")
template_path = "filter_template.html"
output_path = "main.html"

size = {0: "Small", 1: "Medium", 2: "Large"}
insulator = {0: "Plastic", 1: "Oil", 2: "Porcelain", 3: "Mica", 4: "Ebonite", 5: "Mixed"}
location = {0: "Urban", 1: "Rural", 2: "Meadow", 3: "Farmland", 4: "Wood"}

size_random = np.random.randint(0,3,dataset.__len__())
insulator_random = np.random.randint(0,6,dataset.__len__())
location_random = np.random.randint(0,5,dataset.__len__())

dataset["size"] = [size[i] for i in size_random]
dataset["insulator"] = [insulator[i] for i in insulator_random]
dataset["location"] = [location[i] for i in location_random]

var_list_isnum = [np.issubdtype(type, np.number) for type in dataset.dtypes]

var_list = [f"var_{i}" if is_num else f"catvar_{i}" for i,is_num in enumerate(var_list_isnum)]

def template_var_numrical(index):
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

def template_var_categorical(index):
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
    dataset[dataset.columns[index]].drop_duplicates().to_json(f"catvar_{index}.json", orient="values")
    return var_text

numerical_var_list = ""
categorical_var_list = ""
for i, is_num in enumerate(var_list_isnum):
    if is_num:
        ## Write numerical header
        if numerical_var_list == "":
            numerical_var_list  += """
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
        numerical_var_list += template_var_numrical(i)
    else:
        #Write categorical header
        if categorical_var_list == "":
            categorical_var_list +="""
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
        categorical_var_list += template_var_categorical(i)

if numerical_var_list != "":
    numerical_var_list +="</tbody></table>"

if categorical_var_list != "":
    categorical_var_list +="</tbody></table>"

tag_categorical = "<!--$$$FILTER_CATEGORICAL$$$-->"
tag_numerical = "<!--$$$FILTER_NUMERICAL$$$-->"

fileTemp = open(template_path, 'r').read().replace(tag_numerical, numerical_var_list)
fileTemp = fileTemp.replace(tag_categorical, categorical_var_list)

with open(output_path, 'w') as file:
    file.write(fileTemp)
