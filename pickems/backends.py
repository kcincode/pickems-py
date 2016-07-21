from api.models import PickemsUser

class EmailAuthBackend(object):
    """
    Email Authentication Backend

    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """

    def authenticate(self, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = PickemsUser.objects.get(email=username)
            if user.check_password(password):
                return user
        except PickemsUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        """ Get a PickemsUser object from the user_id. """
        try:
            return PickemsUser.objects.get(pk=user_id)
        except PickemsUser.DoesNotExist:
            return None
