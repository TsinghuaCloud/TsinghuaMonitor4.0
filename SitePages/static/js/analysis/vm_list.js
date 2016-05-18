/**
 * Created by pwwpcheng on 2015/12/30.
 */
function get_para_from_url(name){
   if(name=(new RegExp('[?&]'+encodeURIComponent(name)+'=([^&]*)')).exec(location.search))
      return decodeURIComponent(name[1]);
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(document).ready(function () {
    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", $('[name="csrfmiddlewaretoken"]').val());
        }
    }
    });

    machine_table_handle = $('#machine-table').DataTable({
        dom: "<'row'<'col-sm-7'<'machine-typebox'>><'col-sm-4 pull-right'>>" +
                "<'row'<'col-sm-12'tr>>" +
                "<'row'<'col-sm-4'l><'col-sm-3'i><'col-sm-5'p>>",
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
            {"data": "hypervisor"},
            {"data": 'status'},
            {"data": 'id'}
        ],
        "columnDefs": [
            {
                "targets": [1, 2, 3],
                "sortable": true
            },
            {
                "targets": [0],
                "width": "25%"
            },

            {
                "targets": [3],
                "width": "10%",
                "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                    $(nTd).html(translate_name(sData, 'hypervisor_status', 'CN'));
                }
            },
            {
                "targets": [0, 4],
                "sortable": false
            },
            {
                "targets": [4],
                "width": '16%' ,
                "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                    console.info(oData);
                    if(oData.status === 'ACTIVE')
                        $(nTd).html('<a href="/analysis/resources/'+oData.id + '/process/"'+
                        'class="btn btn-sm btn-default">查看进程数据</a>');
                    else
                         //$(nTd).html('<a class="disabled btn btn-sm btn-default">查看进程数据</a>');
                        $(nTd).html('');
                }
            }
        ],
        responsive: true,
        "order": [[ 2, "asc" ]]
    });

    var search_html=
    $("div.meter-searchbox").html($('#datatables-searchbox').html());
    //$("div.machine-typebox").html($('#machine-type-box').html());
    $("div.meter-display").html($('#selected-meter-display').html());

    $('#meter-table').on('xhr.dt', function ( events, settings, json, xhr ) {
        if(json.status === 'error') {
            alert(json.error_msg);
            json.data = [];
        }
        // Note no return - manipulate the data directly in the JSON object.
    } )
});
