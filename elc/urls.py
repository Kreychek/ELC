from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

admin.autodiscover()

# site-wide URLs
urlpatterns = patterns('',
    url(r'^records/', include('marketanalyzer.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^upload_progress/$', 'marketanalyzer.views.upload_progress', name='upload_progress'),
    url(r'^lookup/$', 'marketanalyzer.views.type_lookup'),  # autocomplete view
    url(r'^lp_lookup/$', 'marketanalyzer.views.lp_lookup'),  # autocomplete view
)