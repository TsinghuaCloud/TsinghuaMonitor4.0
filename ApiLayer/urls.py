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
    url(r'^authentication/get-token$', views.get_token, name='Token'),
    url(r'^servers/vm-list$', views.get_vm_list, name='Server List'),
    url(r'^servers/pm-list$', views.get_pm_list, name='Server List'),
    url(r'^meters/meter-list$', views.get_meters, name='Meter List'),
    url(r'^meters/meter-samples$', views.get_samples, name='Sample List'),
    url(r'^alarms/alarm-list$', views.get_alarms, name='Alarm List'),
    url(r'^alarms/alarm-detail$', views.get_alarm_detail, name='Alarm Detail'),
    url(r'^alarms/post-alarm/$', views.post_alarm, name='Create New Alarm'),
    url(r'^alarms/update-alarm/([0-9a-f\-]+)/$', views.update_alarm, name='Edit Alarm'),
    url(r'^alarms/delete-alarm/([0-9a-f\-]+)/$', views.delete_alarm, name='Delete Alarm'),
    url(r'^resources/resource-list$', views.get_resources, name='Resource List'),
    url(r'^getTopoInfo$', views.getTopoInfo, name='getTopoInfo')
]

