"""CeilometerAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
import views
urlpatterns = [
    url('^authentication/get-token$', views.get_token, name='Token'),
    url('^meters/meter-list$', views.get_meters, name='Meter List'),
    url('^meters/sample-list$', views.get_meters, name='Sample List'),
    url('^alarms/alarm-list/$', views.get_alarms, name='Alarm List'),
    url('^resources/resource-list/$', views.get_resources, name='Resource List')
]

