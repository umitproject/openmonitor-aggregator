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

import urllib2 as urlfetch

EmailMessage = None

def send_mail(sender, to, cc='', bcc='', reply_to='', subject='', body='', html='', attachments=[], headers={}):
    #if settings.GAE:
    #    return _gae_send_mail(sender, to, cc, bcc, reply_to, subject, body, html, attachments, headers)
    pass

def _gae_send_mail(sender, to, cc=None, bcc=None, reply_to=None, subject='', body='', html='', attachments=[], headers={}):
    email = EmailMessage()
    email.sender = sender
    email.to = to
    email.subject = subject
    email.body = body
    if cc: email.cc = cc
    if bcc: email.bcc = bcc
    if reply_to: email.reply_to = reply_to
    if html: email.html = html
    if attachments: email.attachments = attachments
    if headers: email.headers = headers
    
    return email.send()


def fetch(url):
    result = urlfetch.urlopen(url)
    return result

def fetch_status(url):
    response = fetch(url)
    return response.getcode()

def fetch_response(url):
    response = fetch(url)
    return response.read()

def fetch_response_status(url):
    response = fetch(url)
    return response.read(), response.getcode()

def fetch_obj(url):
    """Return objects from json outputs retrived by a given url.
    """
    return json.loads(fetch_response(url))