from django.conf.urls import patterns, include, url
from pull.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pull.views.home', name='home'),
    # url(r'^pull/', include('pull.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', NewsListView.as_view()),
    url(r'^new/(\d+)/$', NewsSubject),
    url(r'^class/(?P<id>\d+)/$', ClassShow.as_view()),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^p/(?P<path>.*)$', proxy_to),
    #url(r'^task/(?P<id>\d+)$', task_to),
    url(r'^like/(?P<path>.*)$', like_models),
    url(r'^search/(?P<path>.*)$', search_content),
    url(r'^dup$', DupListView.as_view()),
    url(r'^test$', test_page),
)
