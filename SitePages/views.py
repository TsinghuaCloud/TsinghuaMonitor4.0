from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
import json, httplib

# Create your views here.
def overview(request):
    return render(request, 'overview.html')

def meters_page(request):
    return render(request, 'meters.html')

def test_page(request):
    return render(request, 'test-page.html')