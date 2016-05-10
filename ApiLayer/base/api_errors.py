from Common import error_base


class ClientSocketError(error_base.ClientSideError):
    err_type = 'Client'

    def __init__(self, url):
        msg = 'Socket Error. Please check the address and port ' \
              'of your settings. Error URL: ' + url
        super(ClientSocketError, self).__init__(msg=msg)


class ServerProcessError(error_base.ServerSideError):
    err_type = 'Server'

    def __init__(self, err_msg):
        msg = 'Server has experienced an error when ' \
              'processing current request. Message: "' + err_msg + '"'
        super(ServerProcessError, self).__init__(msg=msg)



