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
                  
                  var current_machine_type = get_para_from_url('type') || 'vm';
                  
                  machine_table_handle = $('#machine-table').DataTable({
                                                                       dom: "<'row'<'col-sm-7'<'machine-typebox'>><'col-sm-4 pull-right'>>" +
                                                                       "<'row'<'col-sm-12'tr>>" +
                                                                       "<'row'<'col-sm-4'l><'col-sm-3'i><'col-sm-5'p>>",
                                                                       processing: true,
                                                                       ajax: {
                                                                       "url": "http://" + window.location.host
                                                                       + "/api/servers/"
                                                                       + current_machine_type
                                                                       + "-list",
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
                                                                   "url": "http://" + window.location.host + "/api/meters/predict-related-meters",
                                                                   "contentType": "application/json",
                                                                   "type": "POST",
                                                                   "data": function (d) {
                                                                   d.resource_id = $("#search-value").attr('value');
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
                                                                                  "targets": [0, 1, 2],
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
                                                                                  //"width": "5%",
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
                                                                                  //"width": "20%"
                                                                                  //                    "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                                                                                  //                        $(nTd).html("<button type='button' class='btn btn-xs btn-empty fa fa-search'></button>" +
                                                                                  //                        "<button type='button' class='btn btn-xs btn-empty fa fa-wrench'></button>" +
                                                                                  //                        "<button type='button' class='btn btn-xs btn-empty fa fa-trash-o'></button>");
                                                                                  //                    }
                                                                                  },
                                                                                  {
                                                                                  "targets": [6],
                                                                                  //"width": '20%',
                                                                                  "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                                                                                  $(nTd).html("<a class='btn btn-sm btn-default'onclick='updateMeterListFromTable(" + iRow + ")' '>查看指标</a>");
                                                                                  }
                                                                                  }
                                                                                  ],
                                                                   responsive: true,
                                                                   "createdRow": function (row, data, index) {
                                                                   
                                                                   }
                                                                   });
                
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

var predict_data;
var url;
function getMeterList(resource_id, resource_name){
    $('.meter-display [name="selected-machine-id"]').val(resource_id);
    //alert('已选主机： '+ resource_name);
    predict_data = 'name='+resource_name+'&meter=';
    $('.meter-display [name="selected-machine-name"]').html(resource_name);
    $('#search-value').attr('value', resource_id);
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
    alert(meter_name);
    var meter;
    switch(meter_name)
    {
        case 'memory.usage':
            meter = 'memory';
            break;
        case 'disk.usage':
            meter = 'disk';
            break;
        case 'cpu_util':
            meter = 'cpu';
            break;
            
    }
    url = predict_data + meter;
    var chartData = updateChart();
}


function updateChart(){
    var chart_data_handle;
    
    chart_data_handle = $.get('/api/predict/get-data', url, function (data) {
                              var chartData = [];
                              
                              var firstDate = new Date();
                              var current_hour = firstDate.getHours();
                              var current_min = firstDate.getMinutes();
                              var add = 0;
                              if(current_min<30){
                              add = 0;
                              }
                              else{
                              add =1;
                              }
                              var time = current_hour*2 + add;
                              
                              
                              for (var i = 0; i < 48; i++) {
                              //console.info(new Date(data['data_date'+i.toString()]));
                              //console.info(data['data_value'+i.toString()]);
                              var d = new Date(data['data_date'+i.toString()]);
                              var pre_v = data['data_pre_value'+i.toString()];
                              var ac_v = data['data_ac_value'+i.toString()];
                              
                              if(i<time){
                              if(pre_v!=-1)
                              {
                              chartData.push({
                                             date: d,
                                             //value: pre_v,
                                             value3: ac_v
                                             });
                              }else{
                              chartData.push({
                                             date: d,
                                             value3: ac_v
                                             });
                              }
                              
                              }else{
                              if(i==time){
                              
                              chartData.push({
                                             date: d,
                                             //value: pre_v,
                                             value3: pre_v,
                                             value2: pre_v
                                             });
                              
                              }else{
                              chartData.push({
                                             date: d,
                                             value2: pre_v
                                             });
                              }
                              }
                              
                              }
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
                                                                        "balloonText": "预测值:[[value]]",
                                                                        "bullet": "round",
                                                                        "bulletBorderAlpha": 0.5,
                                                                        "lineAlpha":0.5,
                                                                        "bulletColor": "#FFFFFF",
                                                                        "hideBulletsCount": 50,
                                                                        "title": "red line",
                                                                        "valueField": "value",
                                                                        "useLineColorForBulletBorder": true,
                                                                        "dashLength":5
                                                                        },
                                                                        {
                                                                        "id": "g2",
                                                                        "balloonText": "预测值:[[value]]",
                                                                        "bullet": "round",
                                                                        "bulletBorderAlpha": 0.5,
                                                                        "bulletColor": "#FFFFFF",
                                                                        "hideBulletsCount": 50,
                                                                        "title": "red line2",
                                                                        "valueField": "value2",
                                                                        "useLineColorForBulletBorder": true,
                                                                        
                                                                        },
                                                                        {
                                                                        "id": "g3",
                                                                        "balloonText": "真实值:[[value]]",
                                                                        "bullet": "round",
                                                                        "bulletBorderAlpha": 0.5,
                                                                        "bulletColor": "#FFFFFF",
                                                                        "hideBulletsCount": 50,
                                                                        "title": "red line3",
                                                                        "valueField": "value3",
                                                                        "useLineColorForBulletBorder": true,
                                                                        
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
                                                             "dateFormats": [{period:'ss',format:'JJ:NN:SS'},
                                                                             {period:'mm',format:'JJ:NN'},
                                                                             {period:'hh',format:'JJ:NN'},
                                                                             {period:'DD',format:'MMM DD'},
                                                                             {period:'WW',format:'MMM DD'},
                                                                             {period:'MM',format:'MMM YYYY'},
                                                                             {period:'YYYY',format:'MMM YYYY'}],
                                                             "minPeriod": "ss",
                                                             "parseDates": true,
                                                             "axisColor": "#DADADA",
                                                             },
                                                             "export": {
                                                             "enabled": true
                                                             }
                                                             });
                              
                              
                              // this method is called when chart is first inited as we listen for "rendered" event
                              
                              
                              })
    
}