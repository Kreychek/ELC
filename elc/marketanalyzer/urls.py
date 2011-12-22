from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView

# for dev server only
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from marketanalyzer.models import MarketRecord

# TO DO: better naming scheme

# marketanalyzer-specific URLs
urlpatterns = patterns('marketanalyzer.views',
    #url(r'^$',
    #    ListView.as_view(   # generic view
    #        queryset = MarketRecord.objects.order_by('-lastUpdated')[:5],
    #        context_object_name = 'latest_rec_list',
    #        template_name = 'records/index.html')),
    url(r'^$', 'search'),
    url(r'^all/$','all'),
    url(r'^all_buy/$','all_buy'),
    url(r'^all_sell/$','all_sell'),
    #url(r'^(?P<pk>\d+)/$',
    #    DetailView.as_view( # generic view
    #        model=MarketRecord,
    #        context_object_name = 'record',
    #        template_name = 'records/record_detail.html')),
    url(r'^upload/$', 'upload'),
    url(r'^clear_db/$', 'clear_db'),
    url(r'^clear_lp_db/$', 'clear_lp_db'),
    url(r'^search/$', 'search'),
    #url(r'^search/(?P<pk>\d+)/$', 'search'),
    url(r'^type_detail/(?P<type_id>\d+)/$', 'type_detail'),
    url(r'^lp_calc/$', 'lp_calc'),
    url(r'^import_lp/$', 'import_lp_data'),
    url(r'^lp_search/$', 'lp_search'),
    url(r'^lp_detail/(?P<type_id>\d+)/$', 'lp_detail'),
    url(r'^set_theme/$', 'set_theme')
    #url(r'^lookup/$', 'type_lookup'),
)

# for dev server only
#urlpatterns += staticfiles_urlpatterns()