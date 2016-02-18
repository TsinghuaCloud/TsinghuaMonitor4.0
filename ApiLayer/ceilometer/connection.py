__author__ = 'pwwpcheng'

from django.conf import settings
from ApiLayer.connection_base import openstack_api_connection

def ceilometer_connection(*args, **kwargs):
    return openstack_api_connection(*args,
                                    port=settings.CEILOMETER_PORT,
                                    version='v2',
                                    **kwargs)

