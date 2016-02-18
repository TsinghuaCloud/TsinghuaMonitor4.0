__author__ = 'pwwpcheng'

import copy

def qdict_to_dict(qdict):
    '''Convert a Django QueryDict to a Python dict.
    Referenced from: http://stackoverflow.com/questions/13349573/how-to-change-a-django-querydict-to-python-dict
    Single-value fields are put in directly, add for multi-value fields, a list
    of all values is stored at the field's key.
    :param qdict: <QueryDict>
    :return: (Dict) python dict
    '''
    return {k[:-2] if k[len(k) - 2:] == '[]' else k: v if k[len(k) - 2:] == '[]' else v[0]
            for k, v in qdict.lists()}

def sanitize_arguments(filter, capabilities):
    f = copy.copy(filter)
    return {k: v for k, v in f.iteritems() if k in capabilities}


def kwargs_to_url_parameter_object(**kwargs):
    '''
    Convert kwargs into q (list(Query))
    :param kwargs:
    :return: (Dict) Filter rules for the data to be returned
    Example:
        kwargs = {'resource_id': 'computer001'}
    '''
    url_parameters_object = {}
    if 'limit' in kwargs.iterkeys():
        url_parameters_object['limit'] = kwargs.pop('limit')
    if 'skip' in kwargs.iterkeys():
        url_parameters_object['skip'] = kwargs.pop('skip')
    q = []
    for k, v in kwargs.iteritems():
        q.append({'field': k, 'value': v})
    url_parameters_object['q'] = q
    return url_parameters_object


def url_para_to_url(**kwargs):
    '''
    Convert query parameters into url string,
    limit & skip are directly written into url_parameters.
    Other parameters are reformatted into {'field': <key>, 'value': <value>}
    :param kwargs: (Dict) query criteria, e.g. limit, skip, resource_id, meter_name etc.
    :return: url: (String) converted url
    '''
    if kwargs is None or len(kwargs) == 0:
        return ''
    else:
        complete_url = ''
        if kwargs.get('limit'):
            complete_url = complete_url + 'limit=' + str(kwargs.pop('limit')) + '&'
        if kwargs.get('skip'):
            complete_url = complete_url + 'skip=' + str(kwargs.pop('skip')) + '&'
        if kwargs.get('q'):
            q = kwargs.pop('q')
            for item in q:
                complete_url = complete_url + 'q.field=%s&q.value=%s&' \
                                              % (item['field'], item['value'])
        complete_url = '?' + complete_url
        return complete_url[:-1]