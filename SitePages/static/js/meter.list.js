/**
 * Created by pwwpcheng on 2015/12/30.
 */

$(document).ready(function () {
    datatable_handle = $('#meter-table').DataTable({
        processing: true,
        serverSide: true,
        //pagingType: "input",
        ajax: "http://" + window.location.host + "/api/meters/meter-list",
        "columns": [
            {"data": "unit"},
            {"data": "meter_id"},
            {"data": "resource_id"},
            {"data": "resource_name"},
            {"data": "name"},
            {"data": "type"}
        ],
        "columnDefs": [
            {
                "targets": [1],
                "visible": false,
                "searchable": false
            },
            {
                "targets": [0,1,2,3,4,5],
                "sortable": false
            },
            {
                "targets": [0],
                "sortable": false,
                "width": "5%",
                "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                    //$(nTd).html("<input type='checkbox' onclick='" + oData.meter_id + "'>");
                    $(nTd).html("<input type='checkbox' onclick='updateMeterList(" + iRow + ")'>");
                }
            },
            {
                "targets": [4],
                "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                    //$(nTd).html("<input type='checkbox' onclick='" + oData.meter_id + "'>");
                    if(sData in meter_name_list){
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
            }

        ],
        "order": [[1, "desc"]],
        responsive: true,
        "createdRow": function ( row, data, index ) {
            if (checkMeterList(data)) {
                $('td', row).eq(0).children()[0].checked = true;
            }
        }
    });
    //var ctx = $("#meter-chart").get(0).getContext("2d");
    // This will get the first returned node in the jQuery collection.
    //var myNewChart = new Chart(ctx);
});

var selected_meter_list = {};
/* selected_meter_list stores selected meter on multiple datatable pages
 * Structure:
 * {
 *     <name>: [resource_id, resource_id...],
 *     <name>: [resource_id, resource_id...],
 * }
 */

function checkMeterList(data){
    /*
    Check if the requested meter is in selected_meter_list.
    Return true if in, [false] if not.
     */
    //var current_row_handle = datatable_handle.data()[row];
    //var current_meter = {'meter_name': current_row_handle['meter_name'],
    //                     'resource_id': current_row_handle['resource_id']};
    var meter_name = data['name'];
    if (meter_name in selected_meter_list){
        for(var i = 0; i < selected_meter_list[meter_name].length; i++){
            if(selected_meter_list[meter_name][i] == data['resource_id'])
                return true;
        }
    }
    return false;
}

function updateMeterList(row){
    /*
    If requested meter in select row is in selected_meter_list,
    add this meter into selected_meter_list,
    else, remove this meter from selected_meter_list.
    Notice: This function considers there are one more same <resource_id>s
            in the meter_name array, and removes them all.
     */
    var row_data = datatable_handle.data()[row];
    if(checkMeterList(row_data)){
        var index = (selected_meter_list[row_data['name']]).indexOf(row_data['resource_id']);
        while (index > -1) {
            (selected_meter_list[row_data['name']]).splice(index, 1);
            index = (selected_meter_list[row_data['name']]).indexOf(row_data['resource_id'])
        }
        if ((selected_meter_list[row_data['name']]).length === 0){
            delete selected_meter_list[row_data['name']];
        }
    }
    else{
        if (row_data['name'] in selected_meter_list){
            (selected_meter_list[row_data['name']]).push(row_data['resource_id']);
        }
        else{
            selected_meter_list[row_data['name']] = [row_data['resource_id']]
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
            var meter_display_name = (chart_data[i])['meter_name'] + '@' + chart_data[i]['resource_id'];
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
            console.info(valueAxis.axisColor);
            console.info(graph.lineColor);

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
        for (var i = 0; i < chart_dataset_list.length; i++){
            chart.valueAxes[i].axisColor = chart.graphs[i].lineColorR;
        };
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

var chartData=sampleData();

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
    "dataDateFormat": "YYYY-MM-DD HH:NN",
	"categoryAxis": {
		"minPeriod": "mm",
		"parseDates": true
	},
    "export": {
        "enabled": true,
        "position": "bottom-right"
     }
});

chart.addListener("rendered", zoomChart);
zoomChart();

// this method is called when chart is first inited as we listen for "rendered" event
function zoomChart() {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    chart.zoomToIndexes(chartData.length - 40, chartData.length - 1);
}

function sampleData() {
    chartData=JSON.parse('[' +
    '{"date":"2016-01-13T23:34:13.499Z","views":0.08830797984264792},' +
    '{"date":"2016-01-14T23:24:13.499Z","views":0.08830797984264792},' +
    '{"date":"2016-01-15T22:54:13.499Z","views":0.08830797984264792},' +
    '{"date":"2016-01-16T22:24:13.499Z","views":0.08830797984264792},' +
    '{"date":"2016-01-17T22:04:13.499Z","views":0.08830797984264792},' +
    '{"date":"2016-01-18T21:44:13.499Z","views":0.08830797984264792},' +
    '{"date":"2016-01-19T20:54:13.499Z","views":0.08830797984264792},' +
    '{"date":"2016-01-20T20:44:13.499Z","views":0.08830797984264792}]');
    return chartData;
}
