__author__ = 'pwwpcheng'

from django.conf import settings

from ApiLayer.base.connection_base import openstack_api_connection


def nova_connection(base_url, method, header, url_parameters=None, body=None):
    return _nova_connection(base_url, method, header, url_parameters=url_parameters, body=body)

def _nova_connection(*args, **kwargs):
    '''
    Specify endpoint settings for openstack connection
    '''
    return openstack_api_connection(*args,
                                    port=settings.NOVA_PORT,
                                    version='v2',
                                    tenant_id=settings.ADMIN_TENANT_ID,
                                    **kwargs)