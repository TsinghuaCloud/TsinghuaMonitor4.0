from django.shortcuts import render
from django.conf import settings
from django.http import HttpRequest
from django.http import HttpResponse
import json
import time
import api_interface as ceilometer_api

def get_token(request, token_type=None):
    '''
    Get token through Keystone v2 api
    :param request:
    :return: token_id if success, <empty> if failed
    '''

    # tenant_name = request.GET['tenant_name']
    # username = request.GET['username']
    # password = request.GET['password']
    tenant_name = settings.OPENSTACK_TENANT_NAME
    username = settings.OPENSTACK_USERNAME_NAME
    password = settings.OPENSTACK_PASSWORD

    token = None
    if not (tenant_name and username and password):
        token = {'status': 'error',
                 'message': 'Login information not provided.'}
    else:
        token = ceilometer_api.get_token(tenant_name, username, password)
    if token_type == 'token':
        return token
    else:
        return HttpResponse(json.dumps(token), content_type='application/json')


def get_meters(request):
    # Deal wth parameters
    limit = 10 if 'length' not in request.GET else request.GET['length']
    skip = 0 if 'start' not in request.GET else request.GET['start']

    # TODO(pwwp):
    # Enhance error handling for token and result

    # TODO(pwwp):
    # Apply token management method instead of requesting one each time
    token = get_token(request, token_type='token')['token']
    request.session['token'] = token
    result = ceilometer_api.get_meters(token, limit, skip)

    _update_total_meters_count(request)

    if result['status'] == 'success':
        result['recordsTotal'] = request.session['total_meters_count']
        result['recordsFiltered'] = request.session['total_meters_count']
        return HttpResponse(json.dumps(result), content_type='application/json')
    else:
        return HttpResponse(json.dumps(result), content_type='application/json')


def _update_total_meters_count(request):
    '''
    Temporarily stores total_meters_count into session for speeding up queries
    Result expires after 180 seconds.
    :param request:
    :return: (int) total meters' count
    '''
    if request.session.has_key('total_meters_count'):
        refreshed_time = request.session['refreshed_time']
        delta = time.time() - refreshed_time
        if delta < 1000:
            print 'cache hit on _update_meters_count'
            return

    request.session['refreshed_time'] = time.time()
    meter_list = ceilometer_api.get_meters(request.session['token'], limit=0, skip=0)['data']
    request.session['total_meters_count'] = len(meter_list)
    return request.session['total_meters_count']


def get_samples(request):
    ''' Get samples of every meter through ceilometer_api
    In a correctly constructed request, all arrays are treated as meters, while
    all independent values are treated as url parameters.
    Example:
        /api/meters/get-samples?limit=10&cpu_util[]=computer001&cpu_util[]=computer002
                                &cpu[]=computer001&skip=2
    Resolved as:
        url_parameters = {'limit': 10, 'skip': 2}
        meters = {'cpu_util': ['computer001', 'computer002'], 'cpu':['computer001']}
    :param request:
    :return:
    '''
    # TODO(pwwp):
    # Apply token management method instead of requesting one each time
    token = get_token(request, token_type='token')['token']
    url_handle = _qdict_to_dict(request.GET)
    meters = {}
    kwargs = {}
    result = []
    for k in url_handle.iterkeys():
        if type(url_handle[k]) is list:
          meters[k] = url_handle[k]
        else:
          kwargs[k] = url_handle[k]
    for meter_name, resource_ids  in meters.iteritems():
        for i in range(len(resource_ids)):
            resource_id = resource_ids[i]
            result.append({
                'meter_name': meter_name,
                'resource_id': resource_id,
                'data': ceilometer_api.get_samples(token, meter_name,
                                                    resource_id=resource_id,
                                                    **kwargs)
                }
            )
    return HttpResponse(json.dumps({'data': result}), content_type='application/json')


def get_alarms(request):
    result = ceilometer_api.get_alarms(request.session['token'])
    pass


def get_resources(request):
    pass


def _qdict_to_dict(qdict):
    '''Convert a Django QueryDict to a Python dict.
    Referenced from: http://stackoverflow.com/questions/13349573/how-to-change-a-django-querydict-to-python-dict
    Single-value fields are put in directly, add for multi-value fields, a list
    of all values is stored at the field's key.

    :param qdict: <QueryDict>
    :return: (Dict) python dict
    '''
    return {k[:-2] if k[len(k)-2:] == '[]' else k: v if k[len(k)-2:] == '[]' else v[0]
            for k, v in qdict.lists()}