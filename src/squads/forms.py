import imghdr

from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _

from stuff.decorators import form_autofocus
from .models import Squad


# http://nldr.net/python/django/2015/11/17/limiting-file-upload-size-in-django-forms.html
MAX_FILE_SIZE = 50 * 1024  # 50KB
MAX_FILE_SIZE_STR = '{0}KB'.format(int(MAX_FILE_SIZE / 1024))

ALLOWED_FILE_FORMATS = ['png', 'jpeg']
ALLOWED_FILE_FORMATS_STR = ', '.join(ALLOWED_FILE_FORMATS)


@form_autofocus(field='name')
class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Squad
        fields = ('name', 'tag')

    def clean_tag(self):
        tag = self.cleaned_data.get('tag')
        if Squad.objects.filter(tag=tag, is_removed=False).exists():
            raise forms.ValidationError(_('A squad with that tag already exists.'))
        return tag


class ProfileForm(forms.ModelForm):
    rm_logo = forms.BooleanField(label=_('Remove logo'), required=False)

    class Meta:
        model = Squad
        fields = ['name', 'tag', 'website', 'logo', 'rm_logo', 'about']
        widgets = {'logo': forms.FileInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.logo:
            self.fields['rm_logo'].widget = forms.HiddenInput()

    def clean_tag(self):
        tag = self.cleaned_data.get('tag')
        if Squad.objects.filter(tag=tag, is_removed=False).exclude(id=self.instance.pk).exists():
            raise forms.ValidationError(_('A squad with that tag already exists.'))
        return tag

    def clean_logo(self):
        uploaded_file = self.cleaned_data['logo']
        if uploaded_file:
            if uploaded_file._size > MAX_FILE_SIZE:
                raise forms.ValidationError(_('Maximum file size: %(size)s') % {'size': MAX_FILE_SIZE_STR})
            if imghdr.what(uploaded_file) not in ALLOWED_FILE_FORMATS:
                raise forms.ValidationError(_('Allowed file formats are: %(formats)s') %
                                            {'formats': ALLOWED_FILE_FORMATS_STR})
        return uploaded_file
