# -*- coding: UTF-8 -*-
import sys, os, os.path

HERE = os.path.dirname(os.path.abspath(__file__))

#root_path = os.path.join(HERE,'pull')
root_path = HERE
sys.path.insert(13, root_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pull.settings'

from django.db.models.loading import get_model
from django.db.models import Count
from django.db.models import Q
from pull.models import *

the_model_string = 'pull.HtmlContent'
the_model = get_model ( *the_model_string.split('.',1) )
objects = the_model.objects
print objects.in_bulk([1,2,3,4,5])
