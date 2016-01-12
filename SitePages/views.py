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
    request.session['username'] = 'admin'
    request.session['password'] = 'cloud'
    request.session['tenant_name'] = 'admin'
    request.session['token'] = ceilometer_api.get_token(request, 'token')

    return render(request, 'test-page.html')