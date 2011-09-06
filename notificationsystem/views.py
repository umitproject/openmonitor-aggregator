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


from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings

from gui.decorators import staff_member_required

from notificationsystem.models import *


CHECK_NOTIFICATION_KEY = "check_notification_key_%s"


def send_event_email(event):
    notification = EmailNotification()
    notification.event = event
    notification.region = event.region
    notification.build_email_data()
    notification.save()
    
    # The following is going to put the email sending task to the background
    # and unblock the current request. If it fails, will try again later,
    # in a cron job that catches the msg sending failures.
    send_event_emails_task(notification)

def subscribe_to_region(request, region):
    if NotifyOnEvent.subscribe(request.user, region):
        return HttpResponse('OK')
    return HttpResponse('FAILED')

def send_event_emails_task(notification):
    not_key = CHECK_NOTIFICATION_KEY % notification.id
    if cache.get(not_key, False):
        # This means that we still have a processing task for this notification
        logging.critical('Task %s is still processing...' %
                            (CHECK_NOTIFICATION_KEY % notification.id))
        return
    
    try:
        task_name = 'check_notification_%s_%s' % (notification.id, uuid.uuid4())
        task = taskqueue.add(url='/cron/send_notification_task/%s' % notification.id,
                             name= task_name, queue_name='cron')
        if task is None:
            logging.critical("!!!! TASK IS NONE! %s " % task_name)
        
        cache.set(not_key, task)
        
    except taskqueue.TaskAlreadyExistsError, e:
        logging.info('Task is still running for module %s: %s' % \
             (module.name,'/cron/create_notification_queue/%s' % notification.id))

@staff_member_required
def check_notifications(request):
    """This method calls out the tasks to send notifications.
    Since it is a cron called view, there is a timeout, so we might want to
    make sure we never get more notifications than we can handle within that
    timeframe. If we start to get backlogs, then we must create more cron
    entries and call this view more than once per minute.
    """
    notifications = EmailNotification.objects.filter(sent_at=None, send=True).order_by('-created_at')
    
    for notification in notifications:
        send_event_emails_task(notification)
    
    return HttpResponse("OK")

@staff_member_required
def send_notification_task(request, notification_id):
    """This task will send out the notifications
    """
    notification = EmailNotification.objects.get(pk=notification_id)
    notification.build_email_data()
    
    sent = send_mail(settings.NOTIFICATION_SENDER,
                     settings.NOTIFICATION_TO,
                     bcc=notification.list_emails,
                     reply_to=settings.NOTIFICATION_REPLY_TO,
                     subject=notification.subject,
                     body=notification.body,
                     html=notification.html)
    
    notification.sent_at = datetime.datetime.now()
    notification.save()
    
    memcache.delete(CHECK_NOTIFICATION_KEY % notification.id)
    return HttpResponse("OK")
