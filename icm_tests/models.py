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
    test_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=False)

    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        new = self.id is None
        
        super(Test, self).save(*args, **kwargs)
        
        if new and self.version == 1:
            # First version of a test is got the id of the test.
            # Subsequent versions of this test will carry the id of the original
            self.test_id = self.id
            self.save()

    @staticmethod
    def get_last_test():
        return Test.objects.order_by('created_at')[0:1].get()

    @staticmethod
    def get_updated_tests():
        new_tests = []
        website_tests = WebsiteTest.get_updated_tests()
        service_tests = ServiceTest.get_updated_tests()
        new_tests.extend(website_tests)
        new_tests.extend(service_tests)
        return new_tests


class WebsiteTest(Test):
    website_url = models.URLField()

    @staticmethod
    def get_updated_tests():
        return WebsiteTestUpdateAggregation.objects.filter(active=True)
    
    def save(self, *args, **kwargs):
        super(WebsiteTest, self).save(*args, **kwargs)
        WebsiteTestUpdateAggregation.update_aggregation(self)

    def __unicode__(self):
        return "%s (%s) - %s" % (self.description, self.website_url,
                                 "Active" if self.active else "Inactive")

class WebsiteTestUpdateAggregation(models.Model):
    """This aggregation hold only the latest tests version for each test. It is
    safe to filter it out by active if you want to. You'll only get one latest
    version of each test in this case.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    test_id = models.IntegerField()
    website_test_id = models.IntegerField(null=True)
    version = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    website_url = models.URLField()
    active = models.BooleanField(default=False)
    
    @property
    def website_test(self):
        return WebsiteTest.objects.get(id=self.website_test_id)
    
    @staticmethod
    def update_aggregation(website_test):
        agg, created = WebsiteTestUpdateAggregation.objects.get_or_create(test_id=website_test.test_id)
        if agg.id is None or agg.version < website_test.version:
            agg.version = website_test.version
            agg.website_test_id = website_test.id
            agg.description = website_test.description
            agg.website_url = website_test.website_url
            agg.active = website_test.active
            created = True
        elif agg.active != website_test.active:
            agg.active = website_test.active
            created = True
        
        if created:
            agg.save()
        
        return agg
    
    def __unicode__(self):
        return "%s (%s) - %s" % (self.description, self.website_url,
                                 "Active" if self.active else "Inactive")

class ServiceTest(Test):
    service_name = models.TextField()
    ip = models.TextField()
    port  = models.PositiveIntegerField()
    
    def save(self, *args, **kwargs):
        super(ServiceTest, self).save(*args, **kwargs)
        ServiceTestUpdateAggregation.update_aggregation(self)

    def __unicode__(self):
        return "%s (%s) - %s" % (self.description, self.service_name,
                                 "Active" if self.active else "Inactive")

class ServiceTestUpdateAggregation(models.Model):
    """This aggregation hold only the latest tests version for each test. It is
    safe to filter it out by active if you want to. You'll only get one latest
    version of each test in this case.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    test_id = models.IntegerField()
    service_test_id = models.IntegerField(null=True)
    version = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    service_name = models.TextField()
    ip = models.TextField()
    port = models.PositiveIntegerField()
    active = models.BooleanField(default=False)
    
    @property
    def service_test(self):
        return ServiceTest.objects.get(id=self.service_test_id)
    
    @staticmethod
    def update_aggregation(service_test):
        agg, created = ServiceTestUpdateAggregation.objects.get_or_create(test_id=service_test.test_id)
        if agg.id is None or agg.version < service_test.version:
            agg.version = service_test.version
            agg.service_test_id = service_test.id
            agg.description = service_test.description
            agg.service_name = service_test.service_name
            agg.ip = service_test.ip
            agg.port = service_test.port
            agg.active = service_test.active
            created = True
        elif agg.active != service_test.active:
            agg.active = service_test.active
            created = True
        
        if created:
            agg.save()
        
        return agg

    def __unicode__(self):
        return "%s (%s) - %s" % (self.description, self.service_name,
                                 "Active" if self.active else "Inactive")
