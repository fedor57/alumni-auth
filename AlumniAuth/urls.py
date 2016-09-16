"""
Definition of urls for AlumniAuth.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views


import app.forms
import app.views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()


urlpatterns = [
    url(r'^$', app.views.askcode),
    url(r'^(?P<code>57-[\w\-]+)$', app.views.invite),
    url(r'^api/get_alumni/', app.views.get_alumni, name='get_alumni'),
    url(r'^api/generate_code/', app.views.generate_code),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls))
]
