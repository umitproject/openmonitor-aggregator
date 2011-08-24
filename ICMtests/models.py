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

class Test(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    testID       = models.IntegerField(primary_key=True)
    description  = models.TextField(blank=True)

    def getLastTestNo():
        return Test.objects.order_by('-testID')[0:1].get()

    def getUpdatedTests(lastTestNo):
        newTests = []
        websiteTests = WebsiteTest.objects.filter(test__testID__gt=lastTestNo)
        serviceTests = ServiceTest.objects.filter(test__testID__gt=lastTestNo)
        newTests.extend(websiteTests)
        newTests.extend(serviceTests)
        return newTests

    getLastTestNo   = staticmethod(getLastTestNo)
    getUpdatedTests = staticmethod(getUpdatedTests)


class WebsiteTest(models.Model):
    test       = models.ForeignKey('Test')
    websiteURL = models.URLField()

    def __unicode__(self):
        return "%s (%s)" % (self.test.description, self.websiteURL)


class ServiceTest(models.Model):
    test        = models.ForeignKey('Test')
    serviceCode = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s (%s)" % (self.test.description, self.serviceCode)
