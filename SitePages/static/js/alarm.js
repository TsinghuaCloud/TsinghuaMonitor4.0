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

// NextTab and prevTab are used to switch tabs between alarm information tabs.
// The code is copied from
//      http://stackoverflow.com/questions/9252127/how-to-change-twitter-bootstrap-tab-when-button-is-pressed
function nextTab(elem) {
  $(elem + ' li.active')
    .next()
    .find('a[data-toggle="tab"]')
    .click();
}
function prevTab(elem) {
  $(elem + ' li.active')
    .prev()
    .find('a[data-toggle="tab"]')
    .click();
}


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
    var step_element = document.getElementsByName("step")[0];
    step_element.value = parseInt(step_element.value) + 1;
    document.getElementById('alarm-form').submit();
}

function prev_step() {
    var step_element = document.getElementsByName("step")[0];
    step_element.value = parseInt(step_element.value) - 1;
    document.getElementById('alarm-form').submit();
}

$(function()
{
    $(document).on('click', '.btn-add', function(e)
    {
        e.preventDefault();
        var controlForm = $(this).parents('.controls form:first'),
            currentEntry = $(this).parents('.entry:first'),
            newEntry = $(currentEntry.clone()).appendTo(controlForm);
        this_element = this;
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
});


