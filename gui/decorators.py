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

from django.contrib.auth.decorators import login_required as django_login_required
from django.contrib.admin.views.decorators import staff_member_required as django_staff_member_required
from django.conf import settings

def login_required(view):
    if not settings.DEBUG:
        return django_login_required(view)
    return view

def staff_member_required(view):
    if not settings.DEBUG:
        def new_view(request, *args, **kwargs):
            # This is in order to bypass authentication if this header is present,
            # which indicates that appengine's cron is issuing this command
            if settings.GAE and request.META.get("X-AppEngine-Cron", False) == "true":
                return view(request, *args, **kwargs)
            return django_staff_member_required(view)(request, *args, **kwargs)
        return new_view
    return view
