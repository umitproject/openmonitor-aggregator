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
from django.core.cache import cache
from djangotoolbox.fields import BlobField

from dbextra.fields import ListField

from messages import messages_pb2

TEST_CACHE_KEY = "compiled_test_key_%s"

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
        website_test = WebsiteTest.objects.order_by('created_at')[0:1]
        service_test = ServiceTest.objects.order_by('created_at')[0:1]

        if len(website_test)==0 and len(service_test)>0:
            return service_test.get()
        elif len(service_test)==0 and len(website_test)>0:
            return website_test.get()
        elif len(website_test)>0 and len(service_test)>0:
            if website_test.get().created_at > service_test.get().created_at:
                return website_test.get()
            else:
                return service_test.get()

        return None

    @staticmethod
    def get_updated_tests(last_test_id=0):
        new_tests = []
        website_tests = WebsiteTest.get_updated_tests(last_test_id)
        service_tests = ServiceTest.get_updated_tests(last_test_id)
        new_tests.extend(website_tests)
        new_tests.extend(service_tests)
        return new_tests


class WebsiteTest(Test):
    website_url = models.URLField()

    @staticmethod
    def get_updated_tests(last_test_id=0):
        return WebsiteTestUpdateAggregation.objects.filter(active=True, test_id__gt=last_test_id)
    
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

    @staticmethod
    def get_updated_tests(last_test_id=0):
        return ServiceTestUpdateAggregation.objects.filter(active=True, test_id__gt=last_test_id)
    
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
        agg, created = ServiceTestUpdateAggregation.objects.get_or_create(
                                                test_id=service_test.test_id)
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

class SuggestionSet(models.Model):
    """This model holds the set of suggestions that took place after
    the release of the latest test set. This aggregation is useful on helping us
    figure what is important to keep in or out of the test sets based on
    response to our test sets. Also, it helps us quickly gather this data to
    build the next test set without having to do time consuming queries on the
    datastore.
    """
    class Meta:
        abstract = True
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    test_id = models.IntegerField(null=True)
    version = models.IntegerField(null=True)
    active = models.BooleanField(default=False)
    count_unique = models.IntegerField(default=0)
    count_total = models.IntegerField(default=0)
    
    @classmethod
    def get_set(cls):
        """Returns the latest and active suggestion set.
        """
        return cls.objects.get(active=True)
    
    @classmethod
    def wrapup_set(cls, test_id, version):
        """Closes the currently active set and creates a new one. This should
        *ONLY* be called when a new test set is released.
        """
        sug_set = cls.get_set()
        sug_set.active = False
        sug_set.test_id = test_id
        sug_set.version = version
        sug_set.save()
        
        new_set = cls()
        new_set.active = True
        new_set.save()

class WebsiteSuggestionSet(SuggestionSet):
    """This model holds the set of website suggestions that took place after
    the release of the latest test set. This aggregation is useful on helping us
    figure what is important to keep in or out of the test sets based on
    response to our test sets. Also, it helps us quickly gather this data to
    build the next test set without having to do time consuming queries on the
    datastore.
    """
    website_urls = ListField()
    locations_names = ListField()
    locations = ListField(py_type=int)
    counters = ListField(py_type=int)
    
    @classmethod
    def add_suggestion(cls, website_url, location):
        """Add the suggestion to this set. If suggestion was already made in the
        past, increase its counter.
        """
        cur_set = cls.get_set()
        try:
            index_url = cur_set.website_urls.index(website_url)
            count_url = cur_set.website_urls.count(website_url)
        except ValueError:
            # Website wasn't suggested before
            cur_set.website_urls.append(website_url)
            cur_set.locations_names.append(str(location))
            cur_set.locations.append(location.id)
            cur_set.counters.append(1)
        else:
            if cur_set.locations[index_url] == location.id:
                # This means suggestion already happened for this location
                cur_set.counters[index_url] += 1
            else:
                # It means website was suggested for another region
                cur_set.locations_names.append(str(location))
                cur_set.locations.append(location.id)
                cur_set.counters.append(1)
        
        cur_set.save()

class ServiceSuggestionSet(SuggestionSet):
    """This model holds the set of service suggestions that took place after
    the release of the latest test set. This aggregation is useful on helping us
    figure what is important to keep in or out of the test sets based on
    response to our test sets. Also, it helps us quickly gather this data to
    build the next test set without having to do time consuming queries on the
    datastore.
    """
    service_names = ListField()
    host_names = ListField()
    ips = ListField()
    ports = ListField()
    locations_names = ListField()
    locations = ListField(py_type=int)
    counters = ListField(py_type=int)
    
    @classmethod
    def add_suggestion(cls, service_name, host_name, ip, port, location):
        """Add the suggestion to this set. If suggestion was already made in the
        past, increase its counter.
        """
        cur_set = cls.get_set()
        try:
            index_url = cur_set.website_urls.index(website_url)
        except ValueError:
            # Website wasn't suggested before
            cur_set.website_urls.append(website_url)
            cur_set.locations_names.append(str(location))
            cur_set.locations.append(location.id)
            cur_set.counters.append(1)
        else:
            if cur_set.locations[index_url] == location.id:
                # This means suggestion already happened for this location
                cur_set.counters[index_url] += 1
            else:
                # It means website was suggested for another region
                cur_set.locations_names.append(str(location))
                cur_set.locations.append(location.id)
                cur_set.counters.append(1)
        
        cur_set.save()


class TestSet(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    test_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=False)
    test_set_blob = BlobField()
    
    @property
    def test_set(self):
        test = cache.get(TEST_CACHE_KEY % self.id, False)
        if not test:
            test = messages_pb2.NewTestsResponse()
            test.ParseFromString(self.test_set_blob)
            cache.set(TEST_CACHE_KEY, test)
        return test









