from django.core import validators
from django.utils.translation import ugettext as _

username = validators.RegexValidator(
    r'^[0-9a-zA-Z\.\@\+\-]+$',
    _('Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.'), 'invalid')
