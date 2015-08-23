from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import views as auth_views, get_user_model, REDIRECT_FIELD_NAME, login as auth_login
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, resolve_url
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST
from django.utils.encoding import force_text
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _

from . import mail
from .decorators import no_login_required
from .forms import (RegistrationForm, AuthenticationForm, PasswordResetForm,
                    SetPasswordForm, ProfileForm, RegistrationConfirmForm)
from .models import User


@never_cache
@no_login_required(redirect_url='/')
@sensitive_post_parameters('password')
def login(request):
    redirect_to = request.GET.get(REDIRECT_FIELD_NAME, '')
    form = AuthenticationForm(request, request.POST or None)
    if form.is_valid():
        # Ensure the user-originating redirection url is safe.
        if not is_safe_url(url=redirect_to, host=request.get_host()):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
        # Okay, security check complete. Log the user in.
        auth_login(request, form.get_user())
        if not form.cleaned_data['remember_me']:
            request.session.set_expiry(0)
        return redirect(redirect_to)
    return render(request, 'users/login.html', {'form': form, REDIRECT_FIELD_NAME: redirect_to})


@never_cache
@login_required
@require_POST
def logout(request):
    # update_session_auth_hash(request=request, user=request.user)
    return auth_views.logout(request)


@never_cache
@no_login_required(redirect_url='/profile/')
@sensitive_post_parameters('password')
def registration(request):
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        if settings.SEND_EMAIL:
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            mail.registration_confirm(user=user, domain=request.get_host())
            return render(request, 'users/info_page_template.html', {
                'page_title': _('Registration'),
                'page_content': _('We send to your email address message with a link to confirm your registration.'),
            })
        else:
            form.save()
            messages.success(request, _('Your registration has been confirmed. Now you can login.'))
            return redirect('users:login')
    return render(request, 'users/registration.html', {'form': form})


@never_cache
@no_login_required(redirect_url='/profile/')
def registration_confirm(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, _('Your registration has been confirmed. Now you can login.'))
        return redirect('users:login')
    else:
        return render(request, 'users/info_page_template.html', {
            'page_title': _('Registration'),
            'page_content': _('Incorrect link to confirm your registration.'),
        })


@never_cache
@no_login_required(redirect_url='/profile/')
def registration_confirm_repeat(request):
    if not settings.SEND_EMAIL:
        return HttpResponseForbidden()

    form = RegistrationConfirmForm(request.POST or None)
    if form.is_valid():
        user = User.objects.get(email=form.cleaned_data['email'])
        mail.registration_confirm(user=user, domain=request.get_host())
        return render(request, 'users/info_page_template.html', {
            'page_title': _('Registration'),
            'page_content': _('We send to your email address message with a link to confirm your registration.'),
        })
    return render(request, 'users/registration_confirm_repeat.html', {'form': form})


@never_cache
@no_login_required(redirect_url='/profile/')
def password_reset(request):
    if not settings.SEND_EMAIL:
        return HttpResponseForbidden()

    form = PasswordResetForm(request.POST or None)
    if form.is_valid():
        user = User.objects.get(email=form.cleaned_data['email'])
        mail.password_reset(user=user, domain=request.get_host())
        return render(request, 'users/info_page_template.html', {
            'page_title': _('Password reset'),
            'page_content': _('We send to your email address message with a link to reset password.'),
        })
    return render(request, 'users/password_reset.html', {'form': form})


@never_cache
@no_login_required(redirect_url='/profile/')
@sensitive_post_parameters()
def password_reset_confirm(request, uidb64, token):
    if not settings.SEND_EMAIL:
        return HttpResponseForbidden()

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        form = SetPasswordForm(request.POST or None, user=user)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            messages.success(request, _('Password successfully changed. Now you can login.'))
            return redirect('users:login')
        else:
            return render(request, 'users/password_reset_confirm.html', {'form': form})
    else:
        return render(request, 'users/info_page_template.html', {
            'page_title': _('Password reset unsuccessful'),
            'page_content': _('Retry a using link from the email or start the password reset procedure again.'),
        })


@never_cache
@login_required
@sensitive_post_parameters('new_password', 'current_password')
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if form.is_valid():
        user = form.save()
        # Updating the password logs out all other sessions for the user except the current one if
        # django.contrib.auth.middleware.SessionAuthenticationMiddleware is enabled.
        update_session_auth_hash(request=request, user=user)
        messages.success(request, _('Profile successfully changed.'))
        return redirect(request.path)
    return render(request, 'users/profile.html', {'form': form})
