from calendar import monthrange

from django import template

from .. import utils


register = template.Library()


@register.filter()
def seconds_to_time(value, arg='hm'):
    return utils.seconds_to_time(value, arg)


@register.filter()
def days_in_month(value):
    return monthrange(value.year, value.month)[1]


@register.filter()
def widget_type(field):
    return field.field.widget.__class__.__name__.replace('Input', '').lower()
    # return field.field.widget.input_type
