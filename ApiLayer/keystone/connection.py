__author__ = 'pwwpcheng'

from django.conf import settings
from ApiLayer.connection_base import openstack_api_connection

def keystone_connection(*args, **kwargs):
    return openstack_api_connection(*args,
                                    port=settings.KEYSTONE_PORT,
                                    version='v2.0',
                                    **kwargs)
