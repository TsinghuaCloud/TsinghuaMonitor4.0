import json
import httplib
import urllib2

from django.conf import settings

def get_alarms(request):
    pass

def get_token(tenant_name=None, username=None, password=None):
    '''
    Since the only reason for utilizing Keystone endpoint is  to get a token,
    thus, we create a separate urllib2 connection for handling this function.
    :param tenant_name: (string) Name of the project
    :param username: (string)
    :param password: (string)
    :return: (Dictionary Object) Server's result
    '''
    request = urllib2.Request('http://%s:%s/v2.0/tokens' %
                              (settings.OPENSTACK_CONTROLLER_IP, settings.KEYSTONE_PORT))
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

def ceilometer_connection(base_url, method, header, url_parameters=None, body=None):
    '''
    :param url: (string)
    :param method: (string) [POST | GET | PUT | DELETE ]
    :param header: (JSON Object) headers for request
    :param url_parameters: (JSON Object)
    :param body: (JSON Object)
    :return: (JSON Object) Data fetched from ceilometer api

    '''
    extra_url = url_para_to_url(**url_parameters)
    conn = httplib.HTTPConnection('%s:%s' % (settings.OPENSTACK_CONTROLLER_IP, settings.CEILOMETER_PORT))
    req_header = header
    print req_header
    req_body = None if body is None else json.dumps(body)
    conn.request(method, '/v2/' + base_url + extra_url, headers=req_header, body=req_body)
    response = conn.getresponse()
    if response.status != 200:
        error = {}
        error['status'] = 'failed'
        error['code'] = response.status
        error['msg'] = response.reason
        error['data'] = ''
        return error
    else:
        data = {}
        data['status'] = 'success'
        data['data'] = json.loads(response.read())
        return data

def get_meters(token, limit=None, skip=None):
    '''
    Get meter list from ceilometer api
    :param token:
    :param limit: (int) number of items to get
    :param skip: (int) start fetching from the (skip)th item
    :return:
    '''
    request_header = {}
    request_header['X-Auth-Token'] = token
    request_header['Content-Type'] = 'application/json'
    url_parameters = {}
    if limit is not None:
        url_parameters['limit'] = limit
    if skip is not None:
        url_parameters['skip'] = skip
    request_body = {}
    return ceilometer_connection('meters', method='GET', header=request_header, url_parameters=url_parameters)

def kwargs_to_query(**kwargs):
    q = []
    q.append({'field': k, 'value': v}
             for k, v in kwargs.iteritems())

def url_para_to_url(**kwargs):
    '''
    Convert query parameters into url string
    :param kwargs: (Dict) query criteria, e.g. limit, skip, resource_id, etc.
    :return: url: (String) converted
    '''
    if not kwargs:
        return ''
    else:
        para_url = ''.join(('{}={}&'.format(key, val)
                        for key, val in kwargs.iteritems()))
        all_url = '?' + para_url
        return all_url[:-1]
