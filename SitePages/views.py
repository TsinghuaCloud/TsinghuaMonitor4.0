from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
import json, httplib
from ApiLayer import views as ceilometer_api

# Create your views here.
def overview(request):
    return render(request, 'overview.html')

def meters_page(request):
    return render(request, 'meters.html', {'title': 'Meter-list'})

def test_page(request):
    request.session['token'] = ceilometer_api.get_token(request, 'token')

    return render(request, 'test-page.html')

def resource_page(request):
    token = ceilometer_api.get_token(request, token_type='token')['token']
    request.session['token'] = token
    PminfoDetail=ceilometer_api.get_PmInfo(token)
    resourceOverview=ceilometer_api.get_allPmStatistics(token)
    return render(request, 'resource.html', {'title': 'resource-list','Pminfo':PminfoDetail,'resourceOverview':resourceOverview['data']['hypervisor_statistics']})
