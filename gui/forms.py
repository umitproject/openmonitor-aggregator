#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Author: Adriano Monteiro Marques <adriano@umitproject.org>
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

import datetime
from django import forms

from suggestions.models import WebsiteSuggestion
from suggestions.models import ServiceSuggestion

from ajax_select import make_ajax_field


EVENT_TYPE = (
    ('censor', 'Censor'),
    ('throttling', 'Throttling'),
    ('offline', 'Offline'),
)

class SuggestWebsiteForm(forms.Form):
    website = forms.CharField(max_length=300, required=True)
    location = make_ajax_field(WebsiteSuggestion, 'location_id', 'location', label='Location')

class SuggestServiceForm(forms.Form):
    host_name = forms.CharField(max_length=300, required=True)
    service_name = forms.CharField(max_length=20, required=True)
    port = forms.IntegerField(required=True)
    location = forms.CharField(max_length=300, required=False)

class WebsiteEventForm(forms.Form):
    website = forms.CharField(max_length=300, required=True)
    location = forms.CharField(max_length=300, required=True)
    first_detection = forms.DateTimeField(initial=datetime.date.today, required=False)
    event_type = forms.ChoiceField(choices=EVENT_TYPE, required=False)

class ServiceEventForm(forms.Form):
    service = forms.CharField(max_length=300, required=True)
    location = forms.CharField(max_length=300, required=True)
    first_detection = forms.DateTimeField(initial=datetime.date.today, required=False)
    event_type = forms.ChoiceField(choices=EVENT_TYPE, required=False)
