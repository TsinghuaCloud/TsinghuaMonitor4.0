from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
import json, httplib
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
    #token = api_interface.get_V3token()['token']
   
    #print tokenv3
    token = ceilometer_api.get_token(request, token_type='token')['token']
    request.session['token'] = token
    PminfoDetail=ceilometer_api.get_PmInfo(token)
    resourceOverview=ceilometer_api.get_allPmStatistics(token)['data']['hypervisor_statistics']
    resourceOverview['memory_mb_left']=round((resourceOverview['memory_mb']-resourceOverview['memory_mb_used'])/1000.0,2)
    resourceOverview['memory_mb_used']=round(resourceOverview['memory_mb_used']/1000.0,2)
    allVMList=ceilometer_api.get_allVMList(token)
    PMs={}
    for key in allVMList:
        temp={}
        temp['len']=len(allVMList[key])
        temp['left']=allVMList[key][1:]
        temp['first']=allVMList[key][0]
        PMs[key]=temp
    return render(request, 'resource.html', {'title': 'resource-list','PMs':PMs,'Pminfo':PminfoDetail,'resourceOverview':resourceOverview})