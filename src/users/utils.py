import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone


def cleanup_registration():
    User = get_user_model()
    expiration_date = timezone.now() - datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
    for u in User.objects.filter(is_active=False, date_joined__lt=expiration_date):
        u.delete()
