from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    ('^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}),
    (r'^map/$', 'gui.views.map'),
    (r'^realtimebox/$', 'gui.views.realtimebox'),
    (r'^send/$', 'gui.views.send'),
    (r'^admin/', include(admin.site.urls)),
    (r'^api/', include('api.urls')),
)
