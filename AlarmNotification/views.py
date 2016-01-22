import copy
import json

from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail, BadHeaderError

ALARM_NOTIFICATION_BODY_PARAS = ['alarm_name', 'alarm_id', 'severity',
                                 'previous', 'current', 'action', 'reason',
                                 'request_id']

# Create your views here.
def notification(request):
    if request.method != 'POST':
        return HttpResponse("Request method should be POST",
                            content_type='text/plain')
    if not _check_validity(request):
        return HttpResponse("Illegal notification request!",
                            content_type='text/plain')

    kwargs = _sanitize_arguments(_request_method_to_dict(request.POST, False),
                                 ALARM_NOTIFICATION_BODY_PARAS)

    return HttpResponse("Success", content_type='text/plain')

def _notice_by_mail(email_args):
    try:
        #send_mail(subject, message, from_email, ['admin@example.com'])
        pass
    except BadHeaderError:
        return HttpResponse('Invalid header found.')

def _check_validity(request):
    '''
    Alarms might not be sent from a real client, but attackers.
    So we perform validity check for alarm notifications.
    :return: (bool) True: valid, False, invalid.
    '''
    return True

def _sanitize_arguments(filter, capabilities):
    f = copy.copy(filter)
    return {k: v for k, v in f.iteritems() if k in capabilities}

def _request_method_to_dict(qdict, seperate_args_and_list=True):
    '''
    Convert url parameters to seperate arrays and url variables
    :param qdict: (QueryDict) QueryDict element such as request.GET
    :return: (Dict) array: array elements in qdict
              (Dict) url_variables: other url parameters
          or: (Dict) array: all arguments and lists in request URL
    '''
    url_handle = _qdict_to_dict(qdict)
    arrays = {}
    url_variables = {}
    for k in url_handle.iterkeys():
        if type(url_handle[k]) is list:
            arrays[k] = url_handle[k]
        else:
            url_variables[k] = url_handle[k]

    if not seperate_args_and_list:
        return arrays.update(url_variables)
    return arrays, url_variables


def _qdict_to_dict(qdict):
    '''Convert a Django QueryDict to a Python dict.
    Referenced from: http://stackoverflow.com/questions/13349573/how-to-change-a-django-querydict-to-python-dict
    Single-value fields are put in directly, add for multi-value fields, a list
    of all values is stored at the field's key.
    :param qdict: <QueryDict>
    :return: (Dict) python dict
    '''
    return {k[:-2] if k[len(k) - 2:] == '[]' else k: v if k[len(k) - 2:] == '[]' else v[0]
            for k, v in qdict.lists()}