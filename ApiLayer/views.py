from django.shortcuts import render
from django.conf import settings

from django.views.decorators.csrf import csrf_protect
from django.http import HttpRequest
from django.http import HttpResponse
import json
import time
import api_interface as ceilometer_api
import classdef


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
    #url_para_obj = _kwargs_to_url_parameter_object(**kwargs)
    return ceilometer_api.nova_connection('/os-hypervisors/statistics', method='GET', header=request_header)

def get_allVMList(token):
    request_header = {}
    request_header['X-Auth-Token'] = token
    request_header['Content-Type'] = 'application/json'
    #url_para_obj = _kwargs_to_url_parameter_object(**kwargs)
    tenantList=ceilometer_api.keystone_connection('tenants', method='GET', header=request_header)
    PM_vmInfo={}
    for tenantIdinfo in tenantList['data']['tenants']:
        serverList=ceilometer_api.nova_connection('/servers/detail', method='GET', header=request_header,tenantId=tenantIdinfo['id'])
        print tenantIdinfo['name']
        print serverList
        if serverList['status']=="success":
            for single in serverList['data']['servers']:
                PM_name=single['OS-EXT-SRV-ATTR:host']
                VM_name=single['name']
                if PM_vmInfo.has_key(PM_name)==False:
                    PM_vmInfo[PM_name]=[]
                PM_vmInfo[PM_name].append(VM_name)
    return PM_vmInfo

def get_PmInfo(token):

    request_header = {}
    request_header['X-Auth-Token'] = token
    request_header['Content-Type'] = 'application/json'
    #url_para_obj = _kwargs_to_url_parameter_object(**kwargs)
    allInfo=[]
    serverList=ceilometer_api.nova_connection('/os-hypervisors', method='GET', header=request_header)
    for single in  serverList['data']['hypervisors'] :
        id=single['id']
        info=ceilometer_api.nova_connection('/os-hypervisors/'+str(id), method='GET', header=request_header)['data']['hypervisor']
        singleInfo={}
        singleInfo['id']=id
        singleInfo['name']=single['hypervisor_hostname']
        singleInfo['vcpus_used']=info['vcpus_used']
        singleInfo['local_gb_used']=info['local_gb_used']
        singleInfo['memory_mb']=info['memory_mb']
        singleInfo['vcpus']=info['vcpus']
        singleInfo['memory_mb_used']=info['memory_mb_used']
        singleInfo['local_gb']=info['local_gb']
        allInfo.append(singleInfo)
    return allInfo
        


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
    kwargs = {}
    if request.method == 'GET':
        arrays, kwargs = _request_GET_to_dict(request.GET)
        # Deal with special parameters in
        kwargs = _rename_parameters(kwargs)
    elif request.method == 'POST':
        # POST method at /api/meter-list is triggered by datatables.
        # So I just deal with some special parameters in this POST request.
        args = json.loads(request.body)
        kwargs['limit'] = 0 if 'length' not in args else args['length']
        kwargs['skip'] = 0 if 'start' not in args else args['start']

        try:
            if 'q' in args:
                for query_item in args['q']:
                    kwargs[query_item['field']] = query_item['value']
        except KeyError:
            print 'Illegal query object in meter-list'
            print 'Query_object: ' + json.dumps(args['q'])

    result = ceilometer_api.get_meters(token, **kwargs)

    _update_total_meters_count(request, kwargs)

    if result['status'] == 'success':
        result['recordsTotal'] = request.session['total_meters_count']
        result['recordsFiltered'] = request.session['total_meters_count']
        return HttpResponse(json.dumps(result), content_type='application/json')
    else:
        return HttpResponse(json.dumps(result), content_type='application/json')


def _update_total_meters_count(request, criteria):
    '''
    Temporarily stores total_meters_count into session for speeding up queries
    Result expires after 1000 seconds or filter criteria has changed.
    :param request: Django request object
            criteria:
    :return: (int) total meters' count
    '''
    if 'limit' in criteria:
        criteria.pop('limit')
    if 'skip' in criteria:
        criteria.pop('skip')
    print criteria
    if request.session.has_key('total_meters_count'):
        refreshed_time = request.session['refreshed_time']
        delta = time.time() - refreshed_time
        print request.session['criteria_hash']
        if delta < 1000 and request.session['criteria_hash'] == criteria:
            return

    print 'cache miss'
    request.session['refreshed_time'] = time.time()
    request.session['criteria_hash'] = criteria

    # TODO: Error handling for hashing meter_list
    meter_list = ceilometer_api.get_meters(request.session['token'], **criteria)['data']
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
    result = ceilometer_api.get_alarms(request.session['token'])
    pass


def get_resources(request):
    pass

def _rename_parameters(args_dict):
    assert isinstance(args_dict, dict)
    if 'length' in args_dict:
        args_dict['limit'] = args_dict.pop('length')
    if 'start' in args_dict:
        args_dict['skip'] = args_dict.pop('start')
    return args_dict

def _request_GET_to_dict(qdict):
    '''
    Convert url parameters to seperate arrays and url variables
    :param qdict: (QueryDict) QueryDict element such as request.GET
    :return: (Dict)array: array elements in qdict
              (Dict)url_variables: other url parameters
    '''
    url_handle = _qdict_to_dict(qdict)
    arrays = {}
    url_variables = {}
    for k in url_handle.iterkeys():
        if type(url_handle[k]) is list:
            arrays[k] = url_handle[k]
        else:
            url_variables[k] = url_handle[k]
    print arrays, url_variables
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