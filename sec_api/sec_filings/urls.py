"""URLs to direct requests"""

from django.conf.urls import url

from sec_filings import views


urlpatterns = [
    url(r'^nonderivative/$', views.nonderivative, name='nonderivative'),
    url(r'^accessionnums/$', views.get_accessionnums, name='accessionnums'),
    url(r'^nonderivative/getfeed/$', views.get_feed, name='getfeed'),
    url(r'^nonderivative/newfeed/$', views.new_feed, name='newfeed'),
]
