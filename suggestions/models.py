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
from messages.messages_pb2 import WebsiteSuggestion, ServiceSuggestion

def add_to_aggregation(agg_model, fields, suggestion):
    agg = agg_model.objects.filter(**dict([(f, getattr(suggestion, f)) for f in fields]))
    suggestions = []
    if agg:
        agg = agg[0]
        suggestions = agg.suggestions.split(',')
        if str(suggestion.id) in suggestions:
            return agg
        agg.count += 1
    else:
        agg = agg_model()
        for f in fields:
            setattr(agg, f, getattr(suggestion, f))
    
    suggestions.append(str(suggestion.id))
    agg.suggestions = ','.join(suggestions)
    agg.save()
    
    return agg

class WebsiteSuggestion(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    website_url = models.URLField(max_length=300)
    region = models.ForeignKey('geodata.Region', blank=True, null=True)
    email = models.EmailField(blank=True)

    @staticmethod
    def create(websiteSuggestionMsg):
        suggestion = WebsiteSuggestion()
        suggestion.website_url = websiteSuggestionMsg.websiteURL
        suggestion.email = websiteSuggestionMsg.emailAddress
        suggestion.save()
        return suggestion
    
    def save(self, *args, **kwargs):
        new = self.id is None
        
        res = super(WebsiteSuggestion, self).save(*args, **kwargs)
        
        if new:
            WebsiteUrlAggregation.add_suggestion(self)
            WebsiteRegionAggregation.add_suggestion(self)
            WebsiteAggregation.add_suggestion(self)

        return res

    def __unicode__(self):
        return "%s - %s" % (self.website_url, self.region)

class WebsiteUrlAggregation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    website_url = models.URLField(max_length=300)
    suggestions = models.TextField()
    count = models.IntegerField(default=1)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(WebsiteUrlAggregation, ['website_url'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.website_url)

class WebsiteRegionAggregation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    region = models.ForeignKey('geodata.Region', blank=True, null=True)
    suggestions = models.TextField()
    count = models.IntegerField(default=1)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(WebsiteRegionAggregation, ['region'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.region)

class WebsiteAggregation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    region = models.ForeignKey('geodata.Region', blank=True, null=True)
    website_url = models.URLField(max_length=300)
    suggestions = models.TextField()
    count = models.IntegerField(default=1)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(WebsiteAggregation, ['website_url', 'region'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s - %s" % (self.count, self.region, self.website_url)


class ServiceSuggestion(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    service_name = models.CharField(max_length=100)
    host_name = models.CharField(max_length=100)
    ip = models.CharField(max_length=60)
    port = models.IntegerField()
    region = models.ForeignKey('geodata.Region', blank=True, null=True)
    email = models.EmailField(blank=True)

    @staticmethod
    def create(serviceSuggestionMsg):
        suggestion = ServiceSuggestion()
        suggestion.service_name = serviceSuggestionMsg.serviceName
        suggestion.host_name = serviceSuggestionMsg.hostName
        suggestion.ip = serviceSuggestionMsg.ip
        suggestion.email = serviceSuggestionMsg.emailAddress
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
            ServiceRegionAggregation.add_suggestion(self)
            ServiceAggregation.add_suggestion(self)

        return res

    def __unicode__(self):
        return self.serviceName

class ServiceNameAggregation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    service_name = models.CharField(max_length=100)
    suggestions = models.TextField()
    count = models.IntegerField(default=1)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(ServiceNameAggregation, ['service_name'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.service_name)

class ServiceHostAggregation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    host_name = models.CharField(max_length=100)
    suggestions = models.TextField()
    count = models.IntegerField(default=1)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(ServiceHostAggregation, ['host_name'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.host_name)

class ServiceIPAggregation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip = models.CharField(max_length=60)
    suggestions = models.TextField()
    count = models.IntegerField(default=1)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(ServiceIPAggregation, ['ip'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.ip)

class ServicePortAggregation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    port = models.IntegerField()
    suggestions = models.TextField()
    count = models.IntegerField(default=1)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(ServicePortAggregation, ['port'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.port)

class ServiceRegionAggregation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    region = models.ForeignKey('geodata.Region', blank=True, null=True)
    suggestions = models.TextField()
    count = models.IntegerField(default=1)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(ServiceRegionAggregation, ['region'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.region)

class ServiceAggregation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    region = models.ForeignKey('geodata.Region', blank=True, null=True)
    port = models.IntegerField()
    ip = models.CharField(max_length=60)
    host_name = models.CharField(max_length=100)
    service_name = models.CharField(max_length=100)
    suggestions = models.TextField()
    count = models.IntegerField(default=1)
    
    @staticmethod
    def add_suggestion(suggestion):
        return add_to_aggregation(ServiceAggregation,
            ['region', 'port', 'ip', 'host_name', 'service_name'], suggestion)
    
    def __unicode__(self):
        return "(%s) %s" % (self.count, self.region)