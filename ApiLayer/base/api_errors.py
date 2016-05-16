from Common import error_base


class ServerAddressError(error_base.ServerSideError):
    err_type = 'server'

    def __init__(self, host_port):
        msg = 'Server is temporarily unavailable. Please check' \
              'your config. Host-port : ' + host_port
        super(ServerAddressError, self).__init__(msg=msg)


class ClientSocketError(error_base.ClientSideError):
    err_type = 'client'

    def __init__(self, url):
        msg = 'Socket Error. Please check the address and port ' \
              'of your settings. Error URL: ' + url
        super(ClientSocketError, self).__init__(msg=msg)


class HttpLibError(error_base.ClientSideError):
    err_type = 'Client'

    def __init__(self, error_class_name, url, msg):
        _msg = 'HTTPLib exception encountered. Exception Type: ' \
               '%s. Url: "%s". Message: "%s".' % (error_class_name, url, msg)
        super(HttpLibError, self).__init__(msg=_msg)


class ServerProcessError(error_base.ServerSideError):
    err_type = 'Server'

    def __init__(self, err_msg):
        msg = 'Server has experienced an error when ' \
              'processing current request. Message: "' + err_msg + '"'
        super(ServerProcessError, self).__init__(msg=msg)


class AlarmDoesNotExist(error_base.ClientSideError):
    def __init__(self, alarm_id):
        msg = 'Alarm does not exist. Alarm ID: ' + alarm_id
        super(AlarmDoesNotExist, self).__init__(msg=msg)


class ResourceNotFound(error_base.ClientSideError):
    def __init__(self, url):
        msg = '404 Error. Resource not found. Url: ' + url
        super(ResourceNotFound, self).__init__(msg=msg)