from django.contrib.auth.models import update_last_login
import datetime
from api.models import NflGame

def jwt_response_payload_handler(token, user=None, request=None):
    if user:
        # if the last_login is set, update it.
        if user.last_login:
            update_last_login(None, user)

    now = datetime.datetime.now()
    game = NflGame.objects.filter(starts_at__gte=now).order_by('starts_at').first()
    current_week = 21 if not game else games.week

    return {'access_token': token, 'user_id': user.id, 'current_week': current_week}
