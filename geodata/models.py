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

import logging

from django.db import models
from django.core.cache import cache

from utils import fetch_obj

PRIMES = [1, 2, 3, 5, 7, 9, 11, 13, 17, 19, 23, 29, 31, 37,
          41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89]

ALL_REGIONS_KEY='all_regions'
CLOSEST_REGION_KEY='closest_region_%s_%s'
CLOSEST_REGIONS_KEY='closes_regions_%s_%s'
PREFIX_KEY = "region_prefix_%s"

class RegionNamesAggregation(models.Model):
    prefix = models.CharField(max_length=200)
    names = models.TextField()
    regions = models.TextField()
    
    @staticmethod
    def add_region(region):
        for i in xrange(1, len(region.asciiname)):
            prefix = region.asciiname[:i]
            
            agg = RegionNamesAggregation.objects.filter(prefix=prefix)
            
            if agg:
                agg = agg[0]
                regions = agg.regions.split(",")
                if str(region.id) in regions:
                    continue
                
                agg.names = ','.join(agg.names.split(",") + [region.asciiname])
                agg.regions = ','.join(regions + [str(region.id)])
            else:
                agg = RegionNamesAggregation()
                agg.prefix = prefix
                agg.names = region.asciiname
                agg.regions = str(region.id)
            
            agg.save()
    
    @staticmethod
    def get_names(prefix):
        names = cache.get(PREFIX_KEY % prefix, [])
        if names:
            return names
        
        agg = RegionNamesAggregation.objects.filter(prefix=prefix)
        if agg:
            names = agg[0].names.split(',')
        
        cache.set(PREFIX_KEY, names)
        return names
    
    def __unicode__(self):
        return self.prefix

class Region(models.Model):
    name = models.CharField(max_length=200)
    asciiname = models.CharField(max_length=200)
    alternatenames = models.TextField()
    lat = models.DecimalField(decimal_places=20, max_digits=23)
    lon = models.DecimalField(decimal_places=20, max_digits=23)
    feature_class = models.CharField(max_length=1)
    feature_code = models.CharField(max_length=10)
    country_code = models.CharField(max_length=2)
    cc2 = models.CharField(max_length=60)
    
    # We're skipping admin code fields for now
    #admin1_code = models.CharField(max_length=20)
    #admin2_code = models.CharField(max_length=80)
    #admin3_code = models.CharField(max_length=20)
    #admin4_code = models.CharField(max_length=20)
    
    population = models.IntegerField()
    elevation = models.IntegerField()
    gtopo30 = models.IntegerField()
    
    # We're skipping timezone field for now
    #timezone = models.ForeignKey('geodata.Timezone')
    
    modification_date = models.DateTimeField()
    
    parent_region = models.ForeignKey('geodata.Region', null=True, blank=True, default=None)
    aggregations = models.TextField(blank=True, null=True, default='')
    
    def add_aggregation(self, aggregation):
        aggregations = self.aggregations.split(',')
        if str(aggregation.id) in aggregations:
            return
        
        aggregations.append(aggregation.id)
        self.aggregations = ','.join(aggregations)
        self.save()
    
    @staticmethod
    def retrieve_region(region_name):
        """If region is empty we consider this suggestion to be world wide.
        If region doesn't exist in our datastore, we try to get its
        coordinates. If successful, we create a new entry. Otherwise, we
        consider the suggestion to be world wide.
        """
        region = Region.objects.filter(asciiname=region_name)
        if not region:
            region = Region.objects.filter(name=region_name)

        if region:
            return region[0]
    
    @staticmethod
    def all_regions():
        regions = cache.get(ALL_REGIONS_KEY, None)
        if regions is None:
            regions = [str(region) for region in Region.objects.all()]
            cache.set(ALL_REGIONS_KEY, regions)
        return regions
    
    @staticmethod
    def closest_region(lat, lon):
        """Not necessarily the closest region, but one in the closest range.
        TODO: make sure we save the regions in order of distance inside the
        aggregations so that we can retrieve the closest region rather than a
        random one in the closest range.
        """
        region = cache.get(CLOSEST_REGION_KEY % (lat, lon), None)
        if region is None:
            aggs = RegionAggregation.objects.filter(lat=int(lat), lon=int(lon)).order_by('range')[:1]
            region = Region.objects.get(pk=aggs.regions.split(',')[0])
            cache.set(CLOSEST_REGION_KEY % (lat, lon), region)
        return region
    
    @staticmethod
    def closest_regions(lat, lon):
        regions = cache.get(CLOSEST_REGIONS_KEY % (lat, lon), None)
        if regions is None:
            aggs = RegionAggregation.objects.filter(lat=int(lat), lon=int(lon)).order_by('range')
            regions = []
            for agg in aggs:
                regions += [Region.objects.get(pk=id) for id in agg.regions.split(',')]
            
            cache.set(CLOSEST_REGIONS_KEY % (lat, lon), regions)
        
        return regions
    
    @property
    def regions(self):
        regions = []
        regions += self.region.regions
        return regions
    
    def save(self, *args, **kwargs):
        new = False
        if self.id is None:
            new = True
        
        super(Region, self).save(*args, **kwargs)
        
        if new:
            # Create proper aggregation for the current lat/lon
            RegionAggregation.add_region(self)
            RegionNamesAggregation.add_region(self)
    
    def __unicode__(self):
        return "%s%s" % (self.asciiname, ", %s" % self.parent_region if self.parent_region else "")


class RegionAggregation(models.Model):
    lat = models.DecimalField(decimal_places=20, max_digits=23) # Base Latitude
    lon = models.DecimalField(decimal_places=20, max_digits=23) # Base Longitude
    regions = models.TextField()

    def add(self, region):
        regions = self.regions.split(',')
        if str(region.id) in regions:
            return
        
        regions.append(region.id)
        self.regions = ','.join(regions)
        self.save()

    @staticmethod
    def add_region(region):
        """Is going to add the region to the aggregation ranges so we can link
        regions that are close to each other.
        """
        lat = int(region.lat)
        lon = int(region.lon)
        
        aggs = RegionAggregation.objects.filter(lat=lat, lon=lon)
        
        if not aggs:
            # There are no aggregations for such region. Let's create them now then
            agg = RegionAggregation()
            agg.lat = int(region.lat)
            agg.lon = int(region.lon)
            agg.save()
                
            agg.add(region)
            region.add_aggregation(agg)
        else:
            agg = agg[0]
            agg.add(region)
            region.add_aggregation(agg)
