__author__ = 'pwwpcheng'

from django.http import request

from ApiLayer.nova.connection import nova_connection

def get_server_list(token):
    request_header = {'X-Auth-Token': token,
                      'Content-Type': 'application/json'}
    return nova_connection('servers', 'GET', request_header)


def get_hypervisor_list(token):
    request_header = {'X-Auth-Token': token,
                      'Content-Type': 'application/json'}
    return nova_connection('os-hypervisors', 'GET', request_header)
