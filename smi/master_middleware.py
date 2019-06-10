import json as js
import jwt as JWT
from django.conf import LazySettings
from django.http import HttpRequest
from io import BytesIO

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response


settings = LazySettings()


class CommsMiddleware(object):
    """
    Middleware for parsing and validate the json web token from the master's
    request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            if request.method == 'GET':
                return self.get_response(request)

            jwt = JWT.JWT()
            jason = js.loads(request.body)
            enc_token = jason['msg']

            key = JWT.jwk.OctetJWK(
                key=settings.SECRET_KEY.encode('utf-8'), kid=1)

            decoded_json = js.dumps(jwt.decode(enc_token, key))
            new_body = js.dumps(decoded_json)

            request._body = decoded_json.encode()

            response = self.get_response(request)
            return response

        except:
            return self.get_response(request)
