__author__ = 'pwwpcheng'

from django.conf import settings
from ApiLayer.connection_base import openstack_api_connection

def ceilometer_connection(base_url, method, header, url_parameters=None, body=None):
    return _ceilometer_connection(base_url, method, header,
                                  url_parameters=url_parameters,
                                  body=body
                                  )

def _ceilometer_connection(*args, **kwargs):
    return openstack_api_connection(*args,
                                    port=settings.CEILOMETER_PORT,
                                    version='v2',
                                    **kwargs)

