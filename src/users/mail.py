from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from django.utils.translation import ugettext_lazy as _


DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


def _send_mail(subject, message, email):
    send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list=[email], fail_silently=False)


def registration_confirm(user, domain):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user=user)
    url = reverse('users:registration_confirm', kwargs={'uidb64': uid, 'token': token})
    full_url = 'http://{domain}{url}'.format(domain=domain, url=url)

    _send_mail(
        subject=_('IL2 stats: registration confirm'),
        email=user.email,
        message=_('Confirmation of registration: %(url)s') % {'url': full_url},
    )


def password_reset(user, domain):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user=user)
    url = reverse('users:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    full_url = 'http://{domain}{url}'.format(domain=domain, url=url)

    _send_mail(
        subject=_('IL2 stats: password reset'),
        email=user.email,
        message=_('Password reset: %(url)s') % {'url': full_url},
    )
