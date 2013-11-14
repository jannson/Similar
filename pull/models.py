# -*- coding: utf-8 -*-

import re
from django.db import models
from django.contrib.auth.models import User

class HtmlContent(models.Model):
    title=models.CharField(max_length=200)
    url=models.URLField(max_length=250, unique=True)
    retry = models.IntegerField()
    tags=models.CharField(max_length=200)
    summerize=models.CharField(max_length=400)
    content=models.TextField()
    preview=models.TextField()
