__author__ = 'pwwpcheng'

# This file stores query capabilities(filter option) for ceilometer-api
# The capabilities is derived from Ceilometer version 1.0.13

alarm_list_capabilities = ['name', 'user_id', 'project_id', 'meter_name', 'enabled',
                           'state', 'alarm_id', 'alarm_type', 'resource_id']

meter_list_capabilities = ['user_id', 'project_id', 'meter_id', 'source',
                           'limit', 'skip']

resource_list_capabilities = ['user_id', 'project_id', 'limit', 'skip']



