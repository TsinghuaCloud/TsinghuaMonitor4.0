from django.db import models
from mongoengine import *

# Create your models here.
class Data(EmbeddedDocument):
    date = StringField()
    predicted_value = StringField()
    actual_value = StringField()

class VM(Document):
    _id = StringField()
    id = StringField()
    name = StringField()
    meter = StringField()
    current_time = StringField()
    data = ListField(EmbeddedDocumentField(Data))
