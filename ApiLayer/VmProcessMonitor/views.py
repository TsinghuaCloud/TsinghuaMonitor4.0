__author__ = 'pwwpcheng'
import api
import json
from django.http import HttpResponse

from Common import error_base as err
from Common import decorators

@decorators.login_required
def get_process_list(request, instance_id):
    token_id = request.session['token'].id
    project_id = request.session['token'].project['id']
    monitor_conn = api.VMProcessMonitor(token_id, project_id, instance_id)

    try:
        data = monitor_conn.get_data()
        return HttpResponse(json.dumps(data), content_type='application/json')
    except (err.ClientSideError, err.ServerSideError), e:
        return HttpResponse(json.dumps(_report_error(e)),
                            content_type='application/json')


def _report_error(e):
    return {
        'status': 'error',
        'error_msg': e.msg
    }