import pytest
from mock import Mock
from django.test import TestCase
from django.conf import settings

from middlewares.master_middleware import *

# https://medium.com/@adamdonaghy/unit-testing-django-middleware-2e8cb26e06ca


class RequestMiddlewareTestCase(TestCase):
    def setUp(self):
        # see about the constructor here
        self.middleware = RequestMiddleware(get_response)
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
        # see about the constructor here
        self.middleware = ResponseMiddleware(get_response)
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
