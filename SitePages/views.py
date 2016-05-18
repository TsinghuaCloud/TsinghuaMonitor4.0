import urllib
import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as django_auth_views
from django.contrib.auth import logout as django_auth_logout
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.utils import functional
from django.views.decorators.csrf import csrf_protect
from openstack_auth import utils as openstack_auth_utils
from openstack_auth import user as openstack_auth_user
from openstack_auth.forms import Login as openstack_auth_form
from keystoneclient import exceptions as keystone_client_exceptions

from ApiLayer import views as openstack_api
from ApiLayer.base import capabilities as APICapabilities
import Common.BaseMethods as BaseMethods
from Common import decorators

import pymongo
from pymongo import MongoClient

@csrf_protect
def login(request, **kwargs):
    '''
    Logs a user in using the :class:`~openstack_auth.forms.Login` form.
    Referenced from openstack_auth.views.login
    '''
    if not request.is_ajax():
        # If the user is already authenticated, redirect them to the
        # dashboard straight away, unless the 'next' parameter is set as it
        # usually indicates requesting access to a page that requires different
        # permissions.
        if request.user.is_authenticated():
            return HttpResponseRedirect('/')

    # Get our initial region for the form.
    form = functional.curry(openstack_auth_form)
    template_name = 'auth/login.html'
    res = django_auth_views.login(request,
                                  template_name=template_name,
                                  authentication_form=form,
                                  **kwargs)

    # Save the region in the cookie, this is used as the default
    # selected region next time the Login form loads.
    if request.method == "POST":
        openstack_auth_utils.set_response_cookie(res, 'login_region',
                                                 request.POST.get('region', ''))
        openstack_auth_utils.set_response_cookie(res, 'login_domain',
                                                 request.POST.get('domain', ''))

    # Set the session data here because django's session key rotation
    # will erase it if we set it earlier.
    print request.user.is_authenticated()
    if request.user.is_authenticated():
        openstack_auth_user.set_session_from_user(request, request.user)
        session = openstack_auth_utils.get_session()
        user_endpoint = settings.OPENSTACK_KEYSTONE_URL
        auth = openstack_auth_utils.get_token_auth_plugin(auth_url=user_endpoint,
                                       token=request.user.unscoped_token,
                                       project_id=settings.ADMIN_TENANT_ID)

        try:
            auth_ref = auth.get_access(session)
        except keystone_client_exceptions.ClientException as e:
            auth_ref = None

        if auth_ref:
            new_user = openstack_auth_user.create_user_from_token(request,
                                                                  openstack_auth_user.Token(auth_ref),
                                                                  endpoint=request.user.endpoint)
            openstack_auth_user.set_session_from_user(request, new_user)

    return res


def logout(request):
    ''' Log out of the system, clean authenticated information
        and redirect user to login page.
    '''
    request.session.delete('region_endpoint')
    request.session.delete('region_name')
    django_auth_logout(request)
    return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)


@decorators.login_required
def overview(request):
    token = request.session['token']
    hypervisor_list = None
    try:
        hypervisor_list = openstack_api.nova_api.get_hypervisor_list(token)['data']['hypervisors']

    except KeyError, e:
        hypervisor_list = {}
    return render(request, 'overview.html', {'hypervisor_list': hypervisor_list})


@decorators.login_required
def meter_list(request):
    '''
        Meter list page.
        Since this page loads meter-list through on-page jquery request,
        it would be enough to just return a rendered page
    '''
    return render(request, 'meters/meters.html', {'title': 'Meter list'})


@decorators.login_required
def alarm_list(request):
    '''
        Alarm list page.
        Since this page loads alarm-list through on-page jquery request,
        it would be enough to just return a rendered page
    '''
    return render(request, 'alarms/alarm_list.html', {'title': 'Alarm list'})


@decorators.login_required
#@decorators.admin_perm_required
def test_page(request):
    return render(request, '_template_page.html')


@decorators.login_required
def resource_page(request):
    token = request.session['token']
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


@decorators.login_required
@csrf_protect
def create_alarm(request):
    '''  Create new alarm through ceilometer alarm-create api  '''
    if request.method == 'GET':
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
        alarm_data['enabled'] = False if alarm_data['enabled'] == 'False' else True
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

    token_id = request.session['token'].id
    return openstack_api.ceilometer_api.post_threshold_alarm(token_id, **kwargs)

@decorators.login_required
def copy_alarm(request, alarm_id):
    token_id = request.session['token'].id
    _alarm_detail = openstack_api.ceilometer_api.get_alarm_detail(token=token_id, alarm_id=alarm_id)['data']

    return render(request, 'alarms/copy_alarm.html', _alarm_detail)

@decorators.login_required
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
    token_id = request.session['token'].id
    alarm_data, original_data = None, {}
    try:
        alarm_data = _read_alarm_data(
            openstack_api.ceilometer_api.get_alarm_detail(token_id, alarm_id))
        original_data['alarm_id'] = alarm_data['alarm_id']
        original_data['meter_name'] = alarm_data['meter_name']
        original_data['query'] = alarm_data.get('query', [])
        original_data['type'] = 'threshold'
    except KeyError, e:
        raise Http404(str(e.message) + ' is missing')

    if request.method == 'GET':
        return render(request, 'alarms/edit_alarm/edit_threshold_alarm_basis.html',
                      {
                          'page_type': 'edit_alarm',
                          'title': 'Edit Alarm',
                          'threshold_step_html': 'alarms/threshold_alarm_basis/_threshold_alarm_step_2.html',
                          'step': 2,
                          'alarm_data': alarm_data
                      })
    if request.method == 'POST':
        # Invalid inputs for step will be served with 404 page
        step = request.POST.get('next_step', '2')
        if step is None or step not in ['2', '3', '4', 'post']:
            raise Http404('Invalid value of "step"')
        edited_data = BaseMethods.qdict_to_dict(request.POST)
        edited_data.update(original_data)  # Overwrite keys that are not allowed to modify

        if step == 'post':
            return_data = _post_edited_alarm(token_id, edited_data, alarm_id)
            new_message = [], {}
            if return_data['status'] == 'success':
                messages.success(request, return_data['data']['name'] + " has been modified")
            else:
                messages.error(request, return_data['error_msg'])
            return HttpResponseRedirect('/monitor/alarms/')

        return render(request, 'alarms/edit_alarm/edit_threshold_alarm_basis.html',
                      {
                          'page_type': 'edit_alarm',
                          'threshold_step_html':
                              'alarms/threshold_alarm_basis/_threshold_alarm_step_' + step + '.html',
                          'step': step,
                          'alarm_data': edited_data,
                      })
    raise Http404('Unknown error in edit_alarm')


def _post_edited_alarm(token, alarm_data, alarm_id=None):
    '''
    Post edited alarm to ceilometer api
    :param request: (Django Request Object) request
    :return: (Dict) success or error message
    '''

    if 'enabled' in alarm_data:
        alarm_data['enabled'] = False if alarm_data['enabled'] == 'False' else True
    if 'repeat_actions' in alarm_data:
        alarm_data['repeat_actions'] = False if alarm_data['repeat_actions'] == 'False' else True
    for action_type in ['alarm_actions', 'ok_actions', 'insufficient_data_actions']:
        if action_type in alarm_data:
            for i in range(0, len(alarm_data[action_type])):
                alarm_data[action_type][i] = \
                    'http://%s/notification/notify/?op=%s' % (settings.THIS_ADDR, alarm_data[action_type][i])
    kwargs = {}
    kwargs.update(alarm_data)

    # Threshold alarms
    threshold_alarm_capabilities = BaseMethods.add_list_unique(
        APICapabilities.ALARM_CAPABILITIES,
        APICapabilities.THRESHOLD_ALARM_CAPABILITIES,
        APICapabilities.QUERY_CAPABILITIES
    )
    kwargs = BaseMethods.sanitize_arguments(kwargs, threshold_alarm_capabilities)

    query_obj = []
    for query_para in APICapabilities.QUERY_CAPABILITIES:
        if query_para in kwargs:
            query_obj.append({'field': query_para, 'value': kwargs.pop(query_para)})
    threshold_rule_obj = {'query': query_obj}

    for threshold_rule_para in APICapabilities.THRESHOLD_ALARM_CAPABILITIES:
        if threshold_rule_para in kwargs:
            threshold_rule_obj[threshold_rule_para] = kwargs.pop(threshold_rule_para)
    alarm_obj = {'threshold_rule': threshold_rule_obj}

    for alarm_para in APICapabilities.ALARM_CAPABILITIES:
        if alarm_para in kwargs:
            alarm_obj[alarm_para] = kwargs.pop(alarm_para)

    return openstack_api.ceilometer_api.update_threshold_alarm(token,
                                                               alarm_id=alarm_id,
                                                               alarm_body=alarm_obj)


@decorators.login_required
def alarm_detail(request, alarm_id):
    ''' Display detail of an alarm '''
    token_id = request.session['token'].id
    alarm_data = {}
    try:
        alarm_data = openstack_api.ceilometer_api.get_alarm_detail(token_id, alarm_id)[
            'data']
    except SystemError:
        pass
    if alarm_data.get('type', '') == 'threshold':
        alarm_data.update(alarm_data.pop('threshold_rule'))
        alarm_data['resource_id'] = alarm_data.get('query', [{}])[0].get('value', '')
    return render(request, 'alarms/alarm_detail.html', {'title': 'Alarm list', 'alarm_data': alarm_data})


@decorators.login_required
def netTopo_page(request):
    return render(request, 'netTopo.html', {'title': 'Create-alarm'})


@decorators.login_required
def process_monitor_vm_list(request):
    return render(request, 'analysis/vm_list.html')


@decorators.login_required
def vm_process_list(request, instance_id):
    # instance_name = openstack_api.nova_api.
    return render(request, 'analysis/vm_process_monitor.html', {'instance_id': instance_id})

def _read_alarm_data(alarm_data):
    '''
    Flatten alarm dictionary to a two-level dict.
    This is only designed for threshold alarms.
    :param alarm_data:
    :return:
    '''
    assert isinstance(alarm_data, dict)
    if alarm_data['status'] == 'error':
        raise Http404('Alarm does not exist')
    data = alarm_data['data'].copy()
    data.update(data.pop('threshold_rule'))
    if len(data['query']) > 0:
        data[data['query'][0].get('field', 'no_field')] = data['query'][0].get('value', '')

    # Fetch operation string from action_list
    # Example:
    # data['alarm_actions'] = ['http://addr.net/path/?op=type%3Da&detail=%3Da',
    #                            'http://addr.net/path/?op=type%3Db&detail=%3Db']
    # Result:
    #   data['alarm_actions'] = ['type%3Da&detail=%3Da', 'type%3Db&detail=%3Db']
    for actions in ['alarm_actions', 'ok_actions', 'insufficient_data_actions']:
        for action_index in range(0, len(data.get(actions, []))):
            operation = urlparse.parse_qs(urlparse.urlparse(data[actions][action_index]).query)
            data[actions][action_index] = urllib.quote(operation['op'][0])
    return data

@decorators.login_required
def prediction_page(request):
    return render(request, 'prediction/prediction_VM.html', {'title': 'workload prediction'})

