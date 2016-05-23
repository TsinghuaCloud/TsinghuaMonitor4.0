/**
 * Created by pwwpcheng on 2016/5/8.
 */

$(document).ready(function(){
    var instance_id = $('#instance-id').attr('value');
    console.info("/api/analysis/instance/"
                    + instance_id + '/process');
    process_table_handle = $('#process-table').DataTable({
        //dom: "<'row'<'col-sm-5'<'meter-display'>><'col-sm-7 pull-right'<'meter-searchbox'>>>" +
        //    "<'row'<'col-sm-12'tr>>" +
        //    "<'row'<'col-sm-5'i><'col-sm-7'p>>",
        //processing: true,
        //serverSide: true,
        ajax: {
            "url": "http://" + window.location.host + "/api/analysis/instance/"
                    + instance_id + '/process/',
            "contentType": "application/json",
            "type": "GET",
            "data": function(data){
                console.info(data);
                return data;
            //},
            //"success": function(data){
            //    var ret_data = {};
            //    ret_data['length'] = data.length;
            //    ret_data['data'] = data;
            //    console.info(ret_data);
            //    return ret_data;
            }
        },
        "columns": [
            {"data": "pid"},
            {"data": "name"},
            {"data": "state"},
            {"data": "physical_memory_usage"},
            {"data": "virtual_memory_usage"},
            {"data": "memory_percent"},
            {"data": "cpu_usage"},
            {"data": "pid"}
        ],
        "columnDefs": [
            {
                "targets": [0, 2, 3, 4, 5, 6, 7],
                "searchable": false
            },
            {
                "targets": [0, 1, 2, 3, 4, 5, 6],
                "sortable": true
            },
            {
                "targets": [7],
                "sortable": false,
                "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                    //$(nTd).html("<input type='checkbox' onclick='" + oData.meter_id + "'>");
                    $(nTd).html('<a class="btn btn-sm btn-default" onclick="some_function('
                                + iRow + ')">查看进程</a>');
                }
            }
        ],
        //responsive: true,
        "createdRow": function (row, data, index) {
        },
        "fnDrawCallback": function(){
            var now_time = new Date();
            $('#refreshed-time').html(now_time.toLocaleTimeString());
        }
    });
    var instance_name = translate_name($('[name="instance-name"]').html(), 'resource_id');
    $('[name="instance-name"]').html(instance_name);

});


function refreshProcessTable(){
    process_table_handle.ajax.reload();

}

setInterval("refreshProcessTable()", 10000);