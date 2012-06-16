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

from django.db import models
from datetime import datetime

class SoftwareVersion(models.Model):
    released_at = models.DateTimeField(auto_now_add=True)
    version  = models.IntegerField()
    url      = models.URLField(max_length=255, verify_exists=False)

    class Meta:
        abstract = True


class DesktopAgentVersion(SoftwareVersion):

    def getLastVersionNo():
        # TODO (Adriano): Use memcache to store this version indefinitely and
        # create signals to revogate cache once a new version is added
        try:
            return DesktopAgentVersion.objects.order_by('-version')[0:1].get()
        except DesktopAgentVersion.DoesNotExist:
            p = DesktopAgentVersion(released_at=datetime.now(),version=1,url="http://alpha.openmonitor.org/")
            return p;

    def __unicode__(self):
        return "Desktop Agent v" + str(self.version)

    getLastVersionNo = staticmethod(getLastVersionNo)


class MobileAgentVersion(SoftwareVersion):

    def getLastVersionNo():
        # TODO (Adriano): Use memcache to store this version indefinitely and create signals 
        # to revogate cache once a new version is added
        try:
            return MobileAgentVersion.objects.order_by('-version')[0:1].get()
        except MobileAgentVersion.DoesNotExist:
            p = MobileAgentVersion(released_at=datetime.now(),version=1,url="http://alpha.openmonitor.org/")
            return p;

    def __unicode__(self):
        return "Mobile Agent v" + str(self.version)

    getLastVersionNo = staticmethod(getLastVersionNo)
