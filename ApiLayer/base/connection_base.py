import httplib
import json
import socket
import urllib2

from django.conf import settings
from Common import BaseMethods
from ApiLayer.base import api_errors as err

def openstack_api_connection(base_url, method, header, port, version,
                             tenant_id=None, url_parameters=None, body=None):
    '''
    :param url: (string)
    :param method: (string) [POST | GET | PUT | DELETE ]
    :param header: (Dict) headers for request
    :param url_parameters: (Dict)
    :param body: (Dict)
    :return: (Dict) Data fetched from openstack api
    '''
    extra_url = (BaseMethods.url_para_to_url(**url_parameters)) if url_parameters else ''
    conn = httplib.HTTPConnection('%s:%s' % (settings.OPENSTACK_CONTROLLER_IP, port))
    req_header = header
    req_body = None if body is None else json.dumps(body)

    # Perform API request
    status = None
    data = None
    # TODO(pwwp):
    # use <finally> to handle success or error data
    try:
        conn.request(method, '/%s/' % version +
                             (('%s/' % tenant_id) if tenant_id is not None else '') +
                             base_url + extra_url,
                     headers=req_header, body=req_body)
        response = conn.getresponse()
        if response.status > 299:
            error = {'status': 'error',
                     'error_code': response.status,
                     'error_msg': response.reason,
                     'data': ''}
            return error
        elif response.status == 204:
            data = {'status': 'success',
                    'data': ''}
            return data
        else:
            data = {'status': 'success',
                    'data': json.loads(response.read())}
            return data
    except socket.error, e:
        return {'status': 'error',
                'error_msg': e.strerror
                }
    except httplib.HTTPException, e:
        return {'status': 'error',
                'error_msg': e.message
                }

class urllib_connection(object):
    url = None
    headers = None
    body = None
    urllib_request = None

    def __init__(self, url, headers=None, body=None):
        self.url = url
        self.headers = {} if headers is None else headers
        self.body = body
        print url
        self.urllib_request = urllib2.Request(url=self.url, data=self.body,
                                              headers=self.headers)

    def get_data(self):
        '''
        Convert returned data into python dict if data is json string.
        Directly return data  if data is not json string.
        '''
        resp = urllib2.urlopen(self.urllib_request)
        data = resp.read()

        try:
            return json.loads(data)
        except TypeError, e:
            return None
        except ValueError, e:
            return data
        except socket.error, e:
            raise err.ClientSocketError(self.url)

