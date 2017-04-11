from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import (AbstractUser, PermissionsMixin, UserManager as DefaultUserManager)
from django.contrib.postgres.fields import CICharField, CIEmailField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
import pytz

from . import validators


TIME_ZONE_CHOICES = zip(pytz.common_timezones, pytz.common_timezones)


class UserManager(DefaultUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        elif not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, is_staff=is_staff,
                          is_superuser=is_superuser, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        return self._create_user(username=username, email=email, password=password,
                                 is_staff=False, is_superuser=False, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(username=username, email=email, password=password,
                                 is_staff=True, is_superuser=True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = CICharField(_('username'), max_length=128, unique=True,
                           help_text=_('Username must match the name in the game IL-2 (including squad tag).'),
                           # validators=[validators.username],
                           error_messages={'unique': _('A user with that username already exists.')})
    email = CIEmailField('Email', unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))

    tz = models.CharField(_('timezone'), max_length=64, blank=True, choices=TIME_ZONE_CHOICES)

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    # def set_password(self, raw_password):
    #     super().set_password(raw_password=raw_password)
