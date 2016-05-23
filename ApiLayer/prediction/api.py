from mongoengine import *
from SitePages.models import VM
from bson import json_util
import json
from django.core.serializers.json import DjangoJSONEncoder

def get_prediction_data(_name,_meter):
    '''
    Get prediction data from MongoDB
    :param _name: (string) name of VM
    :param _meter: (string) meter name
    :return:
    '''
    vms=VM.objects(Q(name=_name) & Q(meter=_meter))
    return vms