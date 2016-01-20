import json
import httplib
import urllib2

from django.conf import settings

def get_alarms(token, **kwargs):
    request_header = {'X-Auth-Token': token,
                      'Content-Type': 'application/json'}
    url_para_obj = _kwargs_to_url_parameter_object(**kwargs)
    return ceilometer_connection('alarms', method='GET', header=request_header, url_parameters=url_para_obj)

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
    extra_url = _url_para_to_url(**url_parameters)
    conn = httplib.HTTPConnection('%s:%s' % (settings.OPENSTACK_CONTROLLER_IP, settings.CEILOMETER_PORT))
    req_header = header
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

def get_meters(token, **kwargs):
    '''
    Get meter list from ceilometer api
    :param token: (string) token issued by Keystone
    :param kwargs: (Dict) filter criteria
    :return:
    '''
    request_header = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    url_para_obj = _kwargs_to_url_parameter_object(**kwargs)
    return ceilometer_connection('meters', method='GET', header=request_header, url_parameters=url_para_obj)

def get_resources(token, **kwargs):
    request_header = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    url_para_obj = _kwargs_to_url_parameter_object(**kwargs)
    return ceilometer_connection('resources', method='GET', header=request_header, url_parameters=url_para_obj)

def get_samples(token, meter_name, **kwargs):
    '''
    Get samples of a selected meter
    :param token: (string) token issued by Keystone
    :param meter_name: (string)
    :param kwargs: (Dict) Query criteria,
                    e.g. ['meter_name': <meter_name>, 'resource_id': <resource_id>]
    :return:
    '''
    request_header = {}
    request_header['X-Auth-Token'] = token
    request_header['Content-Type'] = 'application/json'
    url_para_obj = _kwargs_to_url_parameter_object(**kwargs)
    return ceilometer_connection('meters/' + meter_name,
                                 method='GET',
                                 header=request_header,
                                 url_parameters=url_para_obj)['data']

def post_alarm(token, **kwargs):
    # Pack related kwargs into alarm_dictionary
    new_alarm = {}
    request_header = {'X-Auth-Token': token, 'Content-Type': 'application/json'}

    # Mandatory arguments for packing a new alarm
    try:
        new_alarm['name'] = kwargs['name']
        new_alarm['meter_name'] = kwargs['meter_name']
        new_alarm['threshold'] = kwargs['threshold']
    except KeyError, e:
        return {'status': 'error',
                'msg': 'Key: ' + str(e) + ' not provided!'}

    # Pack other optional arguments
    new_alarm['alarm_actions'] = kwargs.get('alarm_actions', [])
    new_alarm['ok_actions'] = kwargs.get('ok_actions', [])
    new_alarm['insufficient_data_actions'] = kwargs.get('insufficient_data_actions', [])
    new_alarm['type'] = kwargs.get('type', 'threshold')
    new_alarm['period'] = kwargs.get('evaluation_period', 60)
    new_alarm['query'] = kwargs.get('q', {})
    new_alarm['repeat_actions'] = kwargs.get('repeat_actions', 'False')
    new_alarm['severity'] = kwargs.get('severity', 'low')
    new_alarm['enabled'] = kwargs.get('enabled', 'True')
    new_alarm['statistic'] = kwargs.get('statistic', 'avg')
    new_alarm['comparison_operator'] = kwargs.get('comparison_operator', 'ge')

    return ceilometer_connection(base_url='alarms',
                                 method='POST',
                                 header=request_header,
                                 body=new_alarm)['data']

def _kwargs_to_url_parameter_object(**kwargs):
    '''
    Convert kwargs into q (list(Query))
    :param kwargs:
    :return: (Dict) Filter rules for the data to be returned
    Example:
        kwargs = {'resource_id': 'computer001'}
    '''
    url_parameters_object = {}
    if 'limit' in kwargs.iterkeys():
        url_parameters_object['limit'] = kwargs.pop('limit')
    if 'skip' in kwargs.iterkeys():
        url_parameters_object['skip'] = kwargs.pop('skip')
    q = []
    for k, v in kwargs.iteritems():
        q.append({'field': k, 'value': v})
    url_parameters_object['q'] = q
    return url_parameters_object

def _url_para_to_url(**kwargs):
    '''
    Convert query parameters into url string,
    limit & skip are directly written into url_parameters.
    Other parameters are reformatted into {'field': <key>, 'value': <value>}
    :param kwargs: (Dict) query criteria, e.g. limit, skip, resource_id, meter_name etc.
    :return: url: (String) converted url
    '''
    if not kwargs:
        return ''
    else:
        complete_url = ''
        if kwargs.get('limit'):
            complete_url = complete_url + 'limit=' + str(kwargs.pop('limit')) + '&'
        if kwargs.get('skip'):
            complete_url = complete_url + 'skip=' +str(kwargs.pop('skip')) + '&'
        if kwargs.get('q'):
            q = kwargs.pop('q')
            for item in q:
                complete_url = complete_url + 'q.field=%s&q.value=%s&'\
                                              %(item['field'],  item['value'])
        complete_url = '?' + complete_url
        return complete_url[:-1]

        # all_url = ''
        # if kwargs.get('limit'):
        #     all_url
        # para_url = ''.join(('{}={}&'.()
        #                 for key, val in kwargs.iteritems()))
        # all_url = '?' + para_url