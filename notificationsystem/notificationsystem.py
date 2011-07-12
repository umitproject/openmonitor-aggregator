from django.utils import simplejson
from google.appengine.api import channel
import logging

     
class NotificationInterface:

    def eventReceived(self, event):
        return NotImplemented


class NotificationSystem:

    subscribers = []

    def registerSubscriber(subscriber):
        if isinstance(subscriber, NotificationInterface):
            NotificationSystem.subscribers.append(subscriber)
        else:
            raise TypeError, 'subscriber doesnt implement notification interface'

    def publishEvent(event):
        logging.info(NotificationSystem.subscribers)
        try:
            for subscriber in NotificationSystem.subscribers:
                subscriber.eventReceived(event)
        except Exception,ex:
            logging.error(ex)

    registerSubscriber = staticmethod(registerSubscriber)
    publishEvent = staticmethod(publishEvent)


class RealtimeBox(NotificationInterface):

    def eventReceived(self, event):
        logging.info("event received on realtimebox")
        try:
            message = simplejson.dumps(event.getDict())
            channel.send_message('realtimebox', message)
        except Exception,ex:
            logging.error(ex)


class RealtimeMap(NotificationInterface):

    def eventReceived(self, event):
        logging.info("event received on realtimemap")
        try:
            message = simplejson.dumps(event.getDict())
            channel.send_message('map', message)
        except Exception,ex:
            logging.error(ex)


realtimeBox = RealtimeBox()
realtimeMap = RealtimeMap()
NotificationSystem.registerSubscriber(realtimeBox)
NotificationSystem.registerSubscriber(realtimeMap)