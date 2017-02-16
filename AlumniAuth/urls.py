"""
Definition of urls for AlumniAuth.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views
from django.views.decorators.csrf import csrf_exempt


import app.forms
import app.views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()


urlpatterns = [
    url(r'^$', app.views.index),
    url(r'^(?P<code_param>57-.+)$', app.views.index),
    url(r'^invite/new$', app.views.generate_code),
    url(r'^invite/(?P<inv_idx>\d+)$', app.views.invite),
    url(r'^new-code$', app.views.generate_code),
    url(r'^code/(?P<inv_idx>\d+)$', app.views.invite, {'self_issued': True}),
    url(r'^switch/(?P<inv_idx>\d+)$', app.views.switch),
    url(r'^disable/(?P<inv_idx>\d+)$', app.views.disable),
    url(r'^api/get_alumni/', app.views.get_alumni, name='get_alumni'),
    url(r'^enter$', app.views.enter),
    url(r'^clear$', app.views.clear),

    url(r'^api/v1/check_code$', csrf_exempt(app.views.check_code)),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls))
]
