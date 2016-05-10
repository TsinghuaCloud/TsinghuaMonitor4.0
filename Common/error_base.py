__author__ = 'pwwpcheng'


class Error(Exception):
    code = None
    msg = None
    type = None
    diagnose = None

    def __init__(self, code, msg, diagnose=None):
        self.code = code
        self.msg = msg
        self.diagnose = diagnose


class ClientSideError(Error):
    err_type = 'Client'

    def __init__(self, msg, code=None, diagnose=None):
        _code = 400 if code is None else code
        msg = '[Client Error] ' + str(msg)
        super(ClientSideError, self).__init__(_code, msg, diagnose)


class ServerSideError(Error):
    err_type = 'Server'

    def __init__(self, msg, code=None, diagnose=None):
        _code = 400 if code is None else code
        msg = '[Server Error] ' + str(msg)
        super(ServerSideError, self).__init__(_code, msg, diagnose)
