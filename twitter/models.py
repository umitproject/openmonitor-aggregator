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

from django.db import models
from django.core.cache import cache


class TwitterMessage(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    message = models.CharField(max_length=140)
    sent = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s - %s" % (self.message, "SENT" if self.sent else "NOT SENT")


class TwitterAccount(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account = models.CharField(max_length=50)
    api_key = models.CharField(max_length=200)
    consumer_key = models.CharField(max_length=200)
    consumer_secret = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200)
    access_secret = models.CharField(max_length=200)

    def __unicode__(self):
        return "@%s" % self.account

    @staticmethod
    def get_twitter_account():
        twitter_account = cache.get("twitter_account", False)
        if not twitter_account:
            twitter_account = TwitterAccount.objects.all()
            if not twitter_account:
                twitter_account = None
            else:
                twitter_account = twitter_account[0]
                cache.set("twitter_account", twitter_account, 120)
        return twitter_account
