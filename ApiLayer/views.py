from django.shortcuts import render
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
    meter_list = ceilometer_api.get_meters(request.session['token'],limit=0, skip=0)['data']
    request.session['total_meters_count'] = len(meter_list)
    return request.session['total_meters_count']

def get_samples(request):
    meter_list = []
    pass

def get_alarms(request):
    result = ceilometer_api.get_alarms(request.session['token'])

    pass

def get_resources(request):
    pass
