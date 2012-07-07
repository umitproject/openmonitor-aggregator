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

"""Tasks related to twitter.
"""

import logging
import time
import urllib

from django.http import HttpResponse
from django.utils import simplejson as json
from celery.task import task

import oauth2 as oauth
from twitter.models import TwitterAccount
from twitter.models import TwitterMessage


def do_send_tweet(tweet):
    """Called by send_tweets_task to make the API call into Twitter.
    """

    params = {"status":tweet.message}
    url = "http://api.twitter.com/1/statuses/update.json"
    method = "POST"
    twitter_account = TwitterAccount.get_twitter_account()

    if twitter_account is None:
        logging.error(("No twitter account object was created."
                       "Can't send tweets!"))
        return False

    consumer = oauth.Consumer(key=twitter_account.consumer_key,
                              secret=twitter_account.consumer_secret)
    token = oauth.Token(key=twitter_account.access_token,
                        secret=twitter_account.access_secret)

    auth_params = {
        'oauth_version': "1.0",
        'oauth_nonce': oauth.generate_nonce(),
        'oauth_timestamp': int(time.time()),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_token': token.key,
        'oauth_consumer_key': consumer.key,
    }

    client = oauth.Client(consumer, token)
    req = oauth.Request(method=method, url=url, parameters=params)
    resp, content = client.request(url, method=method,
            body=urllib.urlencode(params, True).replace('+', '%20'),
            headers=req.to_header(),
            force_auth_header=True)

    if resp['status'][0] == '5':
        return False

    return True


@task()
def send_tweets_task(tweet_id=None):
    """Task to send a specific tweet or all waiting tweets to the Twitter.
    """

    if tweet_id: #send a specific tweet
        tweets = [TwitterMessage.objects.get(id=tweet_id)]
    else:
        tweets = TwitterMessage.objects.filter(
            sent=False, locked=False).order_by("-updated_at")

    for tweet in tweets:
        response = do_send_tweet(tweet)

        if not response:
            # Twitter seems unavailable for the moment
            logging.error("Couldn't send tweet: %s" % tweet.message)
            tweet.locked = False
            tweet.save()
            # Will run again and retry on next cronjob trigger

        else:
            tweet.sent = True
            tweet.save()
