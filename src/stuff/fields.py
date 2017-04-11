from django.contrib.postgres.fields import CIEmailField, CICharField
# from django.db.models import fields


CaseInsensitiveCharField = CICharField
CaseInsensitiveEmailField = CIEmailField


# class CaseInsensitiveCharField(fields.CharField):
#
#     def db_type(self, connection):
#         return 'citext'
#
#
# class CaseInsensitiveEmailField(fields.EmailField):
#
#     def db_type(self, connection):
#         return 'citext'
