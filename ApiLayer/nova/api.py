__author__ = 'pwwpcheng'

from django.http import request
from openstack_auth.user import Token as openstack_auth_token_class

from ApiLayer.nova.connection import nova_connection

def get_server_list(token):
    assert isinstance(token, openstack_auth_token_class)
    token_string = token.id
    project_id = token.project['id']
    request_header = {'X-Auth-Token': token_string,
                      'Content-Type': 'application/json'}
    return nova_connection(project_id,'servers/detail', 'GET', request_header)


def get_hypervisor_list(token):
    assert isinstance(token, openstack_auth_token_class)
    token_string = token.id
    project_id = token.project['id']
    request_header = {'X-Auth-Token': token_string,
                      'Content-Type': 'application/json'}
    return nova_connection(project_id, 'os-hypervisors', 'GET', request_header)
