# -*- coding: utf-8 -*-

import re
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name=models.CharField(max_length=50, unique=True)

class HtmlContent(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=250, unique=True)
    retry = models.IntegerField()
    tags = models.CharField(max_length=200)
    category = models.ManyToManyField(Category, blank=True)
    summerize = models.CharField(max_length=400)
    content = models.TextField()
    preview = models.TextField()

    def get_title(self):
        return re.split(r'[-_|]', self.title)[0]
