# -*- coding: utf-8 -*-

import re
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
import zerorpc

class PositiveBigIntegerField(models.BigIntegerField):
    empty_strings_allowed = False
    description = _("Big (8 byte) positive integer")

    def db_type(self, connection):
        """
        Returns MySQL-specific column data type. Make additional checks
        to support other backends.
        """
        return 'bigint UNSIGNED'

    def formfield(self, **kwargs):
        defaults = {'min_value': 0,
                    'max_value': BigIntegerField.MAX_BIGINT * 2 - 1}
        defaults.update(kwargs)
        return super(PositiveBigIntegerField, self).formfield(**defaults)

class Category(models.Model):
    name=models.CharField(max_length=50, unique=True)

#status: 0:ok,1:dup,2:req,3:url_error,4:parse_error,5:exists_url
class HtmlContent(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=250, unique=True)
    #hash = models.BigIntegerField(unique=True)
    hash = PositiveBigIntegerField()
    tags = models.CharField(max_length=200)
    category = models.ManyToManyField(Category, blank=True)
    summerize = models.CharField(max_length=400)
    classify = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    preview = models.TextField()
    status = models.IntegerField()

    def get_title(self):
        return re.split(r'[-_|]', self.title)[0]
    def get_dup(self):
        return find_duplicate(self.hash)

class SogouCorpus(models.Model):
    content = models.TextField()
    tokens = models.TextField()
    classify = models.CharField(max_length=100)

def find_duplicate(hash):
    #TODO for zerorpc
    hashm = zerorpc.Client('tcp://localhost:5678')
    sims = hashm.find_all(hash)[0][1]
    sims = list(set(sims))
    return HtmlContent.objects.filter(hash__in=sims)
