__author__ = 'pwwpcheng'

from CommonMethods.BaseMethods import kwargs_to_url_parameter_object, \
                                        sanitize_arguments, \
                                        add_list_unique
from ApiLayer.ceilometer.connection import ceilometer_connection
from ApiLayer.base import capabilities


def get_alarms(token, **kwargs):
    '''
    Get alarm list from Ceilometer
    :param token:
    :param kwargs:
    :return:
    '''
    request_header = {'X-Auth-Token': token,
                      'Content-Type': 'application/json'}
    url_para_obj = kwargs_to_url_parameter_object(**kwargs)
    return ceilometer_connection('alarms', method='GET', header=request_header, url_parameters=url_para_obj)


def get_meters(token, **kwargs):
    '''
    Get meter list from ceilometer api
    :param token: (string) token issued by Keystone
    :param kwargs: (Dict) filter criteria
    :return:
    '''
    request_header = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    url_para_obj = kwargs_to_url_parameter_object(**kwargs)
    return ceilometer_connection('meters', method='GET', header=request_header, url_parameters=url_para_obj)


def get_resources(token, **kwargs):
    request_header = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    url_para_obj = kwargs_to_url_parameter_object(**kwargs)
    return ceilometer_connection('resources', method='GET', header=request_header, url_parameters=url_para_obj)


def get_samples(token, meter_name, **kwargs):
    '''
    Get samples of a selected meter
    :param token: (string) token issued by Keystone
    :param meter_name: (string)
    :param kwargs: (Dict) Query criteria,
                    e.g. ['meter_name': <meter_name>, 'resource_id': <resource_id>]
    :return:
    '''
    request_header = {}
    request_header['X-Auth-Token'] = token
    request_header['Content-Type'] = 'application/json'
    kwargs['limit'] = 500
    url_para_obj = kwargs_to_url_parameter_object(**kwargs)
    return ceilometer_connection('meters/' + meter_name,
                                 method='GET',
                                 header=request_header,
                                 url_parameters=url_para_obj)['data']

def delete_alarm(token, alarm_id):
    '''
    Delete alarm through ceilometer api alarm-delete
    :param token: (string) OpenStack Keystone token
    :param alarm_id: (string) alarm id
    :return: (Object) success or error
    '''
    alarm_existence_status = get_alarm_detail(token, alarm_id=alarm_id)['status']
    if alarm_existence_status != 'success':
        return {'status': 'error', 'error_msg': 'Alarm [' + alarm_id + '] does not exist!'}
    request_header = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    return ceilometer_connection('alarms/' + alarm_id,
                                 method='DELETE',
                                 header=request_header)


def update_threshold_alarm(token, alarm_id, alarm_body):
    '''
    Update threshold alarm via Ceilometer alarm-threshold-update api
    NOTICE: This interface doesn't perform any check on necessary
            field names, types, or structures. It just sends an
            updated alarm to openstack api and returns its result.
            Any check should be performed at the upper layer.
    :param token: (string) OpenStack Keystone token
    :param alarm_id: (string) alarm to be updated
    :param alarm_body: (Dict) alarm_detail (according to OpenStack Alarm Obj)
    :return: (Dict) success or error
    '''

    alarm_existence_status = get_alarm_detail(token, alarm_id=alarm_id)['status']
    if alarm_existence_status != 'success':
        return {'status': 'error', 'error_msg': 'Alarm [' + alarm_id + '] does not exist!'}
    request_header = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    return ceilometer_connection('alarms/' + alarm_id,
                                 method='PUT',
                                 header=request_header,
                                 body=alarm_body)


def post_threshold_alarm(token, **kwargs):
    # Pack related kwargs into alarm_dictionary
    new_alarm = {}
    new_alarm['threshold_rule'] = {}
    request_header = {'X-Auth-Token': token, 'Content-Type': 'application/json'}

    # Mandatory arguments for packing a new alarm
    try:
        new_alarm['name'] = kwargs['name']
        new_alarm['threshold_rule']['meter_name'] = kwargs['meter_name']
        new_alarm['threshold_rule']['threshold'] = kwargs['threshold']
    except KeyError, e:
        return {'status': 'error',
                'error_msg': 'Key: "' + str(e) + '" is illegal!'}

    # Pack other optional arguments
    new_alarm['alarm_actions'] = kwargs.get('alarm_actions', [])
    new_alarm['ok_actions'] = kwargs.get('ok_actions', [])
    new_alarm['insufficient_data_actions'] = kwargs.get('insufficient_data_actions', [])
    new_alarm['type'] = kwargs.get('type', 'threshold')
    new_alarm['repeat_actions'] = kwargs.get('repeat_actions', False)
    new_alarm['severity'] = kwargs.get('severity', 'low')
    new_alarm['enabled'] = kwargs.get('enabled', True)
    new_alarm['threshold_rule']['period'] = kwargs.get('period', 60)
    new_alarm['threshold_rule']['statistic'] = kwargs.get('statistic', 'avg')
    new_alarm['threshold_rule']['comparison_operator'] = kwargs.get('comparison_operator', 'ge')
    new_alarm['threshold_rule']['query'] = kwargs.get('q', [])
    return ceilometer_connection(base_url='alarms/',
                                 method='POST',
                                 header=request_header,
                                 body=new_alarm)


def get_alarm_detail(token, alarm_id, **kwargs):
    '''
    Get alarm detail from Ceilometer
    :param token:
    :param kwargs:
    :return:
    '''
    request_header = {'X-Auth-Token': token,
                      'Content-Type': 'application/json'}
    return ceilometer_connection('alarms/' + alarm_id, method='GET', header=request_header)