from django.shortcuts import render
from django.http import HttpRequest
from django.http import HttpResponse
from django.conf import settings
import json
import httplib
import urllib2


def get_token(request):
    '''
    Get token through Keystone v2 api
    :param request:
    :return: token_id if success, <empty> if failed
    '''
    tenant_name = request.GET['tenant_name']
    username = request.GET['username']
    password = request.GET['password']
    token = None
    if not (tenant_name and username and password):
        token = {'status': 'error',
                 'message': 'Login information not provided.'}
    else:
        token = _get_token(tenant_name, username, password)
    return HttpResponse(json.dumps(token), content_type='application/json')


def get_meters(request):
    result = _get_meters(request.session['token'])
    if result['status'] == 'success':
        return HttpResponse(json.dumps(result['data']), content_type='application/json')


def get_alarms(request):
    pass


def get_resources(request):
    pass


def _get_token(tenant_name=None, username=None, password=None):
    request = urllib2.Request('http://%s:%s/v2.0/tokens' % (settings.OPENSTACK_CONTROLLER_IP, settings.KEYSTONE_PORT))
    request.add_header('Content-Type', 'application/json')
    request.add_data('{"auth":{"tenantName": "%s","passwordCredentials":{"username": "%s","password": "%s"}}}' % (
        tenant_name, username, password))
    try:
        handle = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        return {'status': 'failed',
                'reason': 'HTTPCode: %s, Message: %s' % (e.code, e.msg)}
    except urllib2.URLError as e:
        return {'status': 'failed',
                'reason': e.reason}

    token = json.loads(handle.read())['access']['token']['id']
    return {'status': 'success',
            'token': token}


def _ceilometer_connection(url, method, header, url_parameters=None, body=None):
    extra_url = _url_para_to_url(**url_parameters)
    conn = httplib.HTTPConnection('%s:%s' % (settings.OPENSTACK_CONTROLLER_IP, settings.CEILOMETER_PORT))
    req_header = header
    req_body = json.dumps(body)
    conn.request(method, '/v2/' + url + extra_url, headers=req_header, body=json.dumps(req_body))
    response = conn.getresponse()
    if response.status != 200:
        error = {}
        print 'Get user info failed'
        error['status'] = 'failed'
        error['code'] = response.status
        error['msg'] = json.loads(response.read())
        error['data'] = ''
        return error
    else:
        print 'Get user info succeeded'
        data = {}
        data['status'] = 'success'
        data['data'] = json.loads(response.read())
        return data


def _get_meters(token, limit=None, skip=None):
    request_header = {}
    request_header['X-Auth-Token'] = token
    request_header['Content-Type'] = 'application/json'
    url_parameters = {}
    if limit is not None:
        url_parameters['limit'] = limit
    if skip is not None:
        url_parameters['skip'] = skip
    request_body = {}
    return _ceilometer_connection('meters', 'GET', request_header, url_parameters=url_parameters)


def _kwargs_to_query(**kwargs):
    q = []
    q.append({'field': k, 'value': v}
             for k, v in kwargs.iteritems())


def _url_para_to_url(**kwargs):
    '''
    Convert query parameters into url string
    :param kwargs: (Dict) query criteria, e.g. limit, skip, resource_id, etc.
    :return: url: (String) converted
    '''
    if not kwargs:
        return ''

    else:
        url = '?'.join(('{}={}&'.format(key, val)
                        for key, val in kwargs.iteritems()))
        return url[:-1]
