/**
 * Created by pwwpcheng on 2016/4/19.
 */


function scroll_to_id(id) {
    var offSet = 70;
    var obj = $('#' + id);
    if(obj.length){
      var offs = obj.offset();
      var targetOffset = offs.top - offSet;
      $('html,body').animate({ scrollTop: targetOffset }, 300);
    }
}

function refresh_alarm_count()
{
    $.getJSON('/api/alarms/alarm-count', function(data){
        $("[name=alarm-count-ok]").html(data.ok);
        $("[name=alarm-count-alarm]").html(data.alarm);
        $("[name=alarm-count-insufficient-data]").html(data.insufficient_data);
    })
        .fail(function(){
            $("[name=alarm-count-ok]").html('N/A');
            $("[name=alarm-count-alarm]").html('N/A');
            $("[name=alarm-count-insufficient-data]").html('N/A');
        })
}

refresh_alarm_count();
setInterval("refresh_alarm_count()", 10000);

