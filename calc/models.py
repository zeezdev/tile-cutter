from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _


class Result(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("Result name"))
    data = JSONField(verbose_name=_("Data"))
    result = JSONField(verbose_name=_("Result"))
    ip = models.GenericIPAddressField(verbose_name=_("Client IP"))
    ts = models.DateTimeField(verbose_name=_("Timestamp"), auto_now_add=True)

    def __str__(self):
        return self.name
