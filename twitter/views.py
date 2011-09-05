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

import time
import urllib

from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson as json

import oauth2 as oauth

from twitter.models import *


def send_tweet_task(tweet):
    """This is a non-blocking method safe to be called from anywhere in our
    views. If we need to suddenly send a tweet, use this method and it will
    send the task to background and continue processing. If sending fails,
    our cron job will manage to retry later.
    """
    task = None
    
    try:
        task_name = 'send_tweet_%s' % tweet.id
        task = taskqueue.add(url='/tasks/send_tweet_task/%s' % tweet.id,
                             name=task_name, queue_name='twitter')
        tweet.locked = True
        tweet.save()
        
        logging.info('Scheduled task %s' % task_name)
    except taskqueue.TaskAlreadyExistsError, e:
        logging.info('Task is still running for tweet %s: %s' % \
             (tweet.id, '/cron/send_tweet_task/%s' % tweet.id))
    
    return task

def send_tweet_cron(request):
    tweets = TwitterMessage.objects.filter(sent=False, locked=False).order_by("-created_at", "-updated_at")
    
    for tweet in tweets:
        task = create_send_tweet_task(tweet)
    
    return HttpResponse("OK")

def send_tweet_task(request, tweet_id):
    tweet = TwitterMessage.objects.get(pk=tweet_id)
    resp = send_tweet(tweet)
    
    if not resp:
        # Twitter unavailable for the moment.
        # Try again later.
        tweet.locked = False
        tweet.save()
    else:
        tweet.sent = True
        tweet.save()
    
    return HttpResponse("OK")

def send_tweet(tweet):
    params = {"status":tweet.message}
    url = "http://api.twitter.com/1/statuses/update.json"
    method = "POST"
    
    return call_twitter(url, method, params)

def call_twitter(url, method, params):
    twitter_account = get_twitter_account()
    
    if twitter_account is None:
        logging.warning(">>> No twitter account object was created. Can't send tweets!")
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
