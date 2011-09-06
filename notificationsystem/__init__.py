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

from notificationsystem.models import Notification
from notificationsystem.views import send_event_emails_task

def send_event_email(event):
    notification = Notification()
    notification.event = event
    notification.region = event.region
    notification.build_email_data()
    notification.save()
    
    # The following is going to put the email sending task to the background
    # and unblock the current request. If it fails, will try again later,
    # in a cron job that catches the msg sending failures.
    send_event_emails_task(notification)