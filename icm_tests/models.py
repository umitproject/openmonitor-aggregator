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
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from dbextra.fields import ListField
from geoip.models import Location


class Test(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=False)
    location_id = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        abstract = True

    @property
    def location(self):
        if not self.location_id:
            return None
        else:
            return Location.objects.get(pk=self.location_id)

    @staticmethod
    def create_from_suggestion(suggestion):
        raise NotImplementedError

    @staticmethod
    def get_test_version(agent):
        version_sum = 0

        if not agent:
            return 0

        # Latest version is sum of the all aggregations' versions

        # Add aggregation versions to the version_sum
        for Model in ALL_TESTS_AGGREGATION_MODELS:
            try:
                agg = Model.get_for_agent(agent)
                if agg:
                    version_sum += agg.version
            except Model.DoesNotExist:
                continue

        return version_sum
      
    @staticmethod
    def get_updated_tests(agent, test_version):
        current_test_version = Test.get_test_version(agent)
        if int(current_test_version) > int(test_version):
            return Test.get_tests_for_version(agent, str(current_test_version))
        else:
            return []
      
      
    @staticmethod
    def get_tests_for_version(agent, test_version):
        tests = []
        for Model in WEBSITE_TESTS_AGGREGATION_MODELS.values():
            try:
                agg = Model.get_for_agent(agent)
                _tests = [WebsiteTest.objects.get(id=test_id)
                          for test_id in agg.test_ids]
                tests.extend(_tests)
            except Model.DoesNotExist:
                pass
              
        for Model in SERVICE_TESTS_AGGREGATION_MODELS.values():
            try:
                agg = Model.get_for_agent(agent)
                _tests = [ServiceTest.objects.get(id=test_id)
                          for test_id in agg.test_ids]
                tests.extend(_tests)
            except Model.DoesNotExist:
                pass
              
        return tests
          

    def save(self, *args, **kwargs):
        new = self.id is None

        if new:
            res = super(Test, self).save(*args, **kwargs)
            TestAggregation.update_aggregations_from_test(self)
        else:
            # remove old state from aggregations
            TestAggregation.remove_test_from_aggregations(self)
            # apply new state
            res = super(Test, self).save(*args, **kwargs)
            # add new state to aggregations
            TestAggregation.update_aggregations_from_test(self)
        return res


class WebsiteTest(Test):
    website_url = models.URLField(max_length=255, verify_exists=False)

    @staticmethod
    def create_from_suggestion(suggestion):
        tests = WebsiteTest.objects.filter(
            website_url=suggestion.website_url)

        if suggestion.location:
            tests.objects.filter(location_id=suggestion.location.id)

        if tests.count():
            return False
        else:
            test = WebsiteTest(website_url=suggestion.website_url)
            if suggestion.location:
                test.location_id = suggestion.location.id
            test.save()
            return True

    def __unicode__(self):
        return "%s (%s) - %s" % (self.description, self.website_url,
                                 "Active" if self.active else "Inactive")


@receiver(pre_delete, sender=WebsiteTest)
def delete_website_test(sender, *args, **kwargs):
    test = kwargs['instance']
    TestAggregation.remove_test_from_aggregations(test)


class ServiceTest(Test):
    service_name = models.TextField()
    ip = models.TextField()
    port  = models.PositiveIntegerField()

    @staticmethod
    def create_from_suggestion(suggestion):
        tests = ServiceTest.objects.filter(
            service_name=suggestion.service_name,
            ip=suggestion.ip,
            port=suggestion.port)

        if suggestion.location:
            tests.objects.filter(location_id=suggestion.location.id)

        if tests.count():
            return False
        else:
            test = ServiceTest(service_name=suggestion.service_name,
                               ip=suggestion.ip,
                               port=suggestion.port)
            if suggestion.location:
                test.location_id = suggestion.location.id
            test.save()
            return True

    def __unicode__(self):
        return "%s (%s) - %s:%s" % (self.description, self.service_name,
                                 self.ip, self.port)


@receiver(pre_delete, sender=ServiceTest)
def delete_service_test(sender, *args, **kwargs):
    test = kwargs['instance']
    TestAggregation.remove_test_from_aggregations(test)


class TestAggregation(models.Model):

    version = models.IntegerField(default=1)
    location_id = models.PositiveIntegerField(blank=True, null=True)
    test_ids = ListField(py_type=str)

    class Meta:
        abstract = True

    @property
    def location(self):
        if not self.location_id:
            return None
        else:
            return Location.objects.get(pk=self.location_id)

    @staticmethod
    def _update_aggregation_for_model(Model, test, filter_kwargs=None):
        try:
            if filter_kwargs:
                aggr = Model.objects.get(**filter_kwargs)
            else:
                aggr = Model.objects.get()
            aggr.version += 1
            if not test.id in aggr.test_ids:
                aggr.test_ids.append(test.id)
            aggr.save()
        except Model.DoesNotExist:
            aggr = Model(version=1)
            aggr.test_ids = [test.id]
            if test and test.location_id:
                aggr.location_id = test.location_id
            aggr.save()

    @staticmethod
    def _remove_test_from_aggregation(Model, test, filter_kwargs=None):
        try:
            if filter_kwargs:
                aggr = Model.objects.get(**filter_kwargs)
            else:
                aggr = Model.objects.get()
            if test.id in aggr.test_ids:
                aggr.test_ids.remove(test.id)
                aggr.version += 1
                aggr.save()
        except Model.DoesNotExist:
            pass

    @staticmethod
    def update_aggregations_from_test(test):
        assert type(test) in [WebsiteTest, ServiceTest]

        if type(test) == WebsiteTest:
            aggr_models = WEBSITE_TESTS_AGGREGATION_MODELS
        else:
            aggr_models = SERVICE_TESTS_AGGREGATION_MODELS


        if not test.location:
            #update global aggregation
            TestAggregation._update_aggregation_for_model(
                aggr_models["global"], test)
            return

        # update city aggregation
        if test.location.city:
            TestAggregation._update_aggregation_for_model(
                aggr_models['city'], test,
                {'location_d_city': test.location.city})

            return

        #update region aggregation
        if test.location.state_region:
            TestAggregation._update_aggregation_for_model(
                aggr_models["region"], test,
                {'location_d_state_region': test.location.state_region})

            return

        #update country aggregation
        if test.location.country_name:
            TestAggregation._update_aggregation_for_model(
                aggr_models["country"], test,
                {'location_d_country_name': test.location.country_name})


    @staticmethod
    def remove_test_from_aggregations(test):
        assert type(test) in [WebsiteTest, ServiceTest]

        if type(test) == WebsiteTest:
            aggr_models = WEBSITE_TESTS_AGGREGATION_MODELS
        else:
            aggr_models = SERVICE_TESTS_AGGREGATION_MODELS

        if not test.location:
            #remove from global aggregation
            TestAggregation._remove_test_from_aggregation(
                aggr_models["global"], test)
            return

        #remove from city aggregation
        if test.location.city:
            TestAggregation._remove_test_from_aggregation(
                aggr_models['city'], test,
                {'location_d_city': test.location.city})

            return

        #remove from region aggregation
        if test.location.state_region:
            TestAggregation._remove_test_from_aggregation(
                aggr_models["region"], test,
                {'location_d_state_region': test.location.state_region})

            return

        #remove from country aggregation
        if test.location.country_name:
            TestAggregation._remove_test_from_aggregation(
                aggr_models["country"], test,
                {'location_d_country_name': test.location.country_name})


    @staticmethod
    def get_for_agent(agent):
        raise NotImplementedError


class WebsiteTestsGlobalAggregation(TestAggregation):

    @staticmethod
    def get_for_agent(agent):
        return WebsiteTestsGlobalAggregation.objects.get()


class WebsiteTestsCountryAggregation(TestAggregation):

    location_d_country_name = models.CharField(max_length=100)

    @staticmethod
    def get_for_agent(agent):
        if not agent.location:
            return None
        return WebsiteTestsCountryAggregation.objects.get(
                location_d_country_name=agent.location.country_name)


class WebsiteTestsRegionAggregation(TestAggregation):

    location_d_state_region = models.CharField(max_length=2)

    @staticmethod
    def get_for_agent(agent):
        if not agent.location:
            return None
        return WebsiteTestsRegionAggregation.objects.get(
                location_d_state_region=agent.location.state_region)


class WebsiteTestsCityAggregation(TestAggregation):

    location_d_city = models.CharField(max_length=255)

    @staticmethod
    def get_for_agent(agent):
        if not agent.location:
            return None
        return WebsiteTestsCityAggregation.objects.get(
                location_d_city=agent.location.city)


class ServiceTestsGlobalAggregation(TestAggregation):

    @staticmethod
    def get_for_agent(agent):
        return ServiceTestsGlobalAggregation.objects.get()


class ServiceTestsCountryAggregation(TestAggregation):

    location_d_country_name = models.CharField(max_length=100)

    @staticmethod
    def get_for_agent(agent):
        if not agent.location:
            return None
        return ServiceTestsCountryAggregation.objects.get(
            location_d_country_name=agent.location.country_name)


class ServiceTestsRegionAggregation(TestAggregation):

    location_d_state_region = models.CharField(max_length=2)

    @staticmethod
    def get_for_agent(agent):
        if not agent.location:
            return None
        return ServiceTestsRegionAggregation.objects.get(
            location_d_state_region=agent.location.state_region)


class ServiceTestsCityAggregation(TestAggregation):

    location_d_city = models.CharField(max_length=255)

    @staticmethod
    def get_for_agent(agent):
        if not agent.location:
            return None
        return ServiceTestsCityAggregation.objects.get(
                location_d_city=agent.location.city)


WEBSITE_TESTS_AGGREGATION_MODELS = {
    'global': WebsiteTestsGlobalAggregation,
    'country': WebsiteTestsCountryAggregation,
    'region' : WebsiteTestsRegionAggregation,
    'city': WebsiteTestsCityAggregation,
}


SERVICE_TESTS_AGGREGATION_MODELS = {
    'global': ServiceTestsGlobalAggregation,
    'country': ServiceTestsCountryAggregation,
    'region': ServiceTestsRegionAggregation,
    'city': ServiceTestsCityAggregation,
}

ALL_TESTS_AGGREGATION_MODELS = WEBSITE_TESTS_AGGREGATION_MODELS.values() + \
                               SERVICE_TESTS_AGGREGATION_MODELS.values()
