__author__ = 'pwwpcheng'

# This file stores query capabilities(filter option) for ceilometer-api
# The capabilities is derived from Ceilometer version 1.0.13

ALARM_LIST_CAPABILITIES = ['name', 'user_id', 'project_id', 'meter_name', 'enabled',
                           'state', 'alarm_id', 'alarm_type', 'resource_id']

METER_LIST_CAPABILITIES = ['user_id', 'project_id', 'meter_id', 'source', 'resource_id',
                           'limit', 'skip', 'resource_id_match', 'resource_name_match']

RESOURCE_LIST_CAPABILITIES = ['user_id', 'project_id', 'limit', 'skip', 'resource_id_match',
                              'resource_name_match', 'meter_name_match']

POST_ALARM_CAPABILITIES = ['comparison_operator', 'description', 'enabled', 'periods',
                           'meter_name', 'name', 'project_id', 'query', 'severity',
                           'resource_id', 'statistic', 'threshold', 'type', 'repeated_actions',
                           'alarm_actions', 'ok_actions', 'insufficient_data_actions']