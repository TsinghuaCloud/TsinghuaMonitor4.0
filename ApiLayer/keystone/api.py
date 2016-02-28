import json
import urllib2

from django.conf import settings

def get_token(tenant_name=None, username=None, password=None):
    '''
    Since the only reason for utilizing Keystone endpoint is  to get a token,
    thus, we create a separate urllib2 connection for handling this function.
    :param tenant_name: (string) Name of the project
    :param username: (string)
    :param password: (string)
    :return: (Dictionary Object) Server's result
    '''
    request = urllib2.Request('http://%s:%s/v2.0/tokens' %
                              (settings.OPENSTACK_CONTROLLER_IP, settings.KEYSTONE_PORT))
    request.add_header('Content-Type', 'application/json')
    request.add_data('{"auth":{"tenantName": "%s","passwordCredentials":{"username": "%s","password": "%s"}}}' % (
        tenant_name, username, password))
    try:
        handle = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        return {'status': 'error',
                'reason': 'HTTPCode: %s, Message: %s' % (e.code, e.msg)}
    except urllib2.URLError as e:
        return {'status': 'error',
                'reason': e.reason}

    token = json.loads(handle.read())['access']['token']['id']
    return {'status': 'success',
            'token': token}