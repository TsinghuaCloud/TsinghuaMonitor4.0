__author__ = 'pwwpcheng'

from Common.BaseMethods import kwargs_to_url_parameter_object, \
    sanitize_arguments, \
    add_list_unique
from ApiLayer.ceilometer.connection import CeilometerConnection
from ApiLayer.base import capabilities
from ApiLayer.base import api_errors as err

class CeilometerApi(object):
    """ Ceilometer Connection Object """
    ceilometer_conn = None

    def __init__(self, token):
        """
        Initialize API object.
        :param token: (string) OpenStack Auth Token
        """
        self.ceilometer_conn = CeilometerConnection(token)

    def get_alarms(self, **kwargs):
        '''
        Get alarm list from Ceilometer
        :param kwargs:
        :return:
        '''
        url_para_obj = kwargs_to_url_parameter_object(**kwargs)
        return self.ceilometer_conn.get_data('alarms', method='GET', url_parameters=url_para_obj)


    def get_meters(self, **kwargs):
        '''
        Get meter list from ceilometer api
        :param kwargs: (Dict) filter criteria
        :return:
        '''
        url_para_obj = kwargs_to_url_parameter_object(**kwargs)
        return self.ceilometer_conn.get_data('meters', method='GET', url_parameters=url_para_obj)


    def get_resources(self, **kwargs):
        '''
        Get resource list from Ceilometer API
        :param kwargs: (Dict) filters.
        :return:
        '''
        url_para_obj = kwargs_to_url_parameter_object(**kwargs)
        return self.ceilometer_conn.get_data('resources', method='GET', url_parameters=url_para_obj)

    def get_resource_detail(self, **kwargs):
        '''
        Get detail of a specified resource
        :param kwargs: (Dict) search filters.
        :return:
        '''
        resource_id = kwargs.pop('resource_id', '')
        url_para_obj = kwargs_to_url_parameter_object(**kwargs)
        return self.ceilometer_conn.get_data('resources/' + resource_id, method='GET', url_parameters=url_para_obj)


    def get_samples(self, meter_name, **kwargs):
        '''
        Get samples of a selected meter
        :param meter_name: (string)
        :param kwargs: (Dict) Query criteria,
                        e.g. ['meter_name': <meter_name>, 'resource_id': <resource_id>]
        :return:
        '''
        kwargs['limit'] = 500
        url_para_obj = kwargs_to_url_parameter_object(**kwargs)
        return self.ceilometer_conn.get_data('meters/' + meter_name,
                                             method='GET',
                                             url_parameters=url_para_obj)

    def delete_alarm(self, alarm_id):
        '''
        Delete alarm through ceilometer api alarm-delete
        :param alarm_id: (string) alarm id
        :return: (Object) success or error
        '''
        try:
            self.get_alarm_detail(alarm_id)
        except err.ResourceNotFound, e:
            raise err.AlarmDoesNotExist(alarm_id)

        return self.ceilometer_conn.get_data('alarms/' + alarm_id,
                                             method='DELETE')


    def update_threshold_alarm(self, alarm_id, alarm_body):
        '''
        Update threshold alarm via Ceilometer alarm-threshold-update api
        NOTICE: This interface doesn't perform any check on necessary
                field names, types, or structures. It just sends an
                updated alarm to openstack api and returns its result.
                Any check should be performed at the upper layer.
        :param alarm_id: (string) alarm to be updated
        :param alarm_body: (Dict) alarm_detail (according to OpenStack Alarm Obj)
        :return: (Dict) success or error
        '''

        try:
            self.get_alarm_detail(alarm_id)
        except err.ResourceNotFound, e:
            raise err.AlarmDoesNotExist(alarm_id)

        return self.ceilometer_conn.get_data('alarms/' + alarm_id,
                                             method='PUT',
                                             body=alarm_body)


    def post_threshold_alarm(self, **kwargs):
        # Pack related kwargs into alarm_dictionary
        new_alarm = {}
        new_alarm['threshold_rule'] = {}

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
        return self.ceilometer_conn.get_data(base_url='alarms/',
                                             method='POST',
                                             body=new_alarm)


    def get_alarm_detail(self, alarm_id, **kwargs):
        '''
        Get alarm detail from Ceilometer
        :param token:
        :param kwargs:
        :return:
        '''
        return self.ceilometer_conn.get_data('alarms/' + alarm_id, method='GET')

