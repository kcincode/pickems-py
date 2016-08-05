from django.contrib.auth.models import update_last_login

def jwt_response_payload_handler(token, user=None, request=None):
    if user:
        # if the last_login is set, update it.
        if user.last_login:
            update_last_login(None, user)

    return {'access_token': token}
