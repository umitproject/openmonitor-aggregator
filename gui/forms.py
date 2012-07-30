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

from hashlib import md5
import datetime

from django import forms
from django.core.cache import cache

from suggestions.models import WebsiteSuggestion
from suggestions.models import ServiceSuggestion
from geoip.models import Location

from ajax_select import make_ajax_field


EVENT_TYPE = (
    ('censor', 'Censor'),
    ('throttling', 'Throttling'),
    ('offline', 'Offline'),
)


LOCATION_HELP_TEXT = ("Where do you think it is being blocked? "
                      "Leave empty if you want a world-wide check.")

WEBSITE_HELP_TEXT = ("The website you think we should check.")

SERVICE_NAME_HELP_TEXT = ("Service name. Eg: ssh, ftp, pop3, imap...")

HOST_NAME_HELP_TEXT = ("Address through which we can reach this service, "
                       "without the protocol part. Eg: ftp.test.com instead "
                       "ftp://ftp.test.com")

PORT_HELP_TEXT = ("Port number through which the service should be accessed.")


DOUBLE_REQUEST_PERIOD = 60*60*24*1  #User can't submit same suggestion before 1 day
REQUEST_FORM_KEY = "request_form_%s_%s"  #ip and hash of the value of the fields


class CantRepeat(object):

    def init_repeat_check(self, request, Form, fields):
        self._request = request
        self._Form = Form
        self._fields = fields

    def do_repeat_check(self):
        digest = md5(''.join([self._request.POST.get(f) for f in self._fields]))
        digest = digest.hexdigest()

        key = REQUEST_FORM_KEY % (self._request.META['REMOTE_ADDR'], digest)

        is_cached = cache.get(key, False)
        if is_cached:
            raise forms.ValidationError(("You can send this form only once. "
                                         "Thank you for helping!"))
        else:
            cache.set(key, self._Form, DOUBLE_REQUEST_PERIOD)


class BaseSuggestionForm(forms.Form):

    def clean_location(self ):
        data = self.cleaned_data['location']
        if not data:
            return None
        try:
            return Location.objects.filter(fullname__startswith=data)[0]
        except IndexError:
            raise forms.ValidationError("Location doesn't exists!")


class SuggestWebsiteForm(BaseSuggestionForm, CantRepeat):
    website = forms.CharField(max_length=300, required=True,
                              help_text=WEBSITE_HELP_TEXT)
    location = make_ajax_field(WebsiteSuggestion, 'location_id', 'location',
                               label='Location', help_text=LOCATION_HELP_TEXT)

    def clean(self):
        self.do_repeat_check()
        return super(SuggestWebsiteForm, self).clean()


class SuggestServiceForm(forms.Form, CantRepeat):
    host_name = forms.CharField(max_length=300, required=True,
                                help_text=HOST_NAME_HELP_TEXT)
    service_name = forms.CharField(max_length=20, required=True,
                                   help_text=SERVICE_NAME_HELP_TEXT)
    port = forms.IntegerField(required=True, help_text=PORT_HELP_TEXT)
    location = forms.CharField(max_length=300, required=False,
                               help_text=LOCATION_HELP_TEXT)

    def clean(self):
        self.do_repeat_check()
        return super(SuggestServiceForm, self).clean()


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
