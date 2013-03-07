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
from django.core.mail import EmailMessage, EmailMultiAlternatives

urlfetch = None

import urllib2 as urlfetch


def send_mail(sender, to, cc='', bcc='', reply_to='', subject='',
              body='', html='', attachments=[], headers={}):
    """Attachments list is in the following format:
    [["filename.png", file_data, "image/png"], ...]
    """
    message = EmailMessage()
    if html:
        message = EmailMultiAlternative()
        message.attach_alternative(html)

    message.subject = subject
    message.body = body
    message.from_email = sender
    message.to = to if type(to) == type([]) else [to]
    message.cc = cc if type(cc) == type([]) else [cc]
    message.bcc = bcc if type(bcc) == type([]) else [bcc]
    for attachment in attachments:
        message.attach(*attachment)
    message.headers = headers

    message.send()
    

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
