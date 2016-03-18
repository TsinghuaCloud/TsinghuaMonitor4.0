/**
 * Created by pwwpcheng on 2015/12/30.
 */
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(function(){
    $(document).on('click', '.machine-type-selector', function(){
        machine_table_handle.ajax.url("http://" + window.location.host
                                    + "/api/servers/"
                                    + this.value
                                    + '-list');
        machine_table_handle.ajax.reload();
    });
    tagger_handle.removeTagRelatedElement = function(tag){

    }
});

$(document).ready(function () {
    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", $('[name="csrfmiddlewaretoken"]').val());
        }
    }
    });

    machine_table_handle = $('#machine-table').DataTable({
        dom: "<'row'<'col-sm-7'<'machine-typebox'>><'col-sm-4 pull-right'l>>" +
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
    meter_table_handle = $('#meter-table').DataTable({
        dom: "<'row'<'col-sm-5'<'meter-display'>><'col-sm-7 pull-right'<'meter-searchbox'>>>" +
            "<'row'<'col-sm-12'tr>>" +
            "<'row'<'col-sm-5'i><'col-sm-7'p>>",
        processing: true,
        serverSide: true,
        ajax: {
            "url": "http://" + window.location.host + "/api/meters/meter-list",
            "contentType": "application/json",
            "type": "POST",
            "data": function (d) {
                var query_value = document.getElementById("search-value").value.trim();
                var query_criteria = document.getElementById("search-criteria").value;
                d.q = [];
                if(query_value != ""){
                    d.q[0] = {};
                    d.q[0].field= query_criteria;
                    d.q[0].value = query_value;
                }
                if($('.meter-display [name="selected-machine-id"]').val() != ''){
                    d.q.push({'field': 'resource_id_match',
                              'value': $('.meter-display [name="selected-machine-id"]').val()
                    });
                }
                return JSON.stringify(d);
            }
        },
        "columns": [
            {"data": "unit"},
            {"data": "meter_id"},
            {"data": "resource_id"},
            {"data": "resource_name"},
            {"data": "name"},
            {"data": "type"},
            {"data": "unit"}
        ],
        "columnDefs": [
            {
                "targets": [1, 2],
                "visible": false,
                "searchable": false
            },
            {
                "targets": [0, 1, 2, 3, 4, 5, 6],
                "sortable": false
            },
            {
                "targets": [0],
                "sortable": false,
                "width": "5%",
                "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                    //$(nTd).html("<input type='checkbox' onclick='" + oData.meter_id + "'>");
                    $(nTd).html("<input type='checkbox' onclick='updateMeterListFromTable(" + iRow + ")'>");
                }
            },
            {
                "targets": [4],
                "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                    //$(nTd).html("<input type='checkbox' onclick='" + oData.meter_id + "'>");
                    if (sData in meter_name_list) {
                        $(nTd).html(meter_name_list[sData]);
                    }
                }
            },
            {
                "targets": [5],
                "width": "15%"
//                    "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
//                        $(nTd).html("<button type='button' class='btn btn-xs btn-empty fa fa-search'></button>" +
//                        "<button type='button' class='btn btn-xs btn-empty fa fa-wrench'></button>" +
//                        "<button type='button' class='btn btn-xs btn-empty fa fa-trash-o'></button>");
//                    }
            },
            {
                "targets": [6],
                "width": '15%',
                "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                    $(nTd).html("<a  class='btn btn-xs btn-empty fa fa-wrench'></a>" +
                    "<a href='#' class='btn btn-xs btn-empty fa fa-trash-o'></a>");
                }
            }
        ],
        responsive: true,
        "createdRow": function (row, data, index) {
            if (checkMeterList(data)) {
                $('td', row).eq(0).children()[0].checked = true;
            }
        }
    });
    var search_html=
    $("div.meter-searchbox").html($('#datatables-searchbox').html());
    $("div.machine-typebox").html($('#machine-type-box').html());
    $("div.meter-display").html($('#selected-meter-display').html());

    $('#meter-table').on('xhr.dt', function ( events, settings, json, xhr ) {
        if(json.status === 'error') {
            alert(json.error_msg);
            json.data = [];
        }
        // Note no return - manipulate the data directly in the JSON object.
    } )
});

function getMeterList(resource_id, resource_name){
    $('.meter-display [name="selected-machine-id"]').val(resource_id);
    alert('已选主机： '+ resource_name);
    $('.meter-display [name="selected-machine-name"]').html(resource_name);
    meter_table_handle.ajax.reload();
    $('#meter-tabs a:eq(1)').tab('show');
}

var selected_meter_list = {};
/* selected_meter_list stores selected meter on multiple datatable pages
 * Structure:
 * {
 *     <name>: [resource_id, resource_id...],
 *     <name>: [resource_id, resource_id...],
 * }
 */

function reloadMeterTableData(){
    meter_table_handle.ajax.reload();
}

function clearMeterSearchCriteria(){
    document.getElementById("search-value").value = '';
    meter_table_handle.ajax.reload();
}

function checkMeterList(meter_name, resource_id){
    /*
    Check if the requested meter is in selected_meter_list.
    Return true if in, [false] if not.
     */
    //var current_row_handle = meter_table_handle.data()[row];
    //var current_meter = {'meter_name': current_row_handle['meter_name'],
    //                     'resource_id': current_row_handle['resource_id']};
    if (meter_name in selected_meter_list){
        for(var i = 0; i < selected_meter_list[meter_name].length; i++){
            if(selected_meter_list[meter_name][i] == resource_id)
                return true;
        }
    }
    return false;
}

function updateMeterListFromTable(row){
    var row_data = meter_table_handle.data()[row];
    updateMeterList(row_data['name'], row_data['resource_id']);
}

function updateMeterList(meter_name, resource_id){
    /*
    If requested <meter in select row is in selected_meter_list,
    add this meter into selected_meter_list,
    else, remove this meter from selected_meter_list.
    Notice: This function considers there are one more same <resource_id>s
            in the meter_name array, and removes them all.
    */
    var meter_string = translate_name(meter_name, 'meter_name', 'CN') + '@' +
                        translate_name(resource_id, 'resource_id', 'CN');

    if(checkMeterList(meter_name, resource_id)){
        // The <meter_id, resource_id> combination is in selected list
        tagger_handle.removeTag(meter_string);
        var index = (selected_meter_list[meter_name]).indexOf(resource_id);
        while (index > -1) {
            (selected_meter_list[meter_name]).splice(index, 1);
            index = (selected_meter_list[meter_name]).indexOf()
        }
        if ((selected_meter_list[meter_name]).length === 0){
            delete selected_meter_list[meter_name];
        }
    }
    else{
        // The <meter_id, resource_id> combination is in selected list
        tagger_handle.addTag(meter_string);
        if (meter_name in selected_meter_list){
            (selected_meter_list[meter_name]).push(resource_id);
        }
        else{
            selected_meter_list[meter_name] = [resource_id]
        }
    }
    updateChart();
}

function updateChart(){
    /*
     *
     */
    // Convert data requested from meter-samples api to amchart data
    var chart_data_handle;
    chart_data_handle = $.get('/api/meters/meter-samples', selected_meter_list, function (data) {
        var chart_data = data['data'];

        // Get series' names
        var chart_data_object = {};
        var chart_series_count = chart_data.length;
        var meter_samples, sample, date_string, chart_dataset_list=[];
        for (var i = 0; i < chart_series_count; i++) {
            meter_samples = chart_data[i]['data'];
            var meter_display_name = translate_name((chart_data[i])['meter_name'], 'meter_name') + '@' + chart_data[i]['resource_id'];
            chart_dataset_list.push(meter_display_name);
            for (var j = 0; j < meter_samples.length; j++) {
                sample = meter_samples[j];
                var new_date = new Date(sample['timestamp']);
                date_string = new_date.getTime().toString();
                if (date_string in chart_data_object) {
                    chart_data_object[new_date][meter_display_name] = sample['counter_volume'];
                } else {
                    chart_data_object[new_date] = {};
                    chart_data_object[new_date]['date'] = getFormattedDate(new_date);
                    chart_data_object[new_date][meter_display_name] = sample['counter_volume'];
                }
            }
        }

        // Prepare styles and chart settings for meter chart
        chart.graphs = [];
        chart.valueAxes = [];
        for (var k = 0; k < chart_dataset_list.length; k++){
            // CREATE GRAPH INSTANCE
            var valueAxis = new AmCharts.ValueAxis();
            valueAxis.id = chart_dataset_list[k] + 'axis';
            valueAxis.axisThickness = 2;
            valueAxis.axisAlpha = 1;
            valueAxis.gridAlpha = 0;
            valueAxis.position = (k % 2) ? 'left': 'right';
            valueAxis.offset = Math.floor(k/2) * 50;

            var graph = new AmCharts.AmGraph();

            // SETTINGS
            graph.title = chart_dataset_list[k];
            graph.valueField = chart_dataset_list[k];
            graph.valueAxis = chart_dataset_list[k] + 'axis';
            graph.balloonText = "[[value]]";

            graph.type = "line";
            graph.lineThickness = 2;
            graph.fillAlphas = 0;

            valueAxis.axisColor = graph.lineColor;
            // ATTACH TO CHART INSTANCE
            chart.valueAxes.push(valueAxis);
            chart.addGraph(graph);
        }

        // Add data into dataprovider
        chartData = [];
        for (var key in chart_data_object) {
            if (chart_data_object.hasOwnProperty(key)) {
              chartData.push(chart_data_object[key]);
            }
        }
        chart.dataProvider = chartData.sort(compareDate);
        chart.validateData();
        chart.validateNow();
        for (var m = 0; m < chart_dataset_list.length; m++){
            chart.valueAxes[m].axisColor = chart.graphs[m].lineColorR;
        }
        chart.validateNow();
    });
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

var chartData={};

var chart = AmCharts.makeChart("meter-chart", {
    "legend": {
        "useGraphSettings": true
    },
    "type": "serial",
    "theme": "light",
    "dataProvider": chartData,
    "valueAxes": [{
        'title': 'value'
    }],
    "mouseWheelZoomEnabled": true,
    "chartScrollbar": {
        "autoGridCount": true,
        "scrollbarHeight": 20
    },
    "chartCursor": {
       "cursorPosition": "mouse"
    },
    "graphs": [{
        "lineColor": "#FF6600",
        "bullet": "round",
        "bulletBorderThickness": 1,
        "hideBulletsCount": 30,
        "title": "red line",
        "valueField": "views",
        "fillAlphas": 0
    }],
    "categoryField": "date",
    "dataDateFormat": "YYYY-MM-DD HH:NN:SS",
	"categoryAxis": {
		"minPeriod": "ss",
		"parseDates": true
	},
    "export": {
        "enabled": true,
        "position": "bottom-right"
     }
});
