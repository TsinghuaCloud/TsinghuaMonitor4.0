from django.test import TestCase
from django.test import Client

# Create your tests here.
csrf_client = Client(enforce_csrf_checks=True)
print csrf_client.cookies