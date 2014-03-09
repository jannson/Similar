# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class TestLog(models.Model):
    post_id = models.IntegerField()
    guid = models.CharField(max_length=40L)
    uaction = models.CharField(max_length=3L)
    pos = models.CharField(max_length=5L)
    shiduan = models.IntegerField()
    ctime = models.IntegerField()
    class Meta:
        db_table = 'xxhh_testlog'

class XhLogUd(models.Model):
    id = models.IntegerField(primary_key=True)
    post_id = models.IntegerField()
    guid = models.CharField(max_length=40L)
    uaction = models.CharField(max_length=3L)
    pos = models.CharField(max_length=5L)
    shiduan = models.IntegerField()
    ctime = models.IntegerField()
    class Meta:
        db_table = 'xh_log_ud'

