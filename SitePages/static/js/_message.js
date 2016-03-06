/**
 * Created by pwwpcheng on 2016/3/4.
 */

function add_message(message_tag, message_content){
    // Fetch message template
    var message_obj = $($('#message-template').html());

    // Process alert type
    if(message_tag === 'success')
        message_obj.addClass('alert-success');
    else if (message_tag === 'warning')
        message_obj.addClass('alert-warning');
    else if (message_tag === 'info')
        message_obj.addClass('alert-info');
    else if (message_tag === 'error')
        message_obj.addClass('alert-danger');

    // Add message tag
    message_obj.find('strong').html(message_tag);

    // Add message content
    message_obj.find('p:eq(1)').html(message_content);

    // Add message to page
    $('#message-div').append(message_obj);
}
