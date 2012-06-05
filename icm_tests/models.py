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

from dbextra.fields import ListField
from geoip.models import Location


class Test(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=False)
    location = models.ForeignKey(Location, blank=True, null=True)

    class Meta:
        abstract = True

    @staticmethod
    def create_from_suggestion(suggestion):
        raise NotImplementedError

    @staticmethod
    def get_test_version(agent):
        version_sum = 0

        # Latest version is sum of the all aggregations' versions

        # Add aggregation versions to the version_sum
        for Model in ALL_TESTS_AGGREGATION_MODELS:
            try:
                version_sum += Model.get_for_agent(agent).version
            except Model.DoesNotExist:
                continue

        return version_sum

    def save(self, *args, **kwargs):
        new = self.id is None

        res = super(Test, self).save(*args, **kwargs)

        if new:
            test.update_aggregations_from_test(self)

        return res



class WebsiteTest(Test):
    website_url = models.URLField()

    def __unicode__(self):
        return "%s (%s) - %s" % (self.description, self.website_url,
                                 "Active" if self.active else "Inactive")

class ServiceTest(Test):
    service_name = models.TextField()
    ip = models.TextField()
    port  = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s (%s) - %s" % (self.description, self.service_name,
                                 self.ip, self.port)


class TestAggregation(models.Model):

    version = models.IntegerField(default=1)
    location = models.ForeignKey(Location, blank=True, null=True)
    test_ids = ListField()

    class Meta:
        abstract = True

    @staticmethod
    def _update_aggregation_for_model(Model, test, filter_kwargs=None):
        try:
            aggr = Model.objects.get(**filter_kwargs)
            aggr.version += 1
            if not test.id in aggr.test_ids:
                aggr.test_ids.append(test.id)
            aggr.save()
        except Model.DoesNotExist:
            aggr = Model(version=1)
            aggr.test_ids = [test.id]
            if test and test.location:
                aggr.location = test.location
            aggr.save()


    @staticmethod
    def update_aggregations_from_test(test):
        assert type(test) in [WebsiteTest, ServiceTest]

        if type(test) == WebsiteTest:
            aggr_models = WEBSITE_TESTS_AGGREGATION_MODELS
        else:
            aggr_models = SERVICE_TESTS_AGGREGATION_MODELS

        #update global aggregation
        TestAggregation._update_aggregation_for_model(
            aggr_models["global"], test)

        if not test.location:
            return

        # update city aggregation
        if test.location.city:
            TestAggregation._update_aggregation_for_model(
                aggr_models['city'], test,
                {'location__city': test.location.city})

            return

        #update region aggregation
        if test.location.state_region:
            TestAggregation._update_aggregation_for_model(
                aggr_models["region"], test,
                {'location__state_region': test.location.state_region})

            return

        #update country aggregation
        if test.location.country_name:
            TestAggregation._update_aggregation_for_model(
                aggr_models["country"], test,
                {'location__country_name': test.location.country_name})


class WebsiteTestsGlobalAggregation(TestAggregation):
    pass


class WebsiteTestsCountryAggregation(TestAggregation):
    pass


class WebsiteTestsRegionAggregation(TestAggregation):
    pass


class WebsiteTestsCityAggregation(TestAggregation):
    pass


class ServiceTestsGlobalAggregation(TestAggregation):
    pass


class ServiceTestsCountryAggregation(TestAggregation):
    pass


class ServiceTestsRegionAggregation(TestAggregation):
    pass


class ServiceTestsCityAggregation(TestAggregation):
    pass


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

ALL_TESTS_AGGREGATION_MODELS = dict(**WEBSITE_TESTS_AGGREGATION_MODELS)
ALL_TESTS_AGGREGATION_MODELS.update(dict(**SERVICE_TESTS_AGGREGATION_MODELS))
