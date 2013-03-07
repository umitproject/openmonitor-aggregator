#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Author: Adriano Monteiro Marques <adriano@umitproject.org>
## Author: Orcun Avsar <orc.avs[at]gmail.com>
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

"""Module containing main shortcut functions to easily send tweets.
"""

import logging

from django.template.loader import render_to_string

from twitter.models import TwitterMessage
from twitter.tasks import send_tweets_task


def send_event_tweet(event):
    tweet = TwitterMessage()
    try:
        tweet.message = render_to_string("notificatonsystem/event_tweet.html", locals())
        tweet.save()
    except Exception, err:
        logging.critical("Failed to save tweet. Error was: %s" % err)
        return

    # The following is going to put the tweet sending task to the background
    # and unblock the current request. If it fails, will try again later,
    # in a cron job that catches the msg sending failures.
    send_tweets_task.delay(tweet.id)


def send_tweet(message):
    tweet = TwitterMessage()
    tweet.message = message
    tweet.save()

    # The following is going to put the tweet sending task to the background
    # and unblock the current request. If it fails, will try again later,
    # in a cron job that catches the msg sending failures.
    send_tweets_task.delay(tweet.id)
