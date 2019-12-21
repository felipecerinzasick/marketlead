from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import MultipleObjectsReturned
from social_django.models import UserSocialAuth


class UserManager(BaseUserManager):
    """
    To create users from command line and from register, reworked the base django user manager.
    Base user manager: django.contrib.auth.model.UserManager
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_verified') is not True:
            raise ValueError('Superuser must have is_verified=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Customized user model, for changing base username field to email
    """
    USERNAME_FIELD = 'email'    # default user field is email
    REQUIRED_FIELDS = []    # replaced base required field 'username'
    objects = UserManager()

    # username will no longer be a required field
    username = models.CharField(
        max_length=255,
        blank=True, null=True
    )

    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': "This email address is already registered. Please try a new one",
        },
    )

    is_verified = models.BooleanField(
        verbose_name='verified',
        default=False,
        help_text='Email verification',
    )

    def __str__(self):
        return self.email

    def get_social_auth_obj(self):
        try:
            return UserSocialAuth.objects.get(user=self)
        except UserSocialAuth.DoesNotExist:
            pass
        except MultipleObjectsReturned:
            pass
        return None

    def get_access_token(self):
        if self.is_authenticated:
            usa = self.get_social_auth_obj()
            if usa:
                access_token = usa.extra_data.get('access_token')
                if access_token:
                    return access_token
        return ''

