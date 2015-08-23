from collections import namedtuple
from copy import copy

from django import forms
from django.contrib.auth import authenticate, forms as auth_forms
from django.contrib.auth import password_validation
from django.utils.translation import ugettext, ugettext_lazy as _

from stuff.decorators import form_autofocus
from .models import User


FakeUser = namedtuple('FakeUser', ['username', 'email'])


@form_autofocus(field='username')
class AuthenticationForm(auth_forms.AuthenticationForm):
    remember_me = forms.BooleanField(label=_('Remember me'), required=False, initial=True)


@form_autofocus(field='username')
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    aircraft = forms.CharField(label=_('Protection from bots'), required=False,
                               help_text=_('Enter number associated with correct part of the aircraft.'))

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_aircraft(self):
        aircraft = self.cleaned_data.get('aircraft')
        if aircraft != '3':
            raise forms.ValidationError(_('Incorrect answer.'))
        return aircraft

    def clean_password(self):
        password = self.cleaned_data.get('password')
        self.instance.username = self.cleaned_data.get('username')
        self.instance.email = self.cleaned_data.get('email')
        password_validation.validate_password(password, self.instance)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


@form_autofocus(field='email')
class RegistrationConfirmForm(forms.Form):
    email = forms.EmailField(label=_('Email'), max_length=254)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(_('A user with this email is not found.'))
        if user.is_active:
            raise forms.ValidationError(_('Registration has already been confirmed. This user is activated.'))
        return email


@form_autofocus(field='email')
class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_('Email'), max_length=254)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(_('A user with this email is not found.'))
        return email


@form_autofocus(field='new_password')
class SetPasswordForm(forms.Form):
    new_password = forms.CharField(label=_('New password'), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        password_validation.validate_password(password, self.instance)
        return password


class ProfileForm(forms.ModelForm):
    new_password = forms.CharField(label=_('New password'), widget=forms.PasswordInput, required=False)
    current_password = forms.CharField(label=_('Current password'), widget=forms.PasswordInput, required=False,
                                       help_text=_('To change the email or password you must enter current password.'))

    class Meta:
        model = User
        fields = ('username', 'tz', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(kwargs['instance'], 'profile'):
            del self.fields['username']

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            instance = copy(self.instance)
            instance.username = self.cleaned_data.get('username')
            instance.email = self.cleaned_data.get('email')
            password_validation.validate_password(new_password, instance)
        return new_password

    def clean(self):
        email = self.cleaned_data.get('email')
        new_password = self.cleaned_data.get('new_password')
        if email != self.instance.email or new_password:
            current_password = self.cleaned_data.get('current_password')
            if not current_password:
                self.add_error('current_password',
                               _('To change the email or password you must enter current password.'))
            elif not self.instance.check_password(raw_password=current_password):
                self.add_error('current_password', _('Incorrect current password.'))
        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['new_password']:
            user.set_password(self.cleaned_data['new_password'])
        if commit:
            user.save()
        return user
