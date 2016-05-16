__author__ = 'pwwpcheng'

from django.conf import settings

from ApiLayer.base.connection_base import UrllibConnection
from ApiLayer.base import api_errors as err

class VMProcessMonitor(object):
    openstack_token = None
    project_id = None
    instance_id = None
    conn = None

    def __init__(self, token, project_id, instance_id):
        self.project_id = project_id
        self.openstack_token = token
        self.instance_id = instance_id
        params = {
            'addr': settings.PROCESS_MONITOR_ADDR,
            'port': settings.PROCESS_MONITOR_PORT,
            'token': self.openstack_token,
            'tenant': self.project_id,
            'instance': instance_id,
        }
        url = 'http://%(addr)s:%(port)s/process_list?'\
            'openstack_token=%(token)s&tenant_id=%(tenant)s&'\
            'instance_id=%(instance)s' % params
        self.conn = UrllibConnection(url=url)

    def get_data(self):
        data = self.conn.get_data()
        if data['status'] == 'success':
            return data['data']
        else:
            raise err.ServerProcessError(data['error_msg'])




