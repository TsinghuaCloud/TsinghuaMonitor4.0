import copy
import json
import time
import re

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_protect

from AlarmNotification.capabilities import NOTIFICATION_CAPABILITIES as NOTIFICATION_CAPABILITIES
from ApiLayer.base import capabilities
from ApiLayer.ceilometer import api as ceilometer_api
from ApiLayer.keystone import api as keystone_api
from ApiLayer.nova import api as nova_api
from ApiLayer.nova.connection import nova_connection  # TODO(pwwp): remove this import statement
from Common.BaseMethods import sanitize_arguments, qdict_to_dict, string_to_bool
from Common import decorators
from Common import error_base as err

from ApiLayer.prediction import api as prediction_api
from SitePages.models import VM
# Below is still in test phase
from ApiLayer.ceilometer.new_api import CeilometerApi

import paramiko  # install it from the following link http://www.it165.net/pro/html/201503/36363.html

def get_allPmStatistics(token):
    project_id = token.project['id']
    request_header = {}
    request_header['X-Auth-Token'] = token.id
    request_header['Content-Type'] = 'application/json'
    # url_para_obj = _kwargs_to_url_parameter_object(**kwargs)
    return nova_api.nova_connection(project_id, '/os-hypervisors/statistics', method='GET', header=request_header)


def get_allVMList(token):
    project_id = token.project['id']
    request_header = {}
    request_header['X-Auth-Token'] = token.id
    request_header['Content-Type'] = 'application/json'
    PM_vmInfo = {}
    '''
    url_para_obj = _kwargs_to_url_parameter_object(**kwargs)
    tenantList=ceilometer_api.keystone_connection('tenants', method='GET', header=request_header)
    print tenantList
    
    for tenantIdinfo in tenantList['data']['tenants']:
    '''
    serverList = nova_connection(project_id, '/servers/detail', method='GET', header=request_header)
    # print tenantIdinfo['name']
    # print serverList
    if serverList['status'] == "success":
        for single in serverList['data']['servers']:
            PM_name = single['OS-EXT-SRV-ATTR:host']
            if PM_vmInfo.has_key(PM_name) == False:
                PM_vmInfo[PM_name] = []
            temp = {}
            temp['name'] = single['name']
            temp['id'] = single['id']
            temp['instance_name'] = single['OS-EXT-SRV-ATTR:instance_name']
            PM_vmInfo[PM_name].append(temp)

    return PM_vmInfo


def get_VMonPM(token):
    project_id = token.project['id']
    request_header = {}
    request_header['X-Auth-Token'] = token.id
    request_header['Content-Type'] = 'application/json'
    vm_opInfo = {}
    pmList = nova_connection(project_id, '/servers/detail', method='GET', header=request_header)
    #print pmList
    if pmList['status'] == "success":
        for single in pmList['data']['servers']:
            pm_name = single['OS-EXT-SRV-ATTR:hypervisor_hostname']
            if vm_opInfo.has_key(pm_name) == False:
                vm_opInfo[pm_name] = []
            temp = {}
            temp['name'] = single['name']
            temp['id'] = single['id']
            if (single['addresses']=={}):
                temp['ip']=""
                vm_opInfo[pm_name].append(temp)
                continue
            temp1 = single['addresses']['tenant-net']
            temp['ip'] = temp1[0]['addr']
            vm_opInfo[pm_name].append(temp)
            #print pm_name
            #print vm_opInfo[pm_name]
    allInfo = {}
    serList = nova_connection(project_id, '/os-hypervisors', method='GET', header=request_header)
    #print serList
    for single in serList['data']['hypervisors']:
        id = single['id']
        info = \
            nova_connection(project_id, '/os-hypervisors/' + str(id), method='GET', header=request_header)['data'][
                'hypervisor']
        host_name = info['hypervisor_hostname']
        host_ip = info['host_ip']
        ip_end = host_ip.split('.')[3]
        #print ip_end
        if vm_opInfo.has_key(host_name)==False:
            continue
        if allInfo.has_key(ip_end) == False:
            allInfo[ip_end] = []
        allInfo[ip_end].append(vm_opInfo[host_name])
        #print host_ip
        #print allInfo[host_ip]
    # return allInfo for append in the formation.txt for VM info
    return allInfo


def get_PmInfo(token):
    request_header = {}
    request_header['X-Auth-Token'] = token.id
    request_header['Content-Type'] = 'application/json'
    # url_para_obj = _kwargs_to_url_parameter_object(**kwargs)
    allInfo = []
    project_id = token.project['id']
    serverList = nova_connection(project_id, '/os-hypervisors', method='GET', header=request_header)
    # print serverList
    for single in serverList['data']['hypervisors']:
        id = single['id']
        info = \
            nova_connection(project_id, '/os-hypervisors/' + str(id), method='GET', header=request_header)['data'][
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


@decorators.login_required
@csrf_protect
def post_alarm(request):
    '''
    Post new alarms through ceilometer API.
    Notice: This api is protected by csrf_protect. 'X-csrf-token' should be added to request headers .
    :param request:
    :return: (JSON) Result of posting new alarm.
                     Return state: 'success' or 'error'
    '''
    token_id = request.session['token'].id
    new_ceilometer_api = CeilometerApi(token_id)

    if request.method == 'POST':
        kwargs = sanitize_arguments(_request_GET_to_dict(request.POST, False),
                                    capabilities.ALARM_CAPABILITIES)
        q = []
        try:
            q[0] = {}
            q[0]['value'] = kwargs.pop('resource_id')
            q[0]['field'] = 'resource_id'
            q[0]['op'] = 'eq'
        except NameError:
            q[0] = {}
        finally:
            kwargs['q'] = q
            result = {}
            try:
                new_ceilometer_api.post_threshold_alarm(**kwargs)
                result['status'] = 'success'
                return HttpResponse(json.dumps(result), content_type='application/json')
            except (err.ClientSideError, err.ServerSideError), e:
                return _report_error(e.message)
    else:
        return HttpResponse(json.dumps({'status': 'error',
                                        'error_msg': 'Request method should be POST.'}),
                            content_type='application/json')


@decorators.login_required
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
    token_id = request.session['token'].id
    new_ceilometer_api = CeilometerApi(token_id)
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
            # Currently malformated query objects(q) are ignored.
            pass
            #return _report_error('KeyError', e)

    filters = sanitize_arguments(filters, capabilities.METER_LIST_CAPABILITIES)
    result = {}
    try:
        result['data'] = new_ceilometer_api.get_meters(**filters)
    except (err.ClientSideError, err.ServerSideError), e:
        return _report_error(e.message)

    _update_total_meters_count(request, filters)

    result['recordsTotal'] = request.session['total_meters_count']
    result['recordsFiltered'] = request.session['total_meters_count']
    return HttpResponse(json.dumps(result), content_type='application/json')


@decorators.login_required
def get_predict_meters(request):
    '''
    Get desired meters for prediction page.
    Desired meter_name are listed in capabilities.PREDICT_DESIRED_METERS
    :param request: Django request
    :return: Json response
    '''
    token_id = request.session['token'].id
    print request.body
    print 0
    filters = json.loads(request.body)
    print 111111
    print filters
    try:
        machine_id = filters.pop('resource_id','')
    except KeyError, e:
        return _report_error('KeyError', 'machine_id must be provided')
    print 1
    # Filtering meters, store result in desired
    result = {}
    desired_meters = []
    try:
        meter_list = ceilometer_api.get_meters(token_id, resource_id=machine_id)['data']
        for meter in meter_list:
            if meter['name'] in capabilities.PREDICT_DESIRED_METERS:
                desired_meters.append(meter)
    except KeyError, e:
        return _report_error('KeyError', 'Get prediction data failed')
    print 2
    result['status'] = 'success'
    result['recordsTotal'] = len(desired_meters)
    result['recordsFiltered'] = len(desired_meters)
    result['data'] = desired_meters
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
    if 'total_meters_count' in request.session:
        refreshed_time = request.session['refreshed_time']
        delta = time.time() - refreshed_time
        if delta < 1000 and request.session['criteria_hash'] == filters:
            return
    request.session['refreshed_time'] = time.time()
    request.session['criteria_hash'] = filters

    # TODO: Error handling for hashing meter_list
    # Resend the request purged of limit and skip to get total record number
    token_id = request.session['token'].id
    new_ceilometer_api = CeilometerApi(token_id)

    try:
        meter_list = new_ceilometer_api.get_meters(**filters)
        request.session['total_meters_count'] = len(meter_list)
    except (err.ClientSideError, err.ServerSideError), e:
        request.session['total_meters_count'] = 0
        return _report_error(e.message)


@decorators.login_required
def update_alarm_enabled(request, alarm_id):
    '''
    Update the 'enabled' field of a given alarm
    :param request: (Django request)
    :param alarm_id: (string) id of an alarm
    :return: HTTPResponse (application/json)
    '''

    # First fetch alarm data
    token_id = request.session['token'].id
    new_ceilometer_api = CeilometerApi(token_id)

    try:
        alarm_data = new_ceilometer_api.get_alarm_detail(alarm_id)
        alarm_data['enabled'] = string_to_bool(request.GET['enabled'])
        result = new_ceilometer_api.update_threshold_alarm(alarm_id, alarm_data)
        return HttpResponse(json.dumps(result), content_type='application/json')
    except KeyError, e:
        return _report_error(str(e) + 'shall be provided')
    except ValueError, e:
        return _report_error(e.message)
    except (err.ClientSideError, err.ServerSideError), e:
        return _report_error(e.message)


@decorators.login_required
def copy_alarm_to_resources(request):
    '''
    # TODO:(pwwp)
    Not yet finished!
    :param request:
    :return:
    '''
    # Fetch alarm data
    token_id = request.session['token'].id
    new_ceilometer_api = CeilometerApi(token_id)

    if 'alarm_id' not in request.GET:
        return _report_error('"alarm_id" should be provided.')
    alarm_id = request.GET['alarm_id']
    alarm_data = None
    try:
        alarm_data = new_ceilometer_api.get_alarm_detail(alarm_id)
    except (err.ClientSideError, err.ServerSideError), e:
        return _report_error(e.message)

    args = _request_GET_to_dict(request.GET, False)
    resource_list = args['resource_id']
    try:
        for resource in resource_list:
            alarm_data['q'] = {'field': 'resource_id', 'value': resource}
        result = new_ceilometer_api.post_threshold_alarm(**alarm_data)
        if result['status'] == 'error':
            return _report_error(result['error_msg'])
    except (err.ClientSideError, err.ServerSideError), e:
        return _report_error(e.message)
    except Exception, e:
        return _report_error('Unknown Error')

    messages.success(request, 'Alarm ID: "' + alarm_id + '" has been copied')
    return HttpResponse(json.dumps({'status': 'success', 'data': []}),
                        content_type='application/json')


@decorators.login_required
def delete_alarm(request, alarm_id):
    '''
    Delete a given alarm
    :param request: Django request object
    :param alarm_id: id of an alarm
    :return: HTTPResponse (application/json)
    '''
    token_id = request.session['token'].id
    new_ceilometer_api = CeilometerApi(token_id)
    try:
        new_ceilometer_api.delete_alarm(alarm_id)
        result = {'data': 'Alarm ' + alarm_id + ' has been deleted.'}
        return HttpResponse(json.dumps(result), content_type='application/json')
    except (err.ClientSideError, err.ServerSideError), e:
        return _report_error(e.message)


@decorators.login_required
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
    token_id = request.session['token'].id
    new_ceilometer_api = CeilometerApi(token_id)

    meters, kwargs = _request_GET_to_dict(request.GET)
    result = []
    try:
        for meter_name, resource_ids in meters.iteritems():
            for i in range(len(resource_ids)):
                resource_id = resource_ids[i]
                result.append({
                    'meter_name': meter_name,
                    'resource_id': resource_id,
                    'data': new_ceilometer_api.get_samples(meter_name,
                                                           resource_id=resource_id,
                                                           **kwargs)
                })
        return HttpResponse(json.dumps({'data': result}), content_type='application/json')
    except (err.ClientSideError, err.ServerSideError), e:
        return _report_error(e.message)


@decorators.login_required
def get_alarm_count(request):
    alarm_count = {'alarm': 0, 'ok': 0, 'insufficient_data': 0}
    token_id = request.session['token'].id
    new_ceilometer_api = CeilometerApi(token_id)

    try:
        alarm_count['alarm'] = len(new_ceilometer_api.get_alarms(state='alarm'))
        alarm_count['ok'] = len(new_ceilometer_api.get_alarms(state='ok'))
        alarm_count['insufficient_data'] = len(new_ceilometer_api.get_alarms(
            state='insufficient+data'))
        return HttpResponse(json.dumps(alarm_count), content_type='application/json')
    except KeyError, e:
        return _report_error('ServerSideError: Alarm counting failed')
    except (err.ClientSideError, err.ServerSideError), e:
        return _report_error(e.message)


@csrf_protect
@decorators.login_required
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
    filters = sanitize_arguments(filters, capabilities.ALARM_LIST_CAPABILITIES)
    token_id = request.session['token'].id
    new_ceilometer_api = CeilometerApi(token_id)

    try:
        result = {}
        result['status'] = 'success'
        result['data'] = new_ceilometer_api.get_alarms(**filters)
        result['recordsTotal'] = len(result['data'])
        result['recordsFiltered'] = len(result['data'])
        print 'success'
        return HttpResponse(json.dumps(result), content_type='application/json')
    except (err.ClientSideError, err.ServerSideError), e:
        print 'fail'
        return _report_error(e.message)


@decorators.login_required
def get_alarm_detail(request):
    arrays = _request_GET_to_dict(request.GET, seperate_args_and_list=False)
    if 'alarm_id' not in arrays:
        return _report_error('KeyError: alarm_id not provided')
    alarm_id = arrays['alarm_id']
    #filters = sanitize_arguments(filters, capabilities.ALARM_LIST_CAPABILITIES)
    token_id = request.session['token'].id
    new_ceilometer_api = CeilometerApi(token_id)

    try:
        result = new_ceilometer_api.get_alarm_detail(alarm_id)
        return HttpResponse(json.dumps(result), content_type='application/json')
    except (err.ClientSideError, err.ServerSideError), e:
        return _report_error(e.message)


@decorators.login_required
def get_resources(request):
    '''
    Get resource list through Ceilometer API
    :param request: Django request object
    :return:
    '''
    arrays, filters = _request_GET_to_dict(request.GET)
    filters = sanitize_arguments(filters, capabilities.RESOURCE_LIST_CAPABILITIES)
    token_id = request.session['token'].id
    new_ceilometer_api = CeilometerApi(token_id)
    try:
        result = ceilometer_api.get_resources(token_id, **filters)
        return HttpResponse(json.dumps(result), content_type='application/json')
    except (err.ClientSideError, err.ServerSideError), e:
        return _report_error(e.message)


@decorators.login_required
def resource_detail(request, resource_id):
    '''
    Get resource list through Ceilometer API
    :param request: Django request object
    :return:
    '''
    arrays, filters = _request_GET_to_dict(request.GET)
    token_id = request.session['token'].id
    new_ceilometer_api = CeilometerApi(token_id)

    try:
        result = new_ceilometer_api.get_resources(resource_id=resource_id)
        return HttpResponse(json.dumps(result), content_type='application/json')
    except (err.ClientSideError, err.ServerSideError), e:
        return _report_error(e.message)


@decorators.login_required
def get_vm_list(request):
    '''
    Get tenant's server list(virtual-machine list) through nova api.
    Temporarily does not support filter or pagination.
    :param request: Django request object
    :return: server list json(packed according to data source requirements
                               of DataTables):
              {
                  status: <success| failure> ,
                  recordsTotal: <total>,
                  recordsFiltered: <filtered>,
                  data: [
                      {name: <server_name>, id: <server_id>} ...
                  ],
              }
    '''
    token = request.session['token']
    servers = nova_api.get_server_list(token)
    if servers['status'] != 'success':
        return _report_error('error')
    result = {"status": "success",
              "recordsTotal": len(servers['data']['servers']),
              "recordsFiltered": len(servers['data']['servers']),
              "data": [{'name': server['name'],
                        'id': server['id'],
                        'hypervisor': server['OS-EXT-SRV-ATTR:host'],
                        'status': server['status']}
                       for server in servers['data']['servers']]
              }
    return HttpResponse(json.dumps(result), content_type='application/json')


@decorators.login_required
def get_pm_list(request):
    '''
    Get hypervisor list(physical-machine list) through nova api.
    Temporarily does not support filter or pagination.
    :param request: Django request object
    :return: server list json(packed according to data source requirements
                               of DataTables):
              {
                  status: <success| failure> ,
                  recordsTotal: <total>,
                  recordsFiltered: <filtered>,
                  data: [
                      {name: <server_name>, id: <server_id>} ...
                  ],
              }
    '''
    token = request.session['token']
    hypervisors = nova_api.get_hypervisor_list(token)
    if hypervisors['status'] != 'success':
        return _report_error('error')
    result = {"status": "success",
              "recordsTotal": len(hypervisors['data']['hypervisors']),
              "recordsFiltered": len(hypervisors['data']['hypervisors']),
              "data": [{'name': hypervisor['hypervisor_hostname'],
                        # TODO(pwwp): Confirm this usage (setting id = name)
                        'id': hypervisor['hypervisor_hostname']
                        }
                       for hypervisor in hypervisors['data']['hypervisors']]}
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
    url_handle = qdict_to_dict(qdict)
    arrays = {}
    url_variables = {}
    for k in url_handle.iterkeys():
        if type(url_handle[k]) is list:
            arrays[k] = url_handle[k]
        else:
            url_variables[k] = url_handle[k]

    if not seperate_args_and_list:
        arrays.update(url_variables)
        return arrays
    return arrays, url_variables


def _report_error(error_msg, code=None):
    '''
    Report error data
    :param error_type: (string) Error type
    :param error_msg: (string) Error message
    :return: HTTPResponse Object(application/json response)
    '''
    _code = 404 if code is None else code
    return HttpResponseBadRequest(content=error_msg)


@decorators.login_required
def getTopoInfo(request):
    paramiko.util.log_to_file('paramiko.log')
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(hostname=settings.TOPO_SERVER, port=settings.TOPO_SERVER_PORT, username=settings.TOPO_SERVER_USER,
              password=settings.TOPO_SERVER_PASSWD)
    stdin, stdout, stderr = s.exec_command('cat ' + settings.TOPO_FILE)
    res = stdout.read()
    error_json = {'status': 'error',
                  'error_type': 'error_type',
                  'error_msg': 'error_msg'
                  }
    s.close()
    str(res)
    l=len(res)
    str1=res[0:l-4]
    str1+=","
    #print str1
    str3=""
    token = request.session['token']
    vm_list = get_VMonPM(token)
    for k in vm_list:
        str3+="'"+k+"'"
        str3+=":["
        #print str3
        for n in vm_list[k]:
            count=len(n)
            m=0
            for i in n:
                str3+="{'type':'2','fromPort':'','frominOctets':'','fromoutOctets':'','toId':'','toMac':'',"
                str3+="'toIp':'"+i['ip']+"',"
                str3+="'Name':'"+i['name']+"',"
                str3+="'Id':'"+i['id']+"'}"
                m+=1
                if m!=count:
                    str3+=","
        str3+="],"
    le=len(str3)
    str2=str3[0:le-1]
    #print str2
    str1+=str2
    str1+="}"
    #print str1
    #for now is right
    return HttpResponse(json.dumps({'data': str1.replace('\n', '').replace(' ', '')}), content_type='application/json')
    #return HttpResponse(json.dumps({'data': error_json}), content_type='application/json')

@decorators.login_required
def getVM_TopoInfo(request):
    token = request.session['token']
    project_id = token.project['id']
    request_header = {}
    request_header['X-Auth-Token'] = token.id
    request_header['Content-Type'] = 'application/json'

    vm_topo = []
    vm_ip = []
    pmList = nova_connection(project_id, '/servers/detail', method='GET', header=request_header)
    if pmList['status'] == "success":
        for single in pmList['data']['servers']:
            if (single['addresses']=={}):
                continue
            temp1 = single['addresses']['tenant-net']
            ip = temp1[0]['addr']
            vm_ip.append(ip)
    #print vm_ip
    #for i in vm_ip:
    #    print i
    #print
    #SSH files
    paramiko.util.log_to_file('paramiko.log')
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for pm in range(len(settings.VM_TOPO_SERVER)) :
        s.connect(hostname=settings.VM_TOPO_SERVER[pm], port=settings.VM_TOPO_SERVER_PORT, username=settings.VM_TOPO_SERVER_USER[pm],
              password=settings.VM_TOPO_SERVER_PASSWD[pm])
        stdin, stdout, stderr = s.exec_command('cat ' + settings.VM_TOPO_FILE)
        res = stdout.read()
        to = res.split('\n')
        vm_topo.extend(to)

    while '' in vm_topo :
        vm_topo.remove('')
    #for single in vm_topo :
    #    print single
    #print "#####################"

    #print len(vm_topo)
    for vm in range(len(vm_topo)) :
        ip = []
        ip = vm_topo[vm].split()
        for i in range(len(ip)) :
            if ip[i] not in vm_ip :
                ip[i] = 'externNet'
        temp = ip[0]+' '+ip[1]+','
        vm_topo[vm] = temp

    #delete the repeat item there has 10 21 or 21 10 can not be deleted
    vm_topo = list(set(vm_topo))
    for i in range(len(vm_topo)) :
        if vm_topo[i] == 'externNet externNet,' :
            del vm_topo[i]

    for single in vm_topo :
        print single
    return HttpResponse(vm_topo)


@decorators.login_required
def get_predict_data(request):
    arrays, filters = _request_GET_to_dict(request.GET)
    _name = filters.get("name","")
    _meter = filters.get("meter","")
    
    vms = prediction_api.get_prediction_data(_name,_meter)
    
    
    array = {}
    n = 0
    for d in vms[0].data:
        array.setdefault("data_date"+str(n),d.date)
        array.setdefault("data_pre_value"+str(n),d.predicted_value)
        array.setdefault("data_ac_value"+str(n),d.actual_value)
        n = n+1
    
    return HttpResponse(json.dumps(array), content_type='application/json')





def _convert_action_to_action_url(action_list):
    '''
    Convert an alarm action to link for backend storage.
    Rule:
        Original: type=<email|link|...>&detail=<detail>
        Converted: http://THIS_ADDR/notification/?type=<type>&detail=<detail>
    Example:
        Original: type=email&detail=mail@site.com
        Converted: http://THIS_ADDR/notification/?type=email&detail=mail@site.com
    :param action_list:
    :return:
    '''
    action_url = []
    for action in action_list:
        action_regex = re.compile('type=(' + '|'.join(NOTIFICATION_CAPABILITIES) + ')&detail=(.*)')
        reg_match = action_regex.match(action)
        action_type, action_detail = reg_match.group(1), reg_match.group(2)
        action_url.append('http://' + settings.THIS_ADDR + '/notification/')

