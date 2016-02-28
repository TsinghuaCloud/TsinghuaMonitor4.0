import copy
import json
import httplib

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

import CommonMethods.BaseMethods as BaseMethods
from ApiLayer import views as openstack_api

# Create your views here.
def overview(request):
    return render(request, 'overview.html')


def meter_list(request):
    return render(request, 'meters/meters.html', {'title': 'Meter list'})


def alarm_list(request):
    return render(request, 'alarms/alarm_list.html', {'title': 'Alarm list'})


def test_page(request):
    request.session['token'] = openstack_api.get_token(request, 'token')['token']
    return render(request, 'test-page.html')


def resource_page(request):
    # token = api_interface.get_V3token()['token']

    # print tokenv3
    token = openstack_api.get_token(request, token_type='token')['token']
    request.session['token'] = token
    pm_info_detail = openstack_api.get_PmInfo(token)
    for i in range(len(pm_info_detail)):
        pm_info_detail[i]['memory_mb_used'] = round(pm_info_detail[i]['memory_mb_used'] / 1000.0, 2)
        pm_info_detail[i]['memory_mb'] = round(pm_info_detail[i]['memory_mb'] / 1000.0, 2)
        pm_info_detail[i]['memory_percentage'] = round(
            pm_info_detail[i]['memory_mb_used'] / pm_info_detail[i]['memory_mb'],
            4) * 100
        pm_info_detail[i]['disk_percentage'] = round(
            pm_info_detail[i]['local_gb_used'] * 1.0 / pm_info_detail[i]['local_gb'],
            4) * 100
    resource_overview = openstack_api.get_allPmStatistics(token)['data']['hypervisor_statistics']
    resource_overview['memory_mb_left'] = round(
        (resource_overview['memory_mb'] - resource_overview['memory_mb_used']) / 1000.0, 2)
    resource_overview['memory_mb_used'] = round(resource_overview['memory_mb_used'] / 1000.0, 2)
    all_vm_list = openstack_api.get_allVMList(token)
    PMs = {}
    for key in all_vm_list:
        temp = {}
        temp['len'] = len(all_vm_list[key])
        temp['left'] = all_vm_list[key][1:]
        temp['first'] = all_vm_list[key][0]
        PMs[key] = temp
    return render(request, 'resources/resource.html', {'title': 'resource-list',
                                                       'PMs': PMs,
                                                       'Pminfo': pm_info_detail,
                                                       'resource_overview': resource_overview
                                                       })


@csrf_protect
def create_alarm(request):
    '''  Create new alarm through ceilometer alarm-create api  '''
    if request.method == 'GET':
        request.session['token'] = openstack_api.get_token(request, 'token')['token']
        return render(request, 'alarms/create_alarm/create_threshold_alarm_basis.html',
                      {
                          'page_type': 'create_alarm',
                          'title': 'Create-alarm',
                          'threshold_step_html': 'alarms/threshold_alarm_basis/_threshold_alarm_step_1.html',
                          'step': '1',
                          'alarm_data': {
                              'machine_type': 'vm',
                          },
                      })
    if request.method == 'POST':
        # Invalid inputs for step will be served with 404 page
        step = request.POST.get('next_step', '1')
        if step is None or step not in ['1', '2', '3', '4', 'post']:
            raise Http404('Invalid value of "step"')

        # alarm_data passes alarm data between alarm-create pages.
        alarm_data = BaseMethods.qdict_to_dict(request.POST)

        if step == 'post':
            return_data = _post_new_alarm(request)
            new_message = [], {}
            if return_data['status'] == 'success':
                messages.success(request, return_data['data']['name'] + " has been created")
            else:
                messages.error(request, return_data['error_msg'])
            return HttpResponseRedirect('/monitor/alarms/')
        else:
            return render(request, 'alarms/create_alarm/create_threshold_alarm_basis.html',
                          {
                              'page_type': 'create_alarm',
                              'threshold_step_html': 'alarms/threshold_alarm_basis/_threshold_alarm_step_' + step + '.html',
                              'step': step,
                              'alarm_data': alarm_data,
                          })
    raise Http404('Unknown method')


def _post_new_alarm(request):
    '''
    further process new alarm data, and post to ceilometer_api
    :param (Django request object) request
    :return: JSON
    '''
    alarm_data = BaseMethods.qdict_to_dict(request.POST)
    alarm_data.pop('next_step')
    alarm_data.pop('cur_step')

    if 'enabled' in alarm_data:
        alarm_data['enabled'] = False if alarm_data['enabled'] == 'false' else True
    if 'repeat_actions' in alarm_data:
        alarm_data['repeat_actions'] = False if alarm_data['repeat_actions'] == 'false' else True
    for action_type in ['alarm_actions', 'ok_actions', 'insufficient_data_actions']:
        if action_type in alarm_data:
            for i in range(0, len(alarm_data[action_type])):
                alarm_data[action_type][i] = \
                    'http://%s/notification/notify/?op=%s' % (settings.THIS_ADDR, alarm_data[action_type][i])
    kwargs = {}
    kwargs.update(alarm_data)
    q = [{}]
    try:
        q[0] = {}
        q[0]['value'] = kwargs.pop('resource_id')
        q[0]['field'] = 'resource_id'
        q[0]['op'] = 'eq'
    except NameError:
        q[0] = {}
    finally:
        kwargs['q'] = q
    return openstack_api.ceilometer_api.post_threshold_alarm(request.session['token'], **kwargs)


@csrf_protect
def edit_alarm(request, alarm_id):
    '''
    Edit alarm through ceilometer alarm-update api
    If alarm_id does not exist, return 404 error.
    alarm-id, meter-name, resource-name are not allowed for editing
    Thus users shall create a new alarm if one(more) of these
    options was to be modified.
    :param request: Django request object
    :param alarm_id: (string)
    :return: HTTPResponse
    '''
    alarm_data, original_data = None, {}
    try:
        alarm_data = _read_alarm_data(openstack_api.ceilometer_api.get_alarm_detail(request.session['token'], alarm_id))
        if alarm_data['status'] == 'error':
            raise Http404('Unknown alarm-id')
        original_data['alarm_id'] = alarm_data['alarm_id']
        original_data['meter_name'] = alarm_data['meter_name']
        original_data['query'] = alarm_data.get('query', [])
    except KeyError, e:
        raise Http404(e.message)

    if request.method == 'GET':
        request.session['token'] = openstack_api.get_token(request, 'token')['token']
        return render(request, 'alarms/edit_alarm/edit_threshold_alarm_basis.html',
                      {
                          'page_type': 'edit_alarm',
                          'title': 'Edit Alarm',
                          'threshold_step_html': 'alarms/threshold_alarm_basis/_threshold_alarm_step_2.html',
                          'step': 2,
                          'alarm_data': alarm_data['data']
                      })
    if request.method == 'POST':

        # Invalid inputs for step will be served with 404 page
        step = request.POST.get('next_step', '2')
        if step is None or step not in ['2', '3', '4', 'post']:
            raise Http404('Invalid value of "step"')
        edited_data = BaseMethods.qdict_to_dict(request.POST)
        edited_data.update(original_data)
        if step == 'post':
            pass

        # Overwrite keys that are not allowed to modify
        edited_data.update(original_data)
        return render(request, 'alarms/edit_alarm/edit_threshold_alarm_basis.html',
                      {
                          'page_type': 'edit_alarm',
                          'threshold_step_html': 'alarms/threshold_alarm_basis/_threshold_alarm_step_' + step + '.html',
                          'step': step,
                          'alarm_data': edited_data,
                      })
    raise Http404


def alarm_detail(request, alarm_id):
    ''' Display detail of an alarm '''
    request.session['token'] = openstack_api.get_token(request, 'token')['token']
    alarm_data = {}
    try:
        alarm_data = openstack_api.ceilometer_api.get_alarm_detail(request.session['token'], alarm_id)['data']
    except SystemError:
        pass
    if alarm_data.get('type', '') == 'threshold':
        alarm_data.update(alarm_data.pop('threshold_rule'))
        alarm_data['resource_id'] = alarm_data.get('query', [{}])[0].get('value', '')
    return render(request, 'alarms/alarm_detail.html', {'title': 'Alarm list', 'alarm_data': alarm_data})


def netTopo_page(request):
    return render(request, 'netTopo.html', {'title': 'Create-alarm'})


def _read_alarm_data(alarm_data):
    '''
    Flatten alarm dictionary to a two-level dict.
    This is only designed for threshold alarms.
    :param alarm_data:
    :return:
    '''
    assert isinstance(alarm_data, dict)
    data = alarm_data.copy()
    data.update(data.pop('threshold_rule'))
    if len(data['query']) > 0:
        data[data['query'][0].get('field', 'no_field')] = data['query'][0].get('value', '')
    print 'alarm_data is read as: '
    print data
    return data
