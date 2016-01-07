/**
 * Created by pwwpcheng on 2015/12/30.
 */
$(document).ready(function () {
        $('#meter-table').DataTable({
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
                        $(nTd).html("<input type='checkbox' id='" + oData.meter_id + "'>");
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
            responsive: true
        });
        //var ctx = $("#meter-chart").get(0).getContext("2d");
        // This will get the first returned node in the jQuery collection.
        //var myNewChart = new Chart(ctx);
    });

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
