__author__ = 'pwwpcheng'

from django.conf import settings

from ApiLayer.base.connection_base import openstack_api_connection


def keystone_connection(base_url, method, header, url_parameters=None, body=None):
    return _keystone_connection(base_url, method, header, url_parameters, body)

def _keystone_connection(*args, **kwargs):
    return openstack_api_connection(*args,
                                    port=settings.KEYSTONE_PORT,
                                    version='v2.0',
                                    **kwargs)
