__author__ = 'pwwpcheng'

# This file stores query capabilities(filter option) for ceilometer-api
# The capabilities is derived from Ceilometer version 1.0.13

ALARM_LIST_CAPABILITIES = ['name', 'user_id', 'project_id', 'meter_name', 'enabled',
                           'state', 'alarm_id', 'alarm_type', 'resource_id']

METER_LIST_CAPABILITIES = ['user_id', 'project_id', 'meter_id', 'source', 'resource_id',
                           'limit', 'skip', 'resource_id_match', 'resource_name_match']

RESOURCE_LIST_CAPABILITIES = ['user_id', 'project_id', 'limit', 'skip', 'resource_id_match',
                              'resource_name_match', 'meter_name_match']

# Some attributes of an alarm is automatically modified by ceilometer-api service,
# including alarm_id, user_id, project_id, state_timestamp,
# Thus, these attributed will be filtered out for modification.
ALARM_CAPABILITIES = ['description', 'enabled', 'state', 'meter_name',
                      'name', 'severity', 'type', 'repeat_actions', 'time_constraints',
                      'alarm_actions', 'ok_actions', 'insufficient_data_actions']

THRESHOLD_ALARM_CAPABILITIES = ['query', 'period', 'comparison_operator', 'threshold',
                                'statistic', 'evaluation_periods', 'exclude_outliers']

QUERY_CAPABILITIES = ['resource_id', 'resource_name']