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
from dbextra.decorators import cache_model_method
from dbextra.models import UserModel
from geoip.models import Location
from icm_tests.models import WebsiteTest, ServiceTest

from umit.proto.messages_pb2 import WebsiteSuggestion, ServiceSuggestion

def add_to_aggregation(agg_model, fields, suggestion):
    try:
        agg = agg_model.objects.filter(**dict([(f, getattr(suggestion, f)) for f in fields]))[0]
        if suggestion.id in agg.suggestions:
            return agg
        agg.count += 1
    except IndexError:
        agg = agg_model()
        for f in fields:
            setattr(agg, f, getattr(suggestion, f))
    
    agg.suggestions.append(suggestion.id)
    agg.save()
    
    return agg


def delete_from_aggregation(agg_model, fields, suggestion):
    aggs = agg_model.objects.filter(**dict([(f, getattr(suggestion, f)) for f in fields]))
    for agg in aggs:
        for suggestion_id in agg.suggestions:
            if suggestion_id == suggestion.id:
                agg.suggestions.remove(suggestion_id)

        if len(agg.suggestions) == 0:
            agg.delete()
        else:
            agg.save()


class WebsiteSuggestion(UserModel):
    created_at = models.DateTimeField(auto_now_add=True)
    website_url = models.URLField(max_length=300)
    location_id = models.IntegerField(null=True, blank=True)

    @cache_model_method('website_suggestion_', 300, 'location_id')
    @property
    def location(self):
        if self.location_id is not None:
            return Location.objects.get(id=self.location_id)
    
    @staticmethod
    def create(websiteSuggestionMsg, user):
        suggestion = WebsiteSuggestion()
        suggestion.website_url = websiteSuggestionMsg.websiteURL
        suggestion.user_id = user.id
        suggestion.save()
        return suggestion
    
    def save(self, *args, **kwargs):
        new = self.id is None
        
        res = super(WebsiteSuggestion, self).save(*args, **kwargs)
        
        if new:
            WebsiteUrlAggregation.add_suggestion(self)
            WebsiteLocationAggregation.add_suggestion(self)
            WebsiteAggregation.add_suggestion(self)
            WebsiteUserAggregation.add_suggestion(self)

        return res

    def accept_suggestion(self):
        WebsiteTest.create_from_suggestion(self)
        return self.delete()

    def __unicode__(self):
        return "%s - %s" % (self.website_url, self.location)


class BaseSuggestionAggregation(object):

    class MetaData:
        SuggestionModel = None

    def accept_aggregation(self):
      if not self.suggestions:
        return self.delete()

      for suggestion_id in self.suggestions:
        try:
          suggestion = self.MetaData.SuggestionModel.objects.get(id=suggestion_id)
          suggestion.accept_suggestion()
        except self.MetaData.SuggestionModel.DoesNotExist:
          pass
      self.delete()


class BaseWebsiteSuggestionAggregation(BaseSuggestionAggregation):

    class MetaData:
        SuggestionModel = WebsiteSuggestion


class WebsiteUserAggregation(UserModel, BaseWebsiteSuggestionAggregation):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    suggestions = ListField(py_type=str)
    count = models.IntegerField(default=1)

    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(WebsiteUserAggregation, ['user_id'], suggestion)

    def __unicode__(self):
        return "(%s) %s" % (self.count, self.user_id)


class WebsiteUrlAggregation(models.Model, BaseWebsiteSuggestionAggregation):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    website_url = models.URLField(max_length=300)
    suggestions = ListField(py_type=str)
    count = models.IntegerField(default=1)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(WebsiteUrlAggregation, ['website_url'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.website_url)


class WebsiteLocationAggregation(models.Model,
                                 BaseWebsiteSuggestionAggregation):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location_id = models.IntegerField(null=True)
    suggestions = ListField(py_type=str)
    count = models.IntegerField(default=1)
    
    @cache_model_method('website_location_aggregation_', 300, 'location_id')
    @property
    def location(self):
        if self.location_id is not None:
            return Location.objects.get(id=self.location_id)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(WebsiteLocationAggregation,
                                  ['location_id'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.location)


class WebsiteAggregation(UserModel, BaseWebsiteSuggestionAggregation):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location_id = models.IntegerField(null=True)
    website_url = models.URLField(max_length=300)
    suggestions = ListField(py_type=str)
    count = models.IntegerField(default=1)
    
    @cache_model_method('website_aggregation_', 300, 'location_id')
    @property
    def location(self):
        if self.location_id is not None:
            return Location.objects.get(id=self.location_id)

    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(WebsiteAggregation,
                                  ['website_url', 'location_id', 'user_id'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s - %s" % (self.count, self.location, self.website_url)


class ServiceSuggestion(UserModel):
    created_at = models.DateTimeField(auto_now_add=True)
    service_name = models.CharField(max_length=100)
    host_name = models.CharField(max_length=100)
    ip = models.CharField(max_length=60)
    port = models.IntegerField()
    location_id = models.IntegerField(null=True)

    @cache_model_method('service_suggestion_', 300, 'location_id')
    @property
    def location(self):
        if self.location_id is not None:
            return Location.objects.get(id=self.location_id)

    @staticmethod
    def create(serviceSuggestionMsg, user):
        suggestion = ServiceSuggestion()
        suggestion.service_name = serviceSuggestionMsg.serviceName
        suggestion.host_name = serviceSuggestionMsg.hostName
        suggestion.ip = serviceSuggestionMsg.ip
        suggestion.port = serviceSuggestionMsg.port
        suggestion.user_id = user.id
        suggestion.save()
        return suggestion

    def save(self, *args, **kwargs):
        new = self.id is None
        
        res = super(ServiceSuggestion, self).save(*args, **kwargs)
        
        if new:
            ServiceNameAggregation.add_suggestion(self)
            ServiceHostAggregation.add_suggestion(self)
            ServiceIPAggregation.add_suggestion(self)
            ServicePortAggregation.add_suggestion(self)
            ServiceLocationAggregation.add_suggestion(self)
            ServiceUserAggregation.add_suggestion(self)
            ServiceAggregation.add_suggestion(self)

        return res

    def accept_suggestion(self):
        ServiceTest.create_from_suggestion(self)
        return self.delete()

    def __unicode__(self):
        return self.service_name


class BaseServiceSuggestionAggregation(BaseSuggestionAggregation):

    SuggestionModel = ServiceSuggestion


class ServiceNameAggregation(models.Model, BaseServiceSuggestionAggregation):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    service_name = models.CharField(max_length=100)
    suggestions = ListField(py_type=str)
    count = models.IntegerField(default=1)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(ServiceNameAggregation, ['service_name'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.service_name)

class ServiceHostAggregation(models.Model, BaseServiceSuggestionAggregation):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    host_name = models.CharField(max_length=100)
    suggestions = ListField(py_type=str)
    count = models.IntegerField(default=1)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(ServiceHostAggregation, ['host_name'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.host_name)

class ServiceIPAggregation(models.Model, BaseServiceSuggestionAggregation):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip = models.CharField(max_length=60)
    suggestions = ListField(py_type=str)
    count = models.IntegerField(default=1)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(ServiceIPAggregation, ['ip'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.ip)

class ServicePortAggregation(models.Model, BaseServiceSuggestionAggregation):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    port = models.IntegerField()
    suggestions = ListField(py_type=str)
    count = models.IntegerField(default=1)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(ServicePortAggregation, ['port'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.port)

class ServiceLocationAggregation(models.Model,
                                 BaseServiceSuggestionAggregation):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location_id = models.IntegerField(null=True)
    suggestions = ListField(py_type=str)
    count = models.IntegerField(default=1)
    
    @cache_model_method('service_location_aggregation_', 300, 'location_id')
    @property
    def location(self):
        if self.location_id is not None:
            return Location.objects.filter(id=self.location_id)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(ServiceLocationAggregation,
                                  ['location_id'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.location)

class ServiceUserAggregation(UserModel, BaseServiceSuggestionAggregation):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    suggestions = ListField(py_type=str)
    count = models.IntegerField(default=1)

    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(ServiceUserAggregation, ['user_id'], suggestion)

    def __unicode__(self):
        return "(%s) %s" % (self.count, self.user_id)

class ServiceAggregation(UserModel, BaseServiceSuggestionAggregation):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location_id = models.IntegerField(null=True)
    port = models.IntegerField()
    ip = models.CharField(max_length=60)
    host_name = models.CharField(max_length=100)
    service_name = models.CharField(max_length=100)
    suggestions = ListField(py_type=str)
    count = models.IntegerField(default=1)
    
    @cache_model_method('service_aggregation', 300, 'location_id')
    @property
    def location(self):
        if self.location_id is not None:
            return Location.objects.filter(id=self.location_id)

    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(ServiceAggregation,
            ['location_id', 'port', 'ip', 'host_name', 'service_name', 'user_id'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.location)
