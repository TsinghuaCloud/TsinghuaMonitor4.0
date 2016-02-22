/**
 * Created by pwwpcheng on 2015/12/30.
 */
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(document).ready(function () {
    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", document.getElementById("csrfmiddlewaretoken").value);
        }
    }
    });
    datatable_handle = $('#alarm-list-table').DataTable({
        dom: '<"toolbar">lrtip',
        processing: true,
        ajax: {
            "url": "http://" + window.location.host + "/api/alarms/alarm-list",
            "contentType": "application/json",
            "type": "POST",
            "data": function (d) {
                var query_value = document.getElementById("search-value").value.trim();
                var query_filter = document.getElementById("search-filter").value;
                if(query_value != ""){
                    d.q = [];
                    d.q[0] = {};
                    d.q[0].field= query_filter;
                    d.q[0].value = query_value;
                }
                return JSON.stringify(d);
            }
        },
        "columns": [
            {"data": "alarm_id"},
            {"data": "name"},
            {"data": "state"},
            {"data": "enabled"},
            {"data": "description"},
            {"data": "alarm_id"}
        ],
        "columnDefs": [
            {
                "targets": [0],
                "visible": false,
                "searchable": false
            },
            {
                "targets": [0, 1, 2, 3, 4, 5],
                "sortable": false
            },
            {
                "targets": [2],
                "fnCreatedCell": function(nTd, sData, oData, iRow, iCol){
                    $(nTd).html(translate_name(oData.state, 'alarm_state'))
                }
            },
            {
                "targets": [3],
                "width": "10%",
                "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                    $(nTd).html('<div class="material-switch">' +
                                    '<input id="switch-input-'+ oData.alarm_id +
                                    '" type="checkbox"' + (oData.enabled ? 'checked' : '')  + '/>' +
                                    '<label for="switch-input-' + oData.alarm_id +'" class="label-primary"></label>' +
                                    '</div>');
                }
            },
            {
                "targets": [4],
                "width": "30%"
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
                "targets": [5],
                "width": "18%",
                "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                    $(nTd).html('<a class="btn btn-xs btn-empty fa fa-search" ' +
                                'href="alarm-detail?alarm_id=' + oData.alarm_id +
                                '"></a>' +
                                '<a class="btn btn-xs btn-empty fa fa-gear" ' +
                                'href="/api/alarms/modify-alarms?alarm_id=' + oData.alarm_id +
                                '"></a>' +
                                '<a class="btn btn-xs btn-empty fa fa-trash-o" ' +
                                'href="/api/alarms/delete-alarms?alarm_id=' + oData.alarm_id +
                                '"></a>');
                }
            }
        ],
        responsive: true,
        "createdRow": function (row, data, index) {
            if (false) {
                $('td', row).eq(0).children()[0].checked = true;
            }
        }
    });
    var search_html= document.getElementById('alarm-table-searchbox').innerHTML;
    $("div.toolbar").html(search_html);
});

function reloadTableData(){
    datatable_handle.ajax.reload();
}

function clearSearchCriteria(){
    document.getElementById("search-value").value = '';
    datatable_handle.ajax.reload();
}

$(function(){
    $(document).on('mouseenter', '.fixed-layout-table * td', function(){
        $(this).addClass('td-show-all');
    })
        .on('mouseleave', '.td-show-all', function(){
        $(this).removeClass('td-show-all');
    });

});