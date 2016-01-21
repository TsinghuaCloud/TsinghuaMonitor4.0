__author__ = 'pwwpcheng'

# This file stores query capabilities(filter option) for ceilometer-api
# The capabilities is derived from Ceilometer version 1.0.13

alarm_list_capabilities = ['name', 'user_id', 'project_id', 'meter_name', 'enabled',
                           'state', 'alarm_id', 'alarm_type', 'resource_id']

meter_list_capabilities = ['user_id', 'project_id', 'meter_id', 'source', 'resource_id',
                           'limit', 'skip', 'resource_id_match', 'resource_name_match']

resource_list_capabilities = ['user_id', 'project_id', 'limit', 'skip', 'resource_id_match',
                              'resource_name_match']

post_alarm_capabilities = ['comparison_operator', 'description', 'enabled', 'periods',
                           'meter_name', 'name', 'project_id', 'query', 'severity',
                           'resource_id', 'statistic', 'threshold', 'type',
                           'alarm_actions', 'ok_actions', 'insufficient_data_actions']