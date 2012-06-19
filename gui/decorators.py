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

from django.contrib.auth.decorators import login_required as django_login_required
from django.contrib.admin.views.decorators import staff_member_required as django_staff_member_required
from django.conf import settings
from django.core.cache import cache
from django.utils import simplejson as json
from django.http import HttpResponse

DOUBLE_REQUEST_PERIOD = 60*60*24*1  #User can't submit same suggestion before 1 day
REQUEST_FORM_KEY = "request_form_%s_%s"  #ip and hash of the value of the fields

class cant_repeat_form(object):
    """Views that have this decorator must have a different signature.
    The first two arguments after the request are the form with the data and
    a boolean indicating whether the form validated or not.
    
    This:
    def view(request, *args, **kwargs):
    
    Becomes this:
    def view(request, form, valid, *args, **kwargs):
    
    It also, must return a json with a key named status, returning OK or FAILED.
    If this key is OK, then we'll store the form and make sure user can't resend
    it again withing the DOUBLE_REQUEST_PERIOD time.
    """
    
    def __init__(self, form_class, fields):
        self.form_class = form_class
        self.fields = fields
    
    def __call__(self, view):
        def new_view(request, *args, **kwargs):
            form = None
            valid = False
            
            if request.is_ajax():
                form = self.form_class(request.POST)
                valid = form.is_valid()
                
                if valid:
                    request_key = REQUEST_FORM_KEY % (request.META['REMOTE_ADDR'],
                         md5(''.join([request.POST.get(f) for f in self.fields])).hexdigest())
                    is_cached = cache.get(request_key, False)
                    
                    if is_cached:
                        return HttpResponse(json.dumps(dict(status='FAILED',
                                msg='You can send this form only once. Thank you for helping!')))
                    
                    response = view(request, form, valid, *args, **kwargs)
                    
                    if response.status_code == 403:
                        response = HttpResponse(json.dumps({'status':'FAILED', 'msg':'Sorry. Failed to check if you\'re sending from site.'}))
                    else:
                        result = json.loads(response.content)
                        if result.get('status', 'FAILED') == 'OK':
                            cache.set(request_key, form, DOUBLE_REQUEST_PERIOD)
                    
                    return response
            
            return view(request, form, valid, *args, **kwargs)
        return new_view


def login_required(view):
    if not settings.DEBUG:
        return django_login_required(view)
    return view

def staff_member_required(view):
    if not settings.DEBUG:
        def new_view(request, *args, **kwargs):
            # TODO: MIGRATE THIS TO WORK WITH EC2
            # This is in order to bypass authentication if this header is present,
            # which indicates that appengine's cron is issuing this command
            #if settings.PRODUCTION and request.META.get("X-AppEngine-Cron", False) == "true":
            #    return view(request, *args, **kwargs)
            return django_staff_member_required(view)(request, *args, **kwargs)
        return new_view
    return view
