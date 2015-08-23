import functools

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, resolve_url

from .models import SquadMember


def squad_member_required(redirect_url=None, admin=False):
    def func_wrapper(view):
        @functools.wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.user.is_authenticated:
                try:
                    squad_member = request.user.squad_member
                    if admin and not squad_member.is_admin:
                        return HttpResponseForbidden()
                    return view(request, *args, **kwargs)
                except SquadMember.DoesNotExist:
                    if redirect_url:
                        return redirect(redirect_url)
                    else:
                        return HttpResponseForbidden()
            else:
                return redirect_to_login(next=request.build_absolute_uri())
        return wrapped
    return func_wrapper
