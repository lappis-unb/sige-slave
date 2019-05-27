from jwt import JWT


class CommsMiddleware(object):
    """
    Middleware for parsing and validate the json web token from the master's
    request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        jwt = JWT()
        if request.method == 'GET':
            print('============================================ GET')
            return self.get_response(request)
        print('============================================ POST')
        decoded_json = jwt.decode(request.data, SECRET_KEY)
        response = self.get_response(decoded_json)
        return response
