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

import logging
import uuid
import datetime

from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings

from gui.decorators import staff_member_required
from utils import send_mail
from notificationsystem.models import *
from notificationsystem.tasks import send_notifications_task


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
    send_notifications_task.delay(notification.id)


def subscribe_to_region(request, region):
    if NotifyOnEvent.subscribe(request.user, region):
        return HttpResponse('OK')
    return HttpResponse('FAILED')


def send_notifications_cron(request):
    """Triggers send_notifications_task to send all unsent email notifications.
    """
    send_notifications_task.delay()
    return HttpResponse("OK")
