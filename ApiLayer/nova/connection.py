__author__ = 'pwwpcheng'

from django.conf import settings

from ApiLayer.base.connection_base import openstack_api_connection


def nova_connection(project_id, base_url, method, header, url_parameters=None, body=None):
    if project_id is None or project_id == '':
        raise KeyError(message='Project_id must be provided for Nova API')
    return _nova_connection(base_url, method, header,
                            url_parameters=url_parameters, body=body,
                            project_id=project_id)

def _nova_connection(*args, **kwargs):
    '''
    Specify endpoint settings for openstack connection
    '''
    return openstack_api_connection(*args,
                                    port=settings.NOVA_PORT,
                                    version='v2',
                                    tenant_id=kwargs.pop('project_id'),
                                    **kwargs)