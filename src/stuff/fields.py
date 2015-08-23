from django.db.models import fields


# class CaseInsensitiveTextField(fields.TextField):
#
#     def db_type(self, connection):
#         return 'citext'


class CaseInsensitiveCharField(fields.CharField):

    def db_type(self, connection):
        return 'citext'


class CaseInsensitiveEmailField(fields.EmailField):

    def db_type(self, connection):
        return 'citext'
