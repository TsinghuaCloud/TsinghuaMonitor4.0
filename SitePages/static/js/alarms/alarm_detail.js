/**
 * Created by pwwpcheng on 2016/2/25.
 */

$(function(){
    setTimeout(function () {
        translate_alarm_detail();
    }, 1);
});

function translate_alarm_detail(){
    var elements = $('.detail-translate-element');
    var i;
    for(i = 0; i < elements.length; i++){
        elements[i].innerHTML = translate_name(elements[i].innerHTML,elements[i].getAttribute('name'))
    }
}