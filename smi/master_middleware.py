import json as js
import jwt as JWT
from django.conf import LazySettings
from django.http import HttpRequest
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
        if request.method == 'GET':
            return self.get_response(request)

        jwt = JWT.JWT()
        jason = js.loads(request.body)
        a = jason['msg']

        print('-=-=-=-=-=-=-=-=-=-=-')
        print(settings.SECRET_KEY)
        print('-=-=-=-=-=-=-=-=-=-=-')

        key = JWT.jwk.OctetJWK(key=settings.SECRET_KEY.encode('utf-8'), kid=1)
        decoded_json = jwt.decode(a, key)
        new_body = js.dumps(decoded_json)

        print('-=-=-=-=-=-=-=-=-=-=-')
        print(new_body)
        print('-=-=-=-=-=-=-=-=-=-=-')

        new_request = HttpRequest()
        new_request.POST = new_body
        new_request.META.update(request.META)

        print('-=-=-=-=-=-=-=-=-=-=-')
        print('HUASHUASHUASASHUAHSUASU')
        print(new_request.POST)
        print('-=-=-=-=-=-=-=-=-=-=-')


        response = self.get_response(new_request)
        return response
