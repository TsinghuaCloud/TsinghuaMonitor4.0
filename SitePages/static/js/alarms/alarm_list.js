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
            xhr.setRequestHeader("X-CSRFToken", $('#csrfmiddlewaretoken').attr('value'));
        }
    }
    });
    meter_table_handle = $('#alarm-list-table').DataTable({
        dom: '<"toolbar">lrtip',
        processing: true,
        paging: true,
        ajax: {
            "url": "http://" + window.location.host + "/api/alarms/alarm-list",
            "contentType": "application/json",
            "type": "POST",
            "data": function (d) {
                var query_value = $("#search-value").attr('value').trim();
                var query_filter = $('#search-filter').attr('value');
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
                                'href="/monitor/alarms/alarm-detail/' + oData.alarm_id +
                                '"></a>' +
                                '<a class="btn btn-xs btn-empty fa fa-gear" ' +
                                'href="/monitor/alarms/edit-alarm/' + oData.alarm_id +
                                '"></a>' +
                                '<a class="btn btn-xs btn-empty fa fa-trash-o" data-toggle="modal" ' +
                                'data-target="#delete-alarm-modal" data-alarm-name="'+oData.name+'" ' +
                                'data-alarm-id="'+ oData.alarm_id +'"></a>');
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
    //var search_html= document.getElementById('alarm-table-searchbox').innerHTML;
    //$("div.toolbar").html(search_html);
});

function reloadTableData(){
    meter_table_handle.ajax.reload();
}

function clearSearchCriteria(){
    $("#search-value").value = '';
    meter_table_handle.ajax.reload();
}

$(function(){
    $(document).on('mouseenter', '.fixed-layout-table * td', function(){
        $(this).addClass('td-show-all');
    })
        .on('mouseleave', '.td-show-all', function(){
        $(this).removeClass('td-show-all');
    });
    $('#delete-alarm-modal').on('show.bs.modal', function (event) {
        var trigger = $(event.relatedTarget);
        var alarm_id = trigger.data('alarm-id');
        var alarm_name = trigger.data('alarm-name');
        $(this).find('.modal-body * strong').text(alarm_name);
        $(this).find('.modal-body').find('input').attr('value', alarm_id);
    });
    $('#delete-btn').on('click', function () {
        var btn = $(this).button('loading');
        var alarm_id = $(this).parents('.modal-content').find('#delete-alarm-id').attr('value');
        $.getJSON("/api/alarms/delete-alarm/"+alarm_id, function (json) {
            var status = json.status;
            if(status === 'success'){
                $('#delete-alarm-modal').modal('hide');
                add_message('success', json.data);
                reloadTableData();
            }
            else{
                $('#delete-alarm-modal').modal('hide');
                add_message('error', json.error_msg);
            }
        })
            .done(function (json) {
                console.log("second success");
            })
            .fail(function (jqxhr, textStatus, error) {
                add_message('error', error);
            })
            .always(function () {
                btn.button('reset');
            });
    });
    $(document).on('click', '.material-switch label', function(){
        var this_element = $(this);
        var new_state = !($(this).parent('.material-switch').find('input')[0].checked);

        // id of this label is parsed as switch-input-<alarm_id>
        // The length of phrase switch-input- is 13
        // So .slice(13) is used to cut out 'switch-input-'
        //      in order to get alarm_id
        var alarm_id = $(this).attr('for').slice(13);
        $.getJSON('/api/alarms/update-alarm-enabled/' + alarm_id + '/'+
                '?enabled=' + new_state.toString(),
            function(json){
                var status = json.status;
                if(status === 'success'){
                    add_message('success', 'Enabled of alarm ' + alarm_id + ' has been changed');
                }
                else{
                    add_message('error', json.error_msg);
                    this_element.parent('.material-switch').find('input')[0].checked = !new_state;
                }
            }
        ).fail(function (jqxhr, textStatus, error) {
                add_message('error', error);
            });
    });
});