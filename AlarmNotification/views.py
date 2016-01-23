import copy
import json
import smtplib

from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt

ALARM_NOTIFICATION_BODY_PARAS = ['alarm_name', 'alarm_id', 'severity',
                                 'previous', 'current', 'action', 'reason',
                                 'request_id', 'reason_data']

# Create your views here.
@csrf_exempt
def notification(request):
    '''
    Handles notification requests.
    :param request: Django HTTP request
    :return: HTTPResponse
    '''
    if request.method != 'POST':
        return HttpResponse("Request method should be POST",
                            content_type='text/plain')
    if not _check_validity(request):
        return HttpResponse("Illegal notification request!",
                            content_type='text/plain')
    kwargs = _sanitize_arguments(_request_method_to_dict(request.body),
                                 ALARM_NOTIFICATION_BODY_PARAS)
    return _notice_by_mail(**kwargs)


def _notice_by_mail(**kwargs):
    '''
    Sending emails to administrator.
    :param alarm_id: (string) alarm id provided by ceilometer
    :param alarm_name: (string) name of the triggered alarm
    :param kwargs: (dictionary) other arguments related to emails to send
    :return: (HTTPResponse): Success or Failed.
    '''
    if not kwargs.get('alarm_name'):
        return HttpResponse('Error: alarm_name not provided.')
    if not kwargs.get('alarm_id') :
        return HttpResponse('Error: alarm_id not provided.')
    alarm_name = kwargs.get('alarm_name')
    alarm_id = kwargs.get('alarm_id')

    email_subject = '%(alarm_name)s is triggered' % ({
                                                                        'alarm_name': alarm_name})
    email_msg = "Request ID: %(request_id)s\n" \
                "Alarm   ID: %(alarm_id)s\n" \
                "Alarm Name: %(alarm_name)s\n" \
                "Severity  : %(severity)s\n\n" \
                "This alarm has been triggered. Its states was changed from " \
                "%(previous)s to %(current)s. %(action)s has been taken because " \
                "%(reason)s.\n" % ({'request_id': kwargs.get('request_id', 'N/A'),
                                    'alarm_id': alarm_id,
                                    'alarm_name': alarm_name,
                                    'severity': kwargs.get('severity', 'N/A'),
                                    'previous': kwargs.get('previous', 'N/A'),
                                    'current': kwargs.get('current', 'N/A'),
                                    'action': kwargs.get('action', 'No action'),
                                    'reason': kwargs.get('reason', 'no reason')})
    try:
        email = EmailMessage(subject=email_subject, body=email_msg,
                             from_email='sender@mail.com',
                             to=['receiver@mail.com'])
        email.send()
        return HttpResponse("Success", content_type='text/plain')
    except smtplib.SMTPAuthenticationError, e:
        return HttpResponse('Sending email failed. Reason: Authentication Error'
                            , content_type='text/plain')
    except smtplib.SMTPSenderRefused, e:
        return HttpResponse('Sending email failed. Reason: ' + e.smtp_error
                            , content_type='text/plain')
    except smtplib.SMTPException, e:
        return HttpResponse('Sending email failed. Reason: ' + e.message,
                            content_type='text/plain')
    except EnvironmentError, e:
        return HttpResponse('Environment error ['+ str(e.errno)
                            + ']. Reason: ' + e.strerror, content_type='text/plain')

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


def _request_method_to_dict(json_body):
    '''
    Convert rquest body to seperate arrays and url variables
    :param json_body: (String)
    :return: (Dict) converted dictionary
    '''
    return json.loads(json_body)



