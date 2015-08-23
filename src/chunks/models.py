from django.db import models
from django.utils.translation import ugettext_lazy as _


class Chunk(models.Model):
    key = models.CharField(_('key'), max_length=32, primary_key=True,
                           help_text=_('A unique name for this chunk of content'))
    title = models.CharField(_('title'), max_length=255, blank=True)
    content = models.TextField(_('content'), blank=True)

    class Meta:
        db_table = 'chunks'

    def __unicode__(self):
        return self.key
