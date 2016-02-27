$(document).ready(function(){
    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", $('#alarm-form [name="csrfmiddlewaretoken"]')[0].value);
        }
    }
    });
    datatable_handle = $('#machine-table').DataTable({
        dom: "<'row'<'col-sm-7'<'typebox'>><'col-sm-4 pull-right'l>>" +
                "<'row'<'col-sm-12'tr>>" +
                "<'row'<'col-sm-5'i><'col-sm-7'p>>",
        processing: true,
        ajax: {
            "url": "http://" + window.location.host
                                + "/api/servers/vm-list",
            "contentType": "application/json",
            "type": "GET"
        },
        "columns": [
            {"data": "id"},
            {"data": "name"},
            {"data": "id"}
        ],
        "columnDefs": [
            {
                "targets": [0, 1, 2],
                "width": '40%',
                "sortable": false
            },
            {
                "targets": [2],
                "width": '30%' ,
                "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                    $(nTd).html('<a onclick="getMeterList(\'' + oData.id + '\',\''+ oData.name + '\')" ' +
                    'class="btn btn-sm btn-primary">选择该主机</a>')
                }
            }
        ],
        responsive: true
    });
    setTimeout(function(){
        var step = $('#alarm-form [name="cur_step"]')[0].value;
        if (step === '1'){
            var search_html= document.getElementById('machine-type-select-box').innerHTML;
            $("div.typebox").html(search_html);
        }
        else if(step === '2' || step === '3')
            loadDataFromForm();
        else if(step ==='4')
            loadAlarmConfirmation();
    }, 1);
});

$(function () {
    initializeMeterSelect();
});

var chartData=[];

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
    "dataDateFormat": "YYYY-MM-DD HH:NN:SS",
    "categoryAxis": {
        "parseDates": true,
        "minPeriod": "SS",
        "axisColor": "#DADADA",
        "dashLength": 1,
        "minorGridEnabled": true
    },
    "export": {
        "enabled": true
    }
});

function next_step() {
    var next_step = document.getElementsByName("next_step")[0];
    var current_step = document.getElementsByName("cur_step")[0];
    if (current_step.value === '3')
        submitAlarmActions();
    if (current_step.value === '4')
        next_step.value = 'post';
    else
        next_step.value = parseInt(current_step.value) + 1;
    document.getElementById('alarm-form').submit();
}

function prev_step() {
    var next_step = document.getElementsByName("next_step")[0];
    var current_step = document.getElementsByName("cur_step")[0];
    next_step.value = parseInt(current_step.value) - 1;
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
            if ((action_detail_list[j]).value === "") continue;
            var new_action = document.createElement('input');
            new_action.setAttribute('name', action_name);
            var new_action_value = encodeURIComponent('type=' + action_type_list[j].value  + '&detail=' + action_detail_list[j].value);
            new_action.setAttribute('value', new_action_value);
            submit_form_handle.appendChild(new_action);
        }
    }
}

function initializeMeterSelect(){
    $("#meter-select").select2({
        ajax: {
            url: '/api/meters/meter-list?resource_id_match='
                        + $('#alarm-form [name="resource_id"]')[0].value,
            dataType: 'json',
            type: 'GET',
            delay: 500,
            processResults: function (data, page) {
                var i;
                var result = [];
                for (i = 0; i < data.data.length; i++){
                    var meter = {
                        'id': data.data[i]['name'],
                        'text': translate_name(data.data[i]['name'], 'meter_name'),
                    };
                    result.push(meter);
                }
                return {
                    results: result
                };
            }
        },
        placeholder: "Select an item",
        allowClear: true
    });
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
    $(document).on('change', '.alarm-form-element:input,select', function(){
        var this_name = $(this).attr('name');
        $('#alarm-form [name="'+this_name+'"]')[0].value = this.value;
    });
    $(document).on('click', '.alarm-form-element:input,select', function(){
        var this_name = $(this).attr('name');
        $('#alarm-form [name="'+this_name+'"]')[0].value = this.value;
    });
    $(document).on('change', '.alarm-action-element', function(){
        var this_name = $(this).attr('name');
        $('#alarm-form [name="'+this_name+'"]')[0].value = $('#alarm-detail-wrapper [name="'+this_name+'"]')[0].value
    });
    $(document).on('click', '.machine-type-selector', function(){
        datatable_handle.ajax.url("http://" + window.location.host
                                    + "/api/servers/"
                                    + this.value
                                    + '-list');
        datatable_handle.ajax.reload();
    });
    $(document).on("change", '#meter-select', function(e) {
        updateMeterChart();
    });
    $(document).on("change", '#alarm-form [name="resource_id"]', function(e) {

    });
});

function getMeterList(resource_id, resource_name){
    $('#alarm-form [name="resource_id"]')[0].value = resource_id;
    $('#machine-name')[0].innerHTML = resource_name;
    $("#meter-select")[0].value = "";
    initializeMeterSelect();
}

function updateMeterChart(){
    var resource_id = $('#alarm-form [name="resource_id"]')[0].value;
    var name_m = $('#alarm-form [name="meter_name"]')[0].value;
    var selected_meter = {};
    selected_meter[name_m] = [resource_id];

    // Here we just request for one meter's data.
    var chart_data_handle = $.get('/api/meters/meter-samples', selected_meter, function (data) {
        var chart_data = data['data'];
        // Get series' names
        var chart_data_object = {};
        var meter_samples, sample, date_string;
        meter_samples = chart_data[0]['data'];
        var meter_display_name = (chart_data[0])['meter_name'];
        for (var j = 0; j < meter_samples.length; j++) {
            sample = meter_samples[j];
            var new_date = new Date(sample['timestamp']);
            date_string = new_date.getTime().toString();
            if (date_string in chart_data_object) {
                chart_data_object[new_date][meter_display_name] = sample['counter_volume'];
            } else {
                chart_data_object[new_date] = {};
                chart_data_object[new_date]['date'] = new_date;
                chart_data_object[new_date][meter_display_name] = sample['counter_volume'];
            }
        }

        // Add data into dataprovider
        chartData = [];
        for (var key in chart_data_object) {
            if (chart_data_object.hasOwnProperty(key)) {
              chartData.push(chart_data_object[key]);
            }
        }
        chart.dataProvider = chartData.sort(compareDate);
        chart.graphs[0].valueField = meter_display_name;
        chart.validateData();
        chart.validateNow();
    });

}

function loadDataFromForm(){
    var load_elements = $('.alarm-form-element');
    var index;
    for(index = 0; index < load_elements.length; index++){
        var element = load_elements[index];
        if(['INPUT', 'SELECT'].indexOf(element.tagName) > -1)
            element.value = $('#alarm-form [name="'+element.getAttribute('name')+'"]')[0].value;
        else if(['LABEL'].indexOf(element.tagName) > -1)
            element.innerHTML = translate_name($('#alarm-form [name="'+element.getAttribute('name')+'"]')[0].value,
                                                    element.getAttribute('name'));
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
            var match_result = regMatchTypeDetail.exec(decodeURIComponent(action_list[list_index].value));
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
        element.textContent = translate_name(getAlarmFormElement(element.getAttribute('name')).value, element.getAttribute('name'));
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
            var match_result = regMatchTypeDetail.exec(decodeURIComponent(action_list[list_index].value));
            var append_html = document.createElement('p');
            append_html.textContent = translate_name(match_result[1], 'notification_type') + ": " + match_result[2];
            base_element.appendChild(append_html);
        }
    }


    $('.confirm-trigger-element')[0].innerHTML =
        '当   <b>' + getAlarmFormElement('resource_id').value
        + '  </b>  的  <b>' + translate_name(getAlarmFormElement('meter_name').value, 'meter_name')
        + '  </b>  在  <b>' + getAlarmFormElement('period').value
        + '  </b>  秒内  <b>' + translate_name(getAlarmFormElement('statistic').value, 'statistic')
        + '  </b>  <b>' + translate_name(getAlarmFormElement('comparison_operator').value, 'comparison_operator')
        + '  </b>  <b>' + getAlarmFormElement('threshold').value
        + '  </b>  时触发警报';
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getFormattedDate(dt)
{
    var yyyy = dt.getFullYear().toString();
   var MM = (dt.getMonth()+1).toString();
   var dd  = dt.getDate().toString();
   var hh = dt.getHours().toString();
   var mm = dt.getMinutes().toString();
   var ss = dt.getSeconds().toString();

   //Returns your formatted result
  return yyyy + '-' + (MM[1]?MM:"0"+MM[0]) + '-' + (dd[1]?dd:"0"+dd[0]) + 'T' + (hh[1]?hh:"0"+hh[0]) + ':' + (mm[1]?mm:"0"+mm[0]) + ':' + (ss[1]?ss:"0"+ss[0])+'Z';
}

function compareDate(a,b) {
  if (a.date < b.date)
    return -1;
  else if (a.date > b.date)
    return 1;
  else
    return 0;
}