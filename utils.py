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

from django.conf import settings
from django.utils import simplejson as json

urlfetch = None

if settings.GAE:
    from google.appengine.api import urlfetch
else:
    import urllib2 as urlfetch

def fetch(url):
    if settings.GAE:
        result = urlfetch.fetch(url,
                                follow_redirects=True,
                                allow_truncated=True,
                                deadline=60)
        return result
    
    
    ##########################
    # Outside GAE environment
    
    result = urlfetch.urlopen(url)
    return result

def fetch_status(url):
    response = fetch(url)
    
    if settings.GAE:
        return response.status_code
    
    ##########################
    # Outside GAE environment
    
    return response.getcode()

def fetch_response(url):
    response = fetch(url)
    
    if settings.GAE:
        return response.content
    
    ##########################
    # Outside GAE environment
    
    return response.read()

def fetch_response_status(url):
    response = fetch(url)
    
    if settings.GAE:
        return response.content, response.status_code
    
    ##########################
    # Outside GAE environment
    
    return response.read(), response.getcode()

def fetch_obj(url):
    """Return objects from json outputs retrived by a given url.
    """
    return json.loads(fetch_response(url))