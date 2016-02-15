import json
import time
import copy
import classdef

from django.conf import settings
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

import CommonMethods.BaseMethods as BaseMethods
import api_interface as ceilometer_api
import capabilities
import paramiko  #install it follow link http://www.it165.net/pro/html/201503/36363.html
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


def get_allPmStatistics(token):
    request_header = {}
    request_header['X-Auth-Token'] = token
    request_header['Content-Type'] = 'application/json'
    # url_para_obj = _kwargs_to_url_parameter_object(**kwargs)
    return ceilometer_api.nova_connection('/os-hypervisors/statistics', method='GET', header=request_header)


def get_allVMList(token):
    request_header = {}
    request_header['X-Auth-Token'] = token
    request_header['Content-Type'] = 'application/json'
    PM_vmInfo = {}
    '''
    url_para_obj = _kwargs_to_url_parameter_object(**kwargs)
    tenantList=ceilometer_api.keystone_connection('tenants', method='GET', header=request_header)
    print tenantList
    
    for tenantIdinfo in tenantList['data']['tenants']:
    '''
    serverList = ceilometer_api.nova_connection('/servers/detail', method='GET', header=request_header)
    # print tenantIdinfo['name']
    #print serverList
    if serverList['status'] == "success":
        for single in serverList['data']['servers']:
            PM_name = single['OS-EXT-SRV-ATTR:host']
            if PM_vmInfo.has_key(PM_name) == False:
                PM_vmInfo[PM_name] = []
            temp={}
            temp['name']=single['name']
            temp['id']=single['id']
            temp['instance_name']=single['OS-EXT-SRV-ATTR:instance_name']
            PM_vmInfo[PM_name].append(temp)
            
    return PM_vmInfo


def get_PmInfo(token):
    request_header = {}
    request_header['X-Auth-Token'] = token
    request_header['Content-Type'] = 'application/json'
    # url_para_obj = _kwargs_to_url_parameter_object(**kwargs)
    allInfo = []
    serverList = ceilometer_api.nova_connection('/os-hypervisors', method='GET', header=request_header)
    #print serverList
    for single in serverList['data']['hypervisors']:
        id = single['id']
        info = \
            ceilometer_api.nova_connection('/os-hypervisors/' + str(id), method='GET', header=request_header)['data'][
                'hypervisor']
        singleInfo = {}
        singleInfo['id'] = id
        singleInfo['name'] = single['hypervisor_hostname']
        singleInfo['vcpus_used'] = info['vcpus_used']
        singleInfo['local_gb_used'] = info['local_gb_used']
        singleInfo['memory_mb'] = info['memory_mb']
        singleInfo['vcpus'] = info['vcpus']
        singleInfo['memory_mb_used'] = info['memory_mb_used']
        singleInfo['local_gb'] = info['local_gb']
        allInfo.append(singleInfo)
    return allInfo

@csrf_protect
def post_alarms(request):
    '''
    Post new alarms through ceilometer API.
    Notice: This api is protected by csrf_protect. 'X-csrf-token' should be added to request headers .
    :param request:
    :return: (JSON) Result of posting new alarm.
                     Return state: 'success' or 'error'
    '''
    token = get_token(request, token_type='token')['token']
    request.session['token'] = token
    if request.method == 'POST':
        kwargs = BaseMethods.sanitize_arguments(_request_GET_to_dict(request.POST, False),
                                     capabilities.post_alarm_capabilities)
        return ceilometer_api.post_alarm(token, **kwargs)
    else:
        return HttpResponse(json.dumps({'status': 'error',
                                        'error_msg': 'Request method should be POST.'}),
                            content_type='application/json')

@csrf_protect
def get_meters(request):
    '''

    :param request:
    :return:
    '''
    # TODO(pwwp):
    # Enhance error handling for token and result

    # TODO(pwwp):
    # Apply token management method instead of requesting one each time
    token = get_token(request, token_type='token')['token']
    request.session['token'] = token
    arrays = {}
    filters = {}
    if request.method == 'GET':
        arrays, filters = _request_GET_to_dict(request.GET)
        # Deal with special parameters in
        filters = _rename_parameters(filters)
    elif request.method == 'POST':
        # POST method at /api/meter-list is triggered by datatables.
        # So I just deal with some special parameters in this POST request.
        args = json.loads(request.body)
        filters['limit'] = 0 if 'length' not in args else args['length']
        filters['skip'] = 0 if 'start' not in args else args['start']

        # argument 'q' is designed for supporting complex query, which have not
        # been implement on the back-end side. Thus, we unpack 'q' into
        # simple query form.
        # Example: q: {'resource_id': 'computer001'}
        # Output:  filter['resource_id'] = 'computer001'
        try:
            if 'q' in args:
                for query_item in args['q']:
                    filters[query_item['field']] = query_item['value']
        except KeyError, e:
            return _report_error('KeyError', e)

    filters = BaseMethods.sanitize_arguments(filters, capabilities.meter_list_capabilities)
    result = ceilometer_api.get_meters(token, **filters)

    _update_total_meters_count(request, filters)

    if result['status'] == 'success':
        result['recordsTotal'] = request.session['total_meters_count']
        result['recordsFiltered'] = request.session['total_meters_count']
        return HttpResponse(json.dumps(result), content_type='application/json')
    else:
        return HttpResponse(json.dumps(result), content_type='application/json')


def _update_total_meters_count(request, filters):
    '''
    Temporarily stores total_meters_count into session for speeding up queries
    Result expires after 1000 seconds or filter criteria has changed.
    :param request: Django request object
            criteria:
    :return: (int) total meters' count
    '''
    if 'limit' in filters:
        filters.pop('limit')
    if 'skip' in filters:
        filters.pop('skip')
    if request.session.has_key('total_meters_count'):
        refreshed_time = request.session['refreshed_time']
        delta = time.time() - refreshed_time
        if delta < 1000 and request.session['criteria_hash'] == filters:
            return

    request.session['refreshed_time'] = time.time()
    request.session['criteria_hash'] = filters

    # TODO: Error handling for hashing meter_list
    # Resend the request purged of limit and skip to get total record number
    meter_list_request = ceilometer_api.get_meters(request.session['token'], **filters)
    if meter_list_request['status'] == 'success':
        request.session['total_meters_count'] = len(meter_list_request['data'])
    else:
        request.session['total_meters_count'] = 0
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
    meters, kwargs = _request_GET_to_dict(request.GET)
    result = []
    for meter_name, resource_ids in meters.iteritems():
        for i in range(len(resource_ids)):
            resource_id = resource_ids[i]
            result.append({
                'meter_name': meter_name,
                'resource_id': resource_id,
                'data': ceilometer_api.get_samples(token, meter_name,
                                                   resource_id=resource_id,
                                                   **kwargs)
            })
    return HttpResponse(json.dumps({'data': result}), content_type='application/json')

def get_alarms(request):
    '''
    Fetch alarms for a query.
    Filter options supported by Ceilometer includes:
        name: alarm name, user: user_id, project: project_id, meter: meter_name
        enabled, state, alarm_id, alarm_type
    Additional filter enabled by editing pymongo_base:
        resource: resource_id
    :param request:
    :return:
    '''
    arrays, filters = _request_GET_to_dict(request.GET)
    filters = BaseMethods.sanitize_arguments(filters, capabilities.alarm_list_capabilities)
    result = ceilometer_api.get_alarms(request.session['token'], **filters)
    return HttpResponse(json.dumps(result), content_type='application/json')


def get_resources(request):
    arrays, filters = _request_GET_to_dict(request.GET)
    filters = BaseMethods.sanitize_arguments(filters, capabilities.resource_list_capabilities)
    result = ceilometer_api.get_resources(request.session['token'], **filters)
    return HttpResponse(json.dumps(result), content_type='application/json')

def _rename_parameters(args_dict):
    '''
    In some cases, arguments passed from the front side doesn't meet with ceilometer-ap
    arguments. This function changes those names into accepted arguments.
    :param args_dict: dictionary to perform changes
    :return: (Dict) dict: dictionary after changing
    '''
    dict = copy.copy(args_dict)
    if 'length' in dict:
        dict['limit'] = dict.pop('length')
    if 'start' in dict:
        dict['skip'] = dict.pop('start')
    return dict


def _request_GET_to_dict(qdict, seperate_args_and_list=True):
    '''
    Convert url parameters to seperate arrays and url variables
    :param qdict: (QueryDict) QueryDict element such as request.GET
    :return: (Dict) array: array elements in qdict
              (Dict) url_variables: other url parameters
          or: (Dict) array: all arguments and lists in request URL
    '''
    url_handle = BaseMethods.qdict_to_dict(qdict)
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


def _report_error(error_type, error_msg):
    '''
    Report error data
    :param error_type: (string) Error type
    :param error_msg: (string) Error message
    :return: HTTPResponse Object
    '''
    error_json = {'status': 'error',
                  'error_type': error_type,
                  'error_msg': error_msg
                  }
    return HttpResponse(json.dumps(error_json), content_type='application/json')

def getTopoInfo(request):  
    #paramiko.util.log_to_file('paramiko.log')          
    s=paramiko.SSHClient()                 
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())          
    s.connect(hostname = settings.TOPO_SERVER, port=settings.TOPO_SERVER_PORT ,username=settings.TOPO_SERVER_USER, password=settings.TOPO_SERVER_PASSWD)          
    stdin,stdout,stderr=s.exec_command('cat '+settings.TOPO_FILE)          
    res=stdout.read()  
    error_json = {'status': 'error',
                  'error_type': 'error_type',
                  'error_msg': 'error_msg'
                  }
    s.close()
    return HttpResponse(json.dumps({'data': res.replace('\n','').replace(' ','')}), content_type='application/json')
    #return HttpResponse(json.dumps({'data': error_json}), content_type='application/json')
