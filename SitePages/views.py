import json
import httplib

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect

import CommonMethods.BaseMethods as BaseMethods
from ApiLayer import views as openstack_api


# Create your views here.
def overview(request):
    return render(request, 'overview.html')


def meter_list_page(request):
    return render(request, 'meters/meters.html', {'title': 'Meter list'})


def alarm_list_page(request):
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
    if request.method == 'GET':
        request.session['token'] = openstack_api.get_token(request, 'token')['token']
        return render(request, 'alarms/create_alarm/create_threshold_alarm_basis.html',
                      {
                          'title': 'Create-alarm',
                          'threshold_step_html': 'alarms/threshold_alarm_basis/_threshold_alarm_step_1.html',
                          'step': 1,
                          'alarm_data': {
                              'machine_type': 'vm',
                          },
                      })
    if request.method == 'POST':
        step = request.POST.get('next_step', '0')
        # Invalid inputs for step will be served with 404 page
        if step is None or step not in ['1', '2', '3', '4']:
            raise Http404('Invalid value of "step"')
        alarm_data = BaseMethods.qdict_to_dict(request.POST)
        return render(request, 'alarms/create_alarm/create_threshold_alarm_basis.html',
                      {
                          'threshold_step_html': 'alarms/threshold_alarm_basis/_threshold_alarm_step_' + step + '.html',
                          'step': step,
                          'alarm_data': alarm_data,
                      })
    return Http404

@csrf_protect
def edit_alarm(request, alarm_id):
    try:
        pass
    except KeyError:
        pass

    if request.method == 'GET':
        request.session['token'] = openstack_api.get_token(request, 'token')['token']
        return render(request, 'alarms/create_alarm/create_threshold_alarm_basis.html',
                      {
                          'title': 'Edit Alarm',
                          'threshold_step_html': 'alarms/threshold_alarm_basis/_threshold_alarm_step_1.html',
                          'step': 1,
                          'alarm_data': {
                              'machine_type': 'vm',
                          },
                      })
    if request.method == 'POST':
        step = request.POST.get('next_step', '0')
        # Invalid inputs for step will be served with 404 page
        if step is None or step not in ['1', '2', '3', '4']:
            raise Http404('Invalid value of "step"')
        alarm_data = BaseMethods.qdict_to_dict(request.POST)
        return render(request, 'alarms/create_alarm/create_threshold_alarm_basis.html',
                      {
                          'threshold_step_html': 'alarms/threshold_alarm_basis/_threshold_alarm_step_' + step + '.html',
                          'step': step,
                          'alarm_data': alarm_data,
                      })
    return Http404


def netTopo_page(request):
    return render(request, 'netTopo.html', {'title': 'Create-alarm'})

