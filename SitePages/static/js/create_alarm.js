$(document).ready(function(){
    machine_table_handle = $('#machine-table').DataTable({
        "dom": 'tp',
        "columns": [
            {"data": "checkbox"},
            {"data": "id"},
            {"data": "name"},
            {"data": "backup"}
        ],
        "columnDefs": [
            {
                "targets": [0, 1, 2, 3],
                "sortable": false
            },
            {
                "targets": [0],
                "sortable": false,
                "width": "5%",
                "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                    $(nTd).html("<input type='checkbox' onclick='updateMeterList(" + iRow + ")'>");
                }
            },
        ],
        responsive: true
    });
    setTimeout(function(){
        var step = $('#alarm-form [name="cur_step"]')[0].value;
        if(step === '2' || step === '3')
            loadDataFromForm();
        else if(step ==='4')
            loadAlarmConfirmation();

    }, 1);
});

$(function () {
    $("#project-select").select2({
        ajax: {
            url: '/projects/get-project-name-list',
            dataType: 'json',
            type: 'GET',
            delay: 500,
            processResults: function (data, page) {
                return {
                    results: data
                };
            }
        },
        placeholder: "Select an item",
        allowClear: true
    });
});

var chartData=generateChartData();

var chart = AmCharts.makeChart("meter-chart", {
    "type": "serial",
    "theme": "light",
    "marginRight": 80,
    "autoMarginOffset": 20,
    "marginTop": 7,
    "dataProvider": chartData,
    "valueAxes": [{
        "axisAlpha": 0.2,
        "dashLength": 1,
        "position": "left"
    }],
    "mouseWheelZoomEnabled": true,
    "graphs": [{
        "id": "g1",
        "balloonText": "[[value]]",
        "bullet": "round",
        "bulletBorderAlpha": 1,
        "bulletColor": "#FFFFFF",
        "hideBulletsCount": 50,
        "title": "red line",
        "valueField": "visits",
        "useLineColorForBulletBorder": true,
        "balloon":{
            "drop":true
        }
    }],
    "chartScrollbar": {
        "autoGridCount": true,
        "graph": "g1",
        "scrollbarHeight": 40
    },
    "chartCursor": {
       "limitToGraph":"g1"
    },
    "categoryField": "date",
    "categoryAxis": {
        "parseDates": true,
        "axisColor": "#DADADA",
        "dashLength": 1,
        "minorGridEnabled": true
    },
    "export": {
        "enabled": true
    }
});

chart.addListener("rendered", zoomChart);
zoomChart();

// this method is called when chart is first inited as we listen for "rendered" event
function zoomChart() {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    chart.zoomToIndexes(chartData.length - 40, chartData.length - 1);
}

// generate some random data, quite different range
function generateChartData() {
    var chartData = [];
    var firstDate = new Date();
    firstDate.setDate(firstDate.getDate() - 5);

    for (var i = 0; i < 1000; i++) {
        // we create date objects here. In your data, you can have date strings
        // and then set format of your dates using chart.dataDateFormat property,
        // however when possible, use date objects, as this will speed up chart rendering.
        var newDate = new Date(firstDate);
        newDate.setDate(newDate.getDate() + i);

        var visits = Math.round(Math.random() * (40 + i / 5)) + 20 + i;
        chartData.push({
            date: newDate,
            visits: visits
        });
    }
    return chartData;
}

function next_step() {
    var step_element = document.getElementsByName("next_step")[0];
    step_element.value = parseInt(step_element.value) + 1;
    var current_step = document.getElementsByName("cur_step")[0];
    if (current_step.value === '3'){
        submitAlarmActions();
    }
    document.getElementById('alarm-form').submit();
}

function prev_step() {
    var step_element = document.getElementsByName("next_step")[0];
    step_element.value = parseInt(step_element.value) - 1;
    var current_step = document.getElementsByName("cur_step")[0];
    if (current_step.value === '3'){
        submitAlarmActions();
    }
    document.getElementById('alarm-form').submit();
}

function submitAlarmActions(){
    var action_forms = $('.alarm-action-element');
    var i, j;
    var submit_form_handle = $('#alarm-form')[0];
    for(i = 0; i < action_forms.length; i++){
        var action_name = action_forms[i].getAttribute('name');
        while(submit_form_handle.children[action_name]){
            submit_form_handle.removeChild(submit_form_handle.children[action_name])
        }
        var action_type_list = action_forms[i].getElementsByTagName('select');
        var action_detail_list = action_forms[i].getElementsByTagName('input');
        for(j = 0; j < action_type_list.length; j++){
            var new_action = document.createElement('input');
            new_action.setAttribute('name', action_name);
            new_action.setAttribute('value', 'type=' + action_type_list[j].value
                                            + '&detail=' + action_detail_list[j].value);
            submit_form_handle.appendChild(new_action);
        }
    }
}

$(function()
{
    $(document).on('click', '.btn-add', function(e)
    {
        e.preventDefault();
        var controlForm = $(this).parents('.controls form:first'),
            currentEntry = $(this).parents('.entry:first'),
            newEntry = $(currentEntry.clone()).appendTo(controlForm);
        newEntry.find('input').val('');
        controlForm.find('.entry:not(:last) .btn-add')
            .removeClass('btn-add').addClass('btn-remove')
            .removeClass('btn-primary').addClass('btn-default')
            .html('<span class="glyphicon glyphicon-minus"></span>');
    }).on('click', '.btn-remove', function(e)
    {
		$(this).parents('.entry:first').remove();
		e.preventDefault();
		return false;
	});
    $(document).on('change', '.alarm-form-element', function(){
        var this_name = $(this).attr('name');
        $('#alarm-form [name="'+this_name+'"]')[0].value = $('#alarm-detail-wrapper [name="'+this_name+'"]')[0].value
    });
    $(document).on('change', '.alarm-action-element', function(){
        var this_name = $(this).attr('name');
        //$('#alarm-form [name="'+this_name+'"]')[0].value = $('#alarm-detail-wrapper [name="'+this_name+'"]')[0].value
    });

});

function loadDataFromForm(){
    var load_elements = $('.alarm-form-element');
    var index;
    for(index = 0; index < load_elements.length; index++){
        var element = load_elements[index];
        element.value = $('#alarm-form [name="'+element.name+'"]')[0].value;
    }

    var actions = $('.alarm-action-element');
    for(index = 0; index < actions.length; index++){
        var action = actions[index];
        var action_list = $('#alarm-form [name="'+action.getAttribute('name')+'"]');
        var list_index, base_element;
        base_element = $('#alarm-detail-wrapper [name="'+action.getAttribute('name')+'"]')[0];

        for(list_index = 0; list_index < action_list.length; list_index++){
            // Match result [0: whole string  1: type_match(email|message)  2: detail_match]
            var regMatchTypeDetail = /type=(email|message|link)\&detail=(.*)/g;
            var match_result = regMatchTypeDetail.exec(action_list[list_index].value);
            if(list_index === 0){
                base_element.getElementsByTagName('select')[0].value = match_result[1];
                base_element.getElementsByTagName('input')[0].value = match_result[2];
            }else{
                base_element.getElementsByClassName('btn-add')[0].click();
                var selects =  base_element.getElementsByTagName('select');
                selects[selects.length-1].value = match_result[1];
                var inputs = base_element.getElementsByTagName('input');
                inputs[inputs.length-1].value = match_result[2];
            }
        }
    }
}

function loadAlarmConfirmation(){
    var getAlarmFormElement = function(element_name){
        // function has a hidden argument. Should be treated as getAlarmFormElement(name, getAllElements)
        if(arguments[1] === true)
            return $('#alarm-form [name="'+element_name+'"]');
        return $('#alarm-form [name="'+element_name+'"]')[0];
    };
    var load_elements = $('.confirm-element');
    var index;
    for(index = 0; index < load_elements.length; index++){
        var element = load_elements[index];
        element.textContent = translate(getAlarmFormElement(element.getAttribute('name')).value, element.getAttribute('name'));
    }

    var actions = $('.confirm-action-element');
    for(index = 0; index < actions.length; index++){
        var action = actions[index];
        var action_list = getAlarmFormElement(action.getAttribute('name'), true);
        var list_index, base_element;
        base_element = $('#alarm-detail-wrapper [name="'+action.getAttribute('name')+'"]')[0];

        for(list_index = 0; list_index < action_list.length; list_index++){
            // Match result [0: whole string  1: type_match(email|message)  2: detail_match]
            var regMatchTypeDetail = /type=(email|message|link)\&detail=(.*)/g;
            var match_result = regMatchTypeDetail.exec(action_list[list_index].value);
            var append_html = document.createElement('p');
            append_html.textContent = translate(match_result[1], 'notification_type') + ": " + match_result[2];
            base_element.appendChild(append_html);
        }
    }


    $('.confirm-trigger-element')[0].textContent =
        '当 ' + getAlarmFormElement('resource_id').value
        + ' 的' + translate(getAlarmFormElement('meter_name').value, 'meter_name')
        + ' 在' + getAlarmFormElement('period').value
        + ' 秒内' + translate(getAlarmFormElement('statistic').value, 'statistic')
        + '' + translate(getAlarmFormElement('comparison_operator').value, 'comparison_operator')
        + ' ' + getAlarmFormElement('threshold').value
        + ' 时触发警报';
}

