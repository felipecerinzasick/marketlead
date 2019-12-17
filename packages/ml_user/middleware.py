from django.contrib.auth import get_user_model


class EmailAuthBackend(object):
    """
    Custom Email Backend to perform authentication via email
    """
    User = get_user_model()

    def authenticate(self, username=None, password=None):
        try:
            user = self.User.objects.get(email=username)
            if user.check_password(password): # check valid password
                return user # return user to be authenticated
        except self.User.DoesNotExist: # no matching user exists
            return None

    def get_user(self, user_id):
        try:
            return self.User.objects.get(pk=user_id)
        except self.User.DoesNotExist:
            return None

