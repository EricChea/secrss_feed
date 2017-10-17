"""eldorado_webapp URL Configuration
"""

from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^sec/', include('sec_filings.urls')),
    url(r'^admin/', admin.site.urls),
]
