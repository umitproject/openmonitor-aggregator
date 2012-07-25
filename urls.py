#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Author: Adriano Monteiro Marques <adriano@umitproject.org>
## Author: Diogo Pinheiro <diogormpinheiro@gmail.com>
##
## Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

from django.conf.urls.defaults import *
from django.contrib import admin

from ajax_select import urls as ajax_select_urls

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    url(r'', include('gui.urls')),
    url(r'', include('geoip.urls')),
    url(r'^events/poll$', 'gui.views.poll_active_events'),
    url(r'^map/$', 'gui.views.map'),
    url(r'^realtimebox/$', 'gui.views.realtimebox'),
    url(r'^events/(?P<event_id>\d+)/$', 'gui.views.event'),
    url(r'^twitter/', include('twitter.urls')),
    url(r'^accounts/', include('registration.urls')),
    url(r'^notification/', include('notificationsystem.urls')),
    url('^manifesto/?$', 'gui.views.manifesto', name='manifesto'),
    
    url(r'^api/', include('api.urls')),
    url(r'^decision/', include('decision.urls')),
    url(r'^agents/', include('agents.urls')),
    url(r'^ajax/lookups/', include(ajax_select_urls)),
    url(r'^admin/', include(admin.site.urls)),
)
