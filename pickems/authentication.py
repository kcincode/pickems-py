from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication

class JSONWebTokenQsAuthentication(BaseJSONWebTokenAuthentication):
    def get_jwt_value(self, request):
        # try to login using the query parameters
        jwt = request.query_params.get('jwt')

        if not jwt and request.META.get('HTTP_AUTHORIZATION'):
            # fall back to header verification
            jwt = request.META.get('HTTP_AUTHORIZATION')[4:]

        return jwt
