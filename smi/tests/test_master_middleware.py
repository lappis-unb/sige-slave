import pytest
from mock import Mock
from django.conf import TestCase
from django.conf import settings

from smi.master_middleware import *

# https://medium.com/@adamdonaghy/unit-testing-django-middleware-2e8cb26e06ca


class RequestMiddlewareTestCase(TestCase):
    def setUp(self):
        self.middleware = RequestMiddleware()
        self.request = Mock()
        self.request.META = {
            "HTTP_PROFILE_ID": self.profileId,
            "REQUEST_METHOD": "POST",
            "HTTP_USER_AGENT": "AUTOMATED TEST"
        }
        self.request.path = ''
        self.request.session = {}

    def test_request_processing(self):
        pass


class ResponseMiddlewareTestCase(TestCase):
    def setUp(self):
        self.middleware = ResponseMiddleware()
        self.request = Mock()
        self.request.META = {
            "HTTP_PROFILE_ID": self.profileId,
            "REQUEST_METHOD": "GET",
            "HTTP_USER_AGENT": "AUTOMATED TEST"
        }
        self.request.path = ''
        self.request.session = {}

    def test_request_processing(self):
        pass
