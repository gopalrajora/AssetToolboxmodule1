
document.getElementById('download_filter').addEventListener('click', function(){get_filter_conf(true)});
document.getElementById('apply_filter').addEventListener('click', function(){apply_filter("filter_value")});
document.getElementById('reset_filter').addEventListener('click', function(){reset()});

document.getElementById('load_filter').onclick = function() {
document.getElementById("file-input").value = null;  
document.getElementById('file-input').click();
  $(function(){
    $("#file-input").change(function(e){
        files = document.getElementById('file-input').files
        console.log(files);
        var fr = new FileReader();
        fr.onload = function(e) { 
            console.log(e);
            var result = JSON.parse(e.target.result);
            length_numerical = document.getElementById("table_numerical").rows.length-1;
            length_categorical = document.getElementById("table_categorical").rows.length-1;

            var var_numerical = Array.from(document.getElementById("table_numerical").rows).map(element => element.id).slice(1,);
            var var_categorical = Array.from(document.getElementById("table_categorical").rows).map(element => element.id).slice(1,);

            /// Check if var in existing list

            if (result.mode == "include") {
                $("#check_include")[0].checked = true
                $("#check_exclude")[0].checked = false
            } else {
                $("#check_include")[0].checked = false
                $("#check_exclude")[0].checked = true
            }

            for (i = 0; i < result.numerical.length; i++) {
                for (ii = 0; ii < length_numerical; ii++) {
                    if (result.numerical[i].name == $("#text_"+var_numerical[ii])[0].innerText) {
                        result.numerical[i].var = var_numerical[ii];
                    }

                }
            }

            for (i = 0; i < result.categorical.length; i++) {
                for (ii = 0; ii < length_categorical; ii++) {
                    if (result.categorical[i].name == $("#text_"+var_categorical[ii])[0].innerText) {
                        result.categorical[i].var = var_categorical[ii];
                    }

                }
            }

            /// Load Configuration

            for (i = 0; i < result.numerical.length; i++) {
                if (result.numerical[i].var !== undefined) {
                    load_check_status(result.numerical[i].var,"checked");
                    load_option_numerical(result.numerical[i].var,result.numerical[i].mode);
                    load_value_numerical(result.numerical[i].var,result.numerical[i].mode, result.numerical[i].value);
                }
            }

            for (i = 0; i < result.categorical.length; i++) {
                if (result.categorical[i].var !== undefined) {
                    load_check_status(result.categorical[i].var,"checked");
                    load_option_categorical(result.categorical[i].var, result.categorical[i].value);
                }
            }
              
        }
        fr.readAsText(files.item(0));});
        

        });
};


function apply_filter(hidden_input_id){
    var filter_value;
    filter_value = get_filter_conf(false);
    $("#"+hidden_input_id)[0].value = filter_value
}

function include_exclude_binary(){
      
    if( event.srcElement.id == "check_include" && $("#"+event.srcElement.id)[0].checked) {
    	$("#check_exclude")[0].checked = false
    }
	

    if (event.srcElement.id == "check_include" && ! $("#"+event.srcElement.id)[0].checked) {
    	$("#check_exclude")[0].checked = true
    }
	
    if (event.srcElement.id == "check_exclude" && ! $("#"+event.srcElement.id)[0].checked) {
    	$("#check_include")[0].checked = true
    }

    if (event.srcElement.id == "check_exclude" && $("#"+event.srcElement.id)[0].checked) {
    	$("#check_include")[0].checked = false
    }
}


function reset(){
     var var_numerical = Array.from(document.getElementById("table_numerical").rows).map(element => element.id).slice(1,);
     var_numerical.forEach(num_var => load_check_status(num_var, false))
     var_numerical.forEach(num_var => load_option_numerical(num_var, "none"))

     var var_categorical = Array.from(document.getElementById("table_categorical").rows).map(element => element.id).slice(1,);
     var_categorical.forEach(cat_var => load_check_status(cat_var, false))
     var_categorical.forEach(cat_var => load_option_categorical(cat_var, ""))
}

function get_filter_conf(download){
	var active_numerical = []
    var varnames_numerical = []
    var option_numerical = []
    var value_numerical = []
    var var_numerical = Array.from(document.getElementById("table_numerical").rows).map(element => element.id).slice(1,);
    var_numerical.forEach(active => get_check_status(active, active_numerical))
    var_numerical.forEach(active => get_var_name(active, varnames_numerical))
    var_numerical.forEach(active => get_option_numerical(active, option_numerical))
    var_numerical.forEach(active => get_value_numerical(active, value_numerical))


    var active_categorical = []
    var option_categorical = []
    var varnames_categorical = []
	var var_categorical = Array.from(document.getElementById("table_categorical").rows).map(element => element.id).slice(1,);
    var_categorical.forEach(active => get_check_status(active, active_categorical))
    var_categorical.forEach(active => get_var_name(active, varnames_categorical))
    var_categorical.forEach(active => get_option_categorical(active, option_categorical))

    // Save in Json
    var i;
    var filter_configuration = [];
    var numerical_json = [];
    for (i = 0; i < active_numerical.length; i++) {
      numerical_json.push({"name": varnames_numerical[i], "mode": option_numerical[i], "value": value_numerical[i]})
    }

    var categorical_json = [];
    for (i = 0; i < active_categorical.length; i++) {
      categorical_json.push({"name":varnames_categorical[i], "value": option_categorical[i]});
    }

    var mode

    if ($("#check_include")[0].checked){
        mode = "include"
    } else {
        mode = "exclude"
    }

    filter_configuration = {"mode": mode ,"numerical":numerical_json , "categorical":categorical_json, "assessment_type": assessment_type }
    

    var filter_json_value = JSON.stringify(filter_configuration)

    if (download) {
        var hiddenElement = document.createElement('a');
        hiddenElement.href = 'data:attachment/text,' + encodeURI(filter_json_value);
        hiddenElement.target = '_blank';
        hiddenElement.download = 'filter_configuration.json';
        hiddenElement.click();
    }

    return filter_json_value

}



function load_conf(active_numerical,varnames_numerical,option_numerical,value_numerical,active_categorical,option_categorical,varnames_categorical){
    var i
    for (i = 0; i < active_numerical.length; i++) {
      load_check_status(active_numerical[i],"checked")
      load_option_numerical(active_numerical[i],option_numerical[i])
      load_value_numerical(active_numerical[i],option_numerical[i], value_numerical[i])
    }

    for (i = 0; i < active_categorical.length; i++) {
      load_check_status(active_categorical[i],"checked")
      load_option_categorical(active_categorical[i],option_categorical[i])
    }    
    
}


function load_check_status(id_text, var_active){
    $("#check_"+id_text)[0].checked = var_active
}

function load_option_numerical(id_text, var_option){  
    menu = $("#select_"+id_text).parent()
    select = $("#select_"+id_text+" [value='"+var_option+"']")
    selected = $("#select_"+id_text+" [selected='selected']")
    index = select.index()

    $("#select_"+id_text)[0].options.selectedIndex = index

    menu.css("z-index", 1);
    menu.css('--t', index * -41 + 'px');
    selected.attr('selected', false);
    select.find('option').eq(index).attr('selected', true);

    menu.addClass(index > selected.index() ? 'tilt-down' : 'tilt-up');
    
    menu.removeClass('open tilt-up tilt-down');
    menu.css("z-index", 0);
    option_loaded = var_option;
    //checkbox_active = $("#check_"+menu[0].childNodes[0].id)[0].checked;
    value_prev_condition = $("#value1_"+menu[0].childNodes[0].id).length > 0;
    keep_value = "";
    if (value_prev_condition) {
        keep_value = $("#value1_"+menu[0].childNodes[0].id)[0].value;
    }

    if (option_loaded == "btw"){
        $("#input_"+menu[0].childNodes[0].id)[0].innerHTML="<td style=\"text-align:center; margin:auto\"><input type='text' id=\""+"value1_"+menu[0].childNodes[0].id+"\"><input type='text' id=\""+"value2_"+menu[0].childNodes[0].id+"\"></td>";
    } else if (option_loaded == "none") {
        $("#input_"+menu[0].childNodes[0].id)[0].innerHTML="";
    } else { 
        $("#input_"+menu[0].childNodes[0].id)[0].innerHTML="<td style=\"text-align:center; margin:auto\"><input type='text' id=\""+"value1_"+menu[0].childNodes[0].id+"\"></td>";
    }

    if (value_prev_condition && option_loaded !== "none") {
        $("#value1_"+menu[0].childNodes[0].id)[0].value = keep_value;
    }

}

function load_value_numerical(id_text, var_option, value_numerical){
    if (var_option == "btw") {
        $("#value1_select_"+id_text)[0].value = value_numerical[0];
        $("#value2_select_"+id_text)[0].value = value_numerical[1];
    } else if (var_option == "none") {
    } else {
        $("#value1_select_"+id_text)[0].value = value_numerical[0];
    }
}

function load_option_categorical(id_text, var_option){
    $("#cat"+id_text)[0].ej2_instances[0].value = var_option
}

    

function get_var_name(id_text, var_active){
    if ($("#check_"+id_text)[0].checked) {
        var_active.push($("#text_"+id_text)[0].innerHTML);
    } 
}


function get_check_status(id_text, var_active){
    if ($("#check_"+id_text)[0].checked) {
        var_active.push(id_text);
    } 
}

function get_option_numerical(id_text, var_option){
    if ($("#check_"+id_text)[0].checked) {
        var_option.push($("#select_"+id_text)[0].options[$("#select_"+id_text)[0].options.selectedIndex].value);
    } 
}

function get_value_numerical(id_text, var_value){
    if ($("#check_"+id_text)[0].checked) {
        if ($("#select_"+id_text)[0].options[$("#select_"+id_text)[0].options.selectedIndex].value == "btw"){
            var_value.push([$("#value1_select_"+id_text)[0].value,$("#value2_select_"+id_text)[0].value]);
        } else if ($("#select_"+id_text)[0].options[$("#select_"+id_text)[0].options.selectedIndex].value == "none"){
            var_value.push([""])
        } else {
            var_value.push([$("#value1_select_"+id_text)[0].value])
        }
    } 
}

function get_option_categorical(id_text, var_categorical){
    if ($("#check_"+id_text)[0].checked) {
        var_categorical.push(Array.from($("#cat"+id_text)[0].parentElement.parentElement.getElementsByTagName("select")[0].options).map(element => element.value));
    } 
}



var xhr = new XMLHttpRequest();
xhr.open('HEAD', "/static/results_condition_characterization/store_vars/"+assessment_type+"_loaded_filter_conf.json", false);
xhr.send();

if(!(xhr.status == "404")){
    var rawFile = new XMLHttpRequest();
    rawFile.open("GET", "/static/results_condition_characterization/store_vars/"+assessment_type+"_loaded_filter_conf.json", false);
    rawFile.onreadystatechange = function ()
    {
        if(rawFile.readyState === 4)
        {
            if(rawFile.status === 200 || rawFile.status == 0)
            {
                 allText = rawFile.responseText;
                
            }
        }
    }
    rawFile.send(null);

    var result = JSON.parse(JSON.parse(allText));
    length_numerical = document.getElementById("table_numerical").rows.length-1;
    length_categorical = document.getElementById("table_categorical").rows.length-1;

    var var_numerical = Array.from(document.getElementById("table_numerical").rows).map(element => element.id).slice(1,);
    var var_categorical = Array.from(document.getElementById("table_categorical").rows).map(element => element.id).slice(1,);

    /// Check if var in existing list

    if (result.mode == "include") {
        $("#check_include")[0].checked = true
        $("#check_exclude")[0].checked = false
    } else {
        $("#check_include")[0].checked = false
        $("#check_exclude")[0].checked = true
    }

    for (i = 0; i < result.numerical.length; i++) {
        for (ii = 0; ii < length_numerical; ii++) {
            if (result.numerical[i].name == $("#text_"+var_numerical[ii])[0].innerText) {
                result.numerical[i].var = var_numerical[ii];
            }

        }
    }

    for (i = 0; i < result.categorical.length; i++) {
        for (ii = 0; ii < length_categorical; ii++) {
            if (result.categorical[i].name == $("#text_"+var_categorical[ii])[0].innerText) {
                result.categorical[i].var = var_categorical[ii];
            }

        }
    }

    /// Load Configuration

    for (i = 0; i < result.numerical.length; i++) {
        if (result.numerical[i].var !== undefined) {
            load_check_status(result.numerical[i].var,"checked");
            load_option_numerical(result.numerical[i].var,result.numerical[i].mode);
            load_value_numerical(result.numerical[i].var,result.numerical[i].mode, result.numerical[i].value);
        }
    }

    for (i = 0; i < result.categorical.length; i++) {
        if (result.categorical[i].var !== undefined) {
            load_check_status(result.categorical[i].var,"checked");
            load_option_categorical(result.categorical[i].var, result.categorical[i].value);
        }
    }
      
}
    


