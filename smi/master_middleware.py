import json as js
import jwt as JWT
from django.conf import LazySettings
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
        print(settings.SECRET_KEY)
        key = JWT.jwk.OctetJWK(key=settings.SECRET_KEY.encode('utf-8'), kid=1)
        decoded_json = jwt.decode(a, key)
        new_body = js.dumps(decoded_json)
        print(new_body)
        request.update(body=new_body)
        # request.body = new_body

        response = self.get_response(request)
        return response
