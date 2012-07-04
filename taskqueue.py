#!/usr/bin/python
# -*- coding utf-8 -*-

"""Module containing thread for receiving/executing tasks on rabbitMQ queue.
"""

import threading
import warnings
import simplejson as json
import urllib, urllib2

try:
    from django.conf import settings
    HOST_IP = settings.HOST_IP
    PORT = settings.PORT
    TASKQUEUE_SECRET_KEY = settings.TASKQUEUE_SECRET_KEY
except ImportError:
    HOST_IP = '127.0.0.1'
    PORT = 8000
    TASKQUEUE_SECRET_KEY = '123456'

try:
    import pika
    PIKA = True
except ImportError:
    PIKA = False
    warnings.warn(("module 'pika' not found, ignoring taskqueue calls. "
                   "Install RabbitMQ and pika!"), ImportWarning)


"""Following is a monkey-patch to fix the issue #137.
see: https://github.com/pika/pika/issues/137
"""
#START OF MONKEY-PATCH
from pika.callback import CallbackManager

if not hasattr(CallbackManager, 'sanitize'):
    def sanitize(self, key):
        if hasattr(key, 'method') and hasattr(key.method, 'NAME'):
            return key.method.NAME

        if hasattr(key, 'NAME'):
            return key.NAME

        if hasattr(key, '__dict__') and 'NAME' in key.__dict__:
            return key.__dict__['NAME']

        return str(key)

    CallbackManager.sanitize = sanitize  # monkey-patch
#END OF MONKEY-PATCH


class TaskRunner(threading.Thread):

    def runTask(self, *args, **kwargs):
        """Callback for running all the tasks.

        A task is consist of a URL and parameters to send with the request.
        Task runner simply makes local HTTP calls for each task.
        """
        try:
            self.run_task(*args, **kwargs)
        except Exception, e:
            logging.error("RABBITMQ ERROR: "+e.__class__.__name__+"-"+e.message)

    def runTask_(self, ch, method, properties, body):
        message = json.loads(body)
        url = message['url']
        parameters = message['parameters']
        urllib2.urlopen('http://%s:%s%s' % (HOST_IP, PORT, url),
                        data=urllib.urlencode(parameters))

    def run(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='taskqueue')

        channel.basic_consume(
            self.runTask, queue='taskqueue', no_ack=True)
        channel.start_consuming()


def add(url='', parameters={}, **kwargs):

    if not PIKA:
        return None

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='taskqueue')

    parameters['SECRET_KEY'] = TASKQUEUE_SECRET_KEY
    message = json.dumps({'url': url, 'parameters': parameters})
    channel.basic_publish(
        exchange='', routing_key='taskqueue', body=message)
    connection.close()


def init(daemon=True):
    if PIKA:
        thread = TaskRunner()
        thread.daemon = daemon
        thread.start()


if __name__ == "__main__":
    #DO SOME TESTS
    init(daemon=False)
    add('/dsads')
    add()
