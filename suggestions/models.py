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

from django.db import models
from messages.messages_pb2 import WebsiteSuggestion, ServiceSuggestion


class WebsiteSuggestion(models.Model):
    
    # TODO (Adriano): Another thing we need is to prioritize a region. Users
    # should be allowed to suggest a region to save up resources and make it
    # easier and faster to leverage the results. Let's say china has blocked
    # www.twitter.com, and we get 1k suggestions in one hour. Sure thing we
    # should test www.twitter.com, but if we don't have a location suggestion
    # then we must run that in the other countries that are not blocking the
    # website.
    # Don't get me wrong: we should test the website in the other locations,
    # but with a much lower priority. Countries with high occurrance of
    # censorship records get a higher priority of checking unrelated
    # suggestions, though.
    # TODO (Adriano): Now, we have to decide on how to separate the regions.
    # I think that by country using the english name is the best option, what
    # do you say?
    # Remove my comments once you've read this and linked the list of
    # COUNTRIES to the choices.
    # region = models.CharField(max_length=50, choices=COUNTRIES)

    created_at = models.DateTimeField(auto_now_add=True)
    websiteUrl = models.URLField(max_length=100)
    email      = models.EmailField(blank=True)

    def create(websiteSuggestionMsg):
        suggestion = WebsiteSuggestion()
        suggestion.websiteUrl = websiteSuggestionMsg.websiteURL
        suggestion.email = websiteSuggestionMsg.emailAddress
        suggestion.save()
        return suggestion

    def __unicode__(self):
        return self.websiteUrl

    create = staticmethod(create)


class ServiceSuggestion(models.Model):
    
    # TODO (Adriano): Another thing we need is to prioritize a region. Users
    # should be allowed to suggest a region to save up resources and make it
    # easier and faster to leverage the results. Let's say china has blocked
    # www.twitter.com, and we get 1k suggestions in one hour. Sure thing we
    # should test www.twitter.com, but if we don't have a location suggestion
    # then we must run that in the other countries that are not blocking the
    # website.
    # Don't get me wrong: we should test the website in the other locations,
    # but with a much lower priority. Countries with high occurrance of
    # censorship records get a higher priority of checking unrelated
    # suggestions, though.
    # TODO (Adriano): Now, we have to decide on how to separate the regions.
    # I think that by country using the english name is the best option, what
    # do you say?
    # Remove my comments once you've read this and linked the list of
    # COUNTRIES to the choices.
    # region = models.CharField(max_length=50, choices=COUNTRIES)

    created_at = models.DateTimeField(auto_now_add=True)
    serviceName = models.CharField(max_length=100)
    hostName    = models.CharField(max_length=100)
    ip          = models.CharField(max_length=60)
    email       = models.EmailField(blank=True)

    def create(serviceSuggestionMsg):
        suggestion = ServiceSuggestion()
        suggestion.serviceName = serviceSuggestionMsg.serviceName
        suggestion.hostName = serviceSuggestionMsg.hostName
        suggestion.ip = serviceSuggestionMsg.ip
        suggestion.email = serviceSuggestionMsg.emailAddress
        suggestion.save()
        return suggestion

    def __unicode__(self):
        return self.serviceName

    create = staticmethod(create)