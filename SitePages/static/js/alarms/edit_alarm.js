$(document).ready(function(){
    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", $('#alarm-form').find('[name="csrfmiddlewaretoken"]')[0].value);
        }
    }
    });
    setTimeout(function(){
        var step = $('#alarm-form').find('[name="cur_step"]')[0].value;
        if(step === '2' || step === '3')
            loadDataFromForm();
        else if(step ==='4')
            loadAlarmConfirmation();
    }, 1);
});
function next_step() {
    var next_step = document.getElementsByName("next_step")[0];
    var current_step = document.getElementsByName("cur_step")[0];
    if (current_step.value === '3')
        submitAlarmActions();
    if (current_step.value === '4')
        next_step.value = 'post';
    else
        next_step.value = parseInt(current_step.value) + 1;
    document.getElementById('alarm-form').submit();
}

function prev_step() {
    var next_step = document.getElementsByName("next_step")[0];
    var current_step = document.getElementsByName("cur_step")[0];
    next_step.value = parseInt(current_step.value) - 1;
    if (current_step.value === '3'){
        submitAlarmActions();
    }
    document.getElementById('alarm-form').submit();
}

function submitAlarmActions(){
    var action_forms = $('.alarm-action-element');
    var i, j;
    var submit_form_handle = $('#alarm-form')[0];
    for(i = 0; i < action_forms.length; i++){
        var action_name = action_forms[i].getAttribute('name');
        while(submit_form_handle.children[action_name]){
            submit_form_handle.removeChild(submit_form_handle.children[action_name])
        }
        var action_type_list = action_forms[i].getElementsByTagName('select');
        var action_detail_list = action_forms[i].getElementsByTagName('input');
        for(j = 0; j < action_type_list.length; j++){
            if ((action_detail_list[j]).value === "") continue;
            var new_action = document.createElement('input');
            new_action.setAttribute('name', action_name);
            var new_action_value = encodeURIComponent('type=' + action_type_list[j].value
                                                        + '&detail=' + action_detail_list[j].value);
            new_action.setAttribute('value', new_action_value);
            submit_form_handle.appendChild(new_action);
        }
    }
}

$(function()
{
    $(document).on('click', '.btn-add', function(e)
    {
        e.preventDefault();
        var controlForm = $(this).parents('.controls form:first'),
            currentEntry = $(this).parents('.entry:first'),
            newEntry = $(currentEntry.clone()).appendTo(controlForm);
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
    $(document).on('change', '.alarm-form-element:input,select', function(){
        var this_name = $(this).attr('name');
        $('#alarm-form [name="'+this_name+'"]')[0].value = this.value;
    });
    $(document).on('click', '.alarm-form-element:input,select', function(){
        var this_name = $(this).attr('name');
        $('#alarm-form [name="'+this_name+'"]')[0].value = this.value;
    });
    $(document).on('change', '.alarm-action-element', function(){
        var this_name = $(this).attr('name');
        //$('#alarm-form [name="'+this_name+'"]')[0].value = $('#alarm-detail-wrapper [name="'+this_name+'"]')[0].value
    });
    $(document).on('click', '.machine-type-selector', function(){
        meter_table_handle.ajax.url("http://" + window.location.host
                                    + "/api/servers/"
                                    + this.value
                                    + '-list');
        meter_table_handle.ajax.reload();
    });

});

function loadDataFromForm(){
    var load_elements = $('.alarm-form-element');
    var index;
    for(index = 0; index < load_elements.length; index++){
        var element = load_elements[index];
        element.value = $('#alarm-form [name="'+element.getAttribute('name')+'"]')[0].value;
    }

    var actions = $('.alarm-action-element');
    for(index = 0; index < actions.length; index++){
        var action = actions[index];
        var action_list = $('#alarm-form [name="'+action.getAttribute('name')+'"]');
        var list_index, base_element;
        base_element = $('#alarm-detail-wrapper [name="'+action.getAttribute('name')+'"]')[0];

        for(list_index = 0; list_index < action_list.length; list_index++){
            // Match result [0: whole string  1: type_match(email|message)  2: detail_match]
            var regMatchTypeDetail = /type=(email|message|link)\&detail=(.*)/g;
            var match_result = regMatchTypeDetail.exec(decodeURIComponent(action_list[list_index].value));
            if(list_index === 0){
                base_element.getElementsByTagName('select')[0].value = match_result[1];
                base_element.getElementsByTagName('input')[0].value = match_result[2];
            }else{
                base_element.getElementsByClassName('btn-add')[0].click();
                var selects =  base_element.getElementsByTagName('select');
                selects[selects.length-1].value = match_result[1];
                var inputs = base_element.getElementsByTagName('input');
                inputs[inputs.length-1].value = match_result[2];
            }
        }
    }
}

function loadAlarmConfirmation(){
    var getAlarmFormElement = function(element_name){
        // function has a hidden argument. Should be treated as getAlarmFormElement(name, getAllElements)
        if(arguments[1] === true)
            return $('#alarm-form').find('[name="'+element_name+'"]');
        return $('#alarm-form').find('[name="'+element_name+'"]')[0];
    };
    var load_elements = $('.confirm-element');
    var index;
    for(index = 0; index < load_elements.length; index++){
        var element = load_elements[index];
        element.textContent = translate_name(getAlarmFormElement(element.getAttribute('name')).value, element.getAttribute('name'));
    }

    var actions = $('.confirm-action-element');
    for(index = 0; index < actions.length; index++){
        var action = actions[index];
        var action_list = getAlarmFormElement(action.getAttribute('name'), true);
        var list_index, base_element;
        base_element = $('#alarm-detail-wrapper').find('[name="'+action.getAttribute('name')+'"]')[0];

        for(list_index = 0; list_index < action_list.length; list_index++){
            // Match result [0: whole string  1: type_match(email|message)  2: detail_match]
            var regMatchTypeDetail = /type=(email|message|link)\&detail=(.*)/g;
            var match_result = regMatchTypeDetail.exec(decodeURIComponent(action_list[list_index].value));
            var append_html = document.createElement('p');
            append_html.textContent = translate_name(match_result[1], 'notification_type') + ": " + match_result[2];
            base_element.appendChild(append_html);
        }
    }

    $('.confirm-trigger-element')[0].innerHTML =
        ' 在    <b>' + getAlarmFormElement('period').value
        + '</b>    秒内指标的   <b>' + translate_name(getAlarmFormElement('statistic').value, 'statistic')
        + '</b>   <b>' + translate_name(getAlarmFormElement('comparison_operator').value, 'comparison_operator')
        + '</b>   <b>' + getAlarmFormElement('threshold').value
        + '</b>   时触发警报';
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getFormattedDate(dt)
{
    var yyyy = dt.getFullYear().toString();
   var MM = (dt.getMonth()+1).toString();
   var dd  = dt.getDate().toString();
   var hh = dt.getHours().toString();
   var mm = dt.getMinutes().toString();
   var ss = dt.getSeconds().toString();

   //Returns your formatted result
  return yyyy + '-' + (MM[1]?MM:"0"+MM[0]) + '-' + (dd[1]?dd:"0"+dd[0]) + 'T' + (hh[1]?hh:"0"+hh[0]) + ':' + (mm[1]?mm:"0"+mm[0]) + ':' + (ss[1]?ss:"0"+ss[0])+'Z';
}

function compareDate(a, b) {
    if (a.date < b.date)
        return -1;
    else if (a.date > b.date)
        return 1;
    else
        return 0;
}

