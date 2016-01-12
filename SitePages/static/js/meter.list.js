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
                    $(nTd).html("<input type='checkbox' onclick='update_meter_list(" + iRow + ")'>");
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
            if (check_meter_list(data)) {
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

function check_meter_list(data){
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

function update_meter_list(row){
    /*
    If requested meter in select row is in selected_meter_list,
    add this meter into selected_meter_list,
    else, remove this meter from selected_meter_list.
    Notice: This function considers there are one more same <resource_id>s
            in the meter_name array, and removes them all.
     */
    var row_data = datatable_handle.data()[row];
    if(check_meter_list(row_data)){
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
}

var chartData = generateChartData();

var chart = AmCharts.makeChart("meter-chart", {
    "type": "serial",
    "theme": "light",
    "marginRight": 20,
    "autoMarginOffset": 20,
    "marginTop": 7,
    "dataProvider": chartData,
    "valueAxes": [{
        "axisAlpha": 0.2,
        "dashLength": 1,
        "position": "left"
    }],
    "mouseWheelZoomEnabled": true,
    "chartScrollbar": {
        "autoGridCount": true,
        "graph": "g1",
        "scrollbarHeight": 20
    },
    "chartCursor": {
       "limitToGraph":"g1"
    },
    "graphs": [{
        "lineColor": "#FF6600",
        "bullet": "round",
        "bulletBorderThickness": 1,
        "hideBulletsCount": 30,
        "title": "red line",
        "valueField": "visits",
        "fillAlphas": 0
    }, {
        "lineColor": "#FCD202",
        "bullet": "square",
        "bulletBorderThickness": 1,
        "hideBulletsCount": 30,
        "title": "yellow line",
        "valueField": "hits",
        "fillAlphas": 0
    }, {
        "lineColor": "#B0DE09",
        "bullet": "triangleUp",
        "bulletBorderThickness": 1,
        "hideBulletsCount": 30,
        "title": "green line",
        "valueField": "views",
        "fillAlphas": 0
    }],
    "categoryField": "date",
    "categoryAxis": {
        "parseDates": true,
        "axisColor": "#DADADA",
        "minorGridEnabled": true
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

function generateChartData() {
    var chartData = [];
    var firstDate = new Date();
    firstDate.setDate(firstDate.getDate() - 100);

    for (var i = 0; i < 100; i++) {
        // we create date objects here. In your data, you can have date strings
        // and then set format of your dates using chart.dataDateFormat property,
        // however when possible, use date objects, as this will speed up chart rendering.
        var newDate = new Date(firstDate);
        newDate.setDate(newDate.getDate() + i);

        var visits = Math.round(Math.random() * 40) + 100;
        var hits = Math.round(Math.random() * 80) + 500;
        var views = Math.round(Math.random() * 6000);

        chartData.push({
            date: newDate,
            visits: visits,
            hits: hits,
            views: views
        });
    }
    return chartData;
}
