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

from ApiLayer.VmProcessMonitor import urls as process_monitor_urls
import views
urlpatterns = [
    url(r'^servers/vm-list$', views.get_vm_list, name='Server List'),
    url(r'^servers/pm-list$', views.get_pm_list, name='Hypervisor List'),
    url(r'^meters/meter-list$', views.get_meters, name='Meter List'),
    url(r'^meters/predict-related-meters$', views.get_predict_meters, name='Prediction Meter List'),
    url(r'^meters/meter-samples$', views.get_samples, name='Sample List'),
    url(r'^alarms/alarm-list$', views.get_alarms, name='Alarm List'),
    url(r'^alarms/alarm-count$', views.get_alarm_count, name='Alarm Count'),
    url(r'^alarms/alarm-detail$', views.get_alarm_detail, name='Alarm Detail'),
    url(r'^alarms/post-alarm/$', views.post_alarm, name='Create New Alarm'),
    url(r'^alarms/delete-alarm/([0-9a-f\-]+)/$', views.delete_alarm, name='Delete Alarm'),
    url(r'^alarms/update-alarm-enabled/([0-9a-f\-]+)/$', views.update_alarm_enabled, name='Enable/Disable Alarm'),
    url(r'^resources/resource-list$', views.get_resources, name='Resource List'),
    url(r'^resources/resource-detail/([^/]+)/$', views.resource_detail, name='Resource List'),
    url(r'^analysis/', include(process_monitor_urls)),
    url(r'^getTopoInfo$', views.getTopoInfo, name='getTopoInfo'),
    url(r'^predict/get-data$', views.get_predict_data, name='PredictData List')

]

