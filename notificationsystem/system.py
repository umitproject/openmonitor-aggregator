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

import logging
import decimal

import simplejson

#TODO(orc.avs): implement channel equivalent with HTTP polling.
#from google.appengine.api import channel

from twitter.main import send_event_tweet
from notificationsystem.views import send_event_email

class NotificationInterface:
    def eventReceived(self, event):
        return NotImplemented


class NotificationSystem:
    subscribers = []

    @staticmethod
    def registerSubscriber(subscriber):
        if isinstance(subscriber, NotificationInterface):
            NotificationSystem.subscribers.append(subscriber)
        else:
            raise TypeError, 'subscriber doesnt implement notification interface'

    @staticmethod
    def publishEvent(event):
        logging.info(NotificationSystem.subscribers)
        logging.info(">>> Publishing events: %s" % event)

        for subscriber in NotificationSystem.subscribers:
            try:
                subscriber.eventReceived(event)
            except Exception,ex:
                logging.error("Error on notification system: %s" % subscriber)
                logging.error(ex)


class RealtimeBox(NotificationInterface):
    def eventReceived(self, event):
	'''
        logging.info("event received on realtimebox")
        try:
            message = simplejson.dumps(event.get_dict(), use_decimal=True)
            channel.send_message('realtimebox', message)
        except Exception,ex:
            logging.error(ex)
	'''
	pass


class RealtimeMap(NotificationInterface):
    def eventReceived(self, event):
	'''
        logging.info("event received on realtimemap")
        try:
            logging.info("%s,%s" % (event.lats[0], event.lons[0]))
            message = simplejson.dumps(event.get_dict(), use_decimal=True)
            channel.send_message('map', message)
        except Exception,ex:
            logging.error(ex)
	'''
	pass


class EmailNotification(NotificationInterface):
    def eventReceived(self, event):
        logging.info("event received on email notification")
        send_event_email(event)


class TwitterNotification(NotificationInterface):
    def eventReceived(self, event):
        logging.info("event received on twitter notification")
        send_event_tweet(event)


realtimeBox = RealtimeBox()
realtimeMap = RealtimeMap()
emailNotification = EmailNotification()
twitterNotification = TwitterNotification()

NotificationSystem.registerSubscriber(realtimeBox)
NotificationSystem.registerSubscriber(realtimeMap)
NotificationSystem.registerSubscriber(emailNotification)
NotificationSystem.registerSubscriber(twitterNotification)
