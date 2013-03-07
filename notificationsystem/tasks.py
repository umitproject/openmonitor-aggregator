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

"""Module containing notifications tasks.
"""

import datetime

from django.conf import settings

from celery.task import task

from notificationsystem.models import EmailNotification
from utils import send_mail


@task()
def send_notifications_task(notification_id=None):
    """Task that sends out notifications.
    """

    if notification_id:
        notifications = [EmailNotification.objects.get(pk=notification_id)]
    else:
        notifications = EmailNotification.objects.filter(
            sent_at=None, send=True).order_by('-created_at')

    for notification in notifications:
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

    return "OK"
