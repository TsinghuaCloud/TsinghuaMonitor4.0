/**
 * Created by pwwpcheng on 2016/5/8.
 */

$(function(){
    var instance_id = $('#instance-id').value();
    process_table_handle = $('#process-table').DataTable({
        dom: "<'row'<'col-sm-5'<'meter-display'>><'col-sm-7 pull-right'<'meter-searchbox'>>>" +
            "<'row'<'col-sm-12'tr>>" +
            "<'row'<'col-sm-5'i><'col-sm-7'p>>",
        processing: true,
        serverSide: true,
        ajax: {
            "url": "/api/monitor/" + instance_id + '/process',
            "contentType": "application/json",
            "type": "GET"
        },
        "columns": [
            {"data": "pid"},
            {"data": "name"},
            {"data": "state"},
            {"data": "physical_memory_usage"},
            {"data": "virtual_memory_usage"},
            {"data": "memory_percent"},
            {"data": "cpu_percent"},
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
        responsive: true,
        "createdRow": function (row, data, index) {
        }
    });
});