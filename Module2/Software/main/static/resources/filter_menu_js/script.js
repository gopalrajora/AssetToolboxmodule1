$('select[data-menu]').each(function() {
    var myOptions = {
        none : {
            text: 'None',
            selected: true
        },
        gr : {
            text: '>  : greater than',
            selected: false
        },
        lo : {
            text: '<  : lower than',
            selected: false
        },
        eq : {
            text: '== : equal to',
            selected: false
        },

        btw : {
            text: '>-<: between',
            selected: false
        },
    };

    var mySelect = $(this);
    $.each(myOptions, function(key, value) {
        mySelect.append( new Option(value['text'],key,false,value['selected']) );
    });

    let select = $(this),
        options = select.find('option'),
        menu = $('<div />').addClass('select-menu'),
        button = $('<div />').addClass('button'),
        list = $('<ul />'),
        arrow = $('<em />').prependTo(button);

    options.each(function(i) {
        let option = $(this);
        list.append($('<li />').text(option.text()));
    });

    menu.css('--t', select.find(':selected').index() * -41 + 'px');

    select.wrap(menu);

    button.append(list).insertAfter(select);

    list.clone().insertAfter(button);

});

$(document).on('click', '.select-menu', function(e) {

    let menu = $(this);
    menu.css("z-index", 2);
    menu.css("text-align", "left")
    if(!menu.hasClass('open')) {
        menu.addClass('open');
    }

});

$(document).on('click', '.select-menu > ul > li', function(e) {

    let li = $(this),
        menu = li.parent().parent(),
        select = menu.children('select'),
        selected = select.find('option:selected'),
        index = li.index();

    menu.css("z-index", 1);
    menu.css('--t', index * -41 + 'px');
    selected.attr('selected', false);
    select.find('option').eq(index).attr('selected', true);

    menu.addClass(index > selected.index() ? 'tilt-down' : 'tilt-up');

    setTimeout(() => {
        menu.removeClass('open tilt-up tilt-down');
        menu.css("z-index", 0);
        option_loaded = $("#"+menu[0].childNodes[0].id)[0].options[$("#"+menu[0].childNodes[0].id)[0].options.selectedIndex].value;
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

    }, 500);
});

$(document).click(e => {
    e.stopPropagation();
    if($('.select-menu').has(e.target).length === 0) {
        $('.select-menu').removeClass('open');
        $('.select-menu').css("z-index", 1);
    }
})


$(document).ready(function () {

    $("#addRow").click(function () {
        $("#myTable").append("<tr><td>row</td><td><input type='text'></td></tr>");
    });
});