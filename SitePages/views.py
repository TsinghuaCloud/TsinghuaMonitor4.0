import json
import httplib

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect

from ApiLayer import views as ceilometer_api
from ApiLayer import api_interface

# Create your views here.
def overview(request):
    return render(request, 'overview.html')


def meters_page(request):
    return render(request, 'meters.html', {'title': 'Meter-list'})


def test_page(request):
    request.session['token'] = ceilometer_api.get_token(request, 'token')

    return render(request, 'test-page.html')


def resource_page(request):
    # token = api_interface.get_V3token()['token']

    #print tokenv3
    token = ceilometer_api.get_token(request, token_type='token')['token']
    request.session['token'] = token
    PminfoDetail = ceilometer_api.get_PmInfo(token)
    for i in range(len(PminfoDetail)):
        PminfoDetail[i]['memory_mb_used'] = round(PminfoDetail[i]['memory_mb_used'] / 1000.0, 2)
        PminfoDetail[i]['memory_mb'] = round(PminfoDetail[i]['memory_mb'] / 1000.0, 2)
    resourceOverview = ceilometer_api.get_allPmStatistics(token)['data']['hypervisor_statistics']
    resourceOverview['memory_mb_left'] = round(
        (resourceOverview['memory_mb'] - resourceOverview['memory_mb_used']) / 1000.0, 2)
    resourceOverview['memory_mb_used'] = round(resourceOverview['memory_mb_used'] / 1000.0, 2)
    allVMList = ceilometer_api.get_allVMList(token)
    PMs = {}
    for key in allVMList:
        temp = {}
        temp['len'] = len(allVMList[key])
        temp['left'] = allVMList[key][1:]
        temp['first'] = allVMList[key][0]
        PMs[key] = temp
    return render(request, 'resource.html',
                  {'title': 'resource-list', 'PMs': PMs, 'Pminfo': PminfoDetail, 'resourceOverview': resourceOverview})


@csrf_protect
def create_alarm(request):
    if request.method == 'GET':
        return render(request, 'create_threshold_alarm_basis.html',
                      {
                          'title': 'Create-alarm',
                          'threshold_step_html': '_create_threshold_alarm_step_1.html',
                          'step': 1,
                      })
    if request.method == 'POST':
        step = request.POST.get('step')
        # Invalid inputs for step will return 404_page
        if step is None or step not in ['1', '2', '3', '4']:
            raise Http404
        return render(request, 'create_threshold_alarm_basis.html',
                      {
                          'threshold_step_html': '_create_threshold_alarm_step_' + step + '.html',
                          'step': step,
                          'threshold': '1',
                          'meter_name': 'cpu_util',
                          'alarm_actions': ['166.111'],
                      })
    return Http404


def netTopo_page(request):
    return render(request, 'netTopo.html', {'title': 'Create-alarm'})

