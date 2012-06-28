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
from piston.resource import Resource
from api.handlers import *
from gui.decorators import staff_member_required

registeragent_handler = Resource(RegisterAgentHandler)
getpeerlist_handler = Resource(GetPeerListHandler)
addpeer_handler = Resource(AddPeerHandler)
getsuperpeerlist_handler = Resource(GetSuperPeerListHandler)
getevents_handler = Resource(GetEventsHandler)
sendwebsitereport_handler = Resource(SendWebsiteReportHandler)
sendservicereport_handler = Resource(SendServiceReportHandler)
checkversion_handler = Resource(CheckNewVersionHandler)
checktests_handler = Resource(CheckNewTestHandler)
websitesuggestion_handler = Resource(WebsiteSuggestionHandler)
servicesuggestion_handler = Resource(ServiceSuggestionHandler)
test_handler = Resource(TestsHandler)
checkaggregator_handler = Resource(CheckAggregator)
login_handler = Resource(LoginHandler)
login2_handler = Resource(Login2Handler)
logout_handler = Resource(LogoutHandler)
get_netlist_handler = Resource(GetNetlistHandler)
get_banlist_handler = Resource(GetBanlistHandler)
get_bannets_handler = Resource(GetBannetsHandler)
get_location_handler = Resource(GetLocationHandler)


urlpatterns = patterns('',
   url(r'^registeragent/$', registeragent_handler),
   url(r'^loginagent/$', login_handler),
   url(r'^loginagent2/$', login2_handler),
   url(r'^logoutagent/$', logout_handler),
   url(r'^getpeerlist/$', getpeerlist_handler),
   url(r'^addpeer/$',addpeer_handler),
   url(r'^getsuperpeerlist/$', getsuperpeerlist_handler),
   url(r'^getevents/$', getevents_handler),
   url(r'^sendwebsitereport/$', sendwebsitereport_handler),
   url(r'^sendservicereport/$', sendservicereport_handler),
   url(r'^checkversion/$', checkversion_handler),
   url(r'^checktests/$', checktests_handler),
   url(r'^websitesuggestion/$', websitesuggestion_handler),
   url(r'^servicesuggestion/$', servicesuggestion_handler),
   url(r'^tests/$', staff_member_required(test_handler)),
   url(r'^checkaggregator/$', checkaggregator_handler),
   url(r'^get_netlist/$', get_netlist_handler),
   url(r'^get_banlist/$', get_banlist_handler),
   url(r'^get_bannets/$', get_bannets_handler),
   url(r'^get_location/$', get_location_handler),
   url(r'^$', checkaggregator_handler),
)