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

import decimal

from django.db import models
from django.core.cache import cache
from django.conf import settings

from dbextra.fields import ListField
from geoip.ip import convert_ip, convert_int_ip

CACHE_EXPIRATION = 60*60 # 1 hour, since this doesn't change any often
LOCATION_CACHE_KEY = "location_%s"
PUBLIC_KEY_AGENT_CACHE_KEY = "pkey_agent_%s"
AGENT_CACHE_KEY = "agent_%s"
IP_RANGE_CACHE_KEY = "ip_range_%s"
IP_RANGES_CACHE_KEY = "ip_ranges_%s"
NETWORK_LIST_AGENTS_CACHE_KEY = "network_logged_agents_%s"
PREFIX_KEY = "region_prefix_%s"
CLOSEST_LOCATION_KEY='closest_location_%s_%s'
CLOSEST_LOCATIONS_KEY='closes_locationss_%s_%s'

BAN_FLAGS = dict(
    abuse=1,
    robot=2,
    other=4
)


class LocationAggregation(models.Model):
    lat = models.DecimalField(decimal_places=20, max_digits=23) # Base Latitude
    lon = models.DecimalField(decimal_places=20, max_digits=23) # Base Longitude
    locations = ListField(py_type=int)

    def add(self, location):
        if location.id in self.locations:
            return
        
        self.locations.append(location.id)
        self.save()

    @staticmethod
    def add_location(location):
        """Is going to add the location to the aggregation ranges so we can link
        locations that are close to each other.
        """
        lat = int(location.lat)
        lon = int(location.lon)
        
        aggs = LocationAggregation.objects.filter(lat=lat, lon=lon)
        
        if not aggs:
            # There are no aggregations for such region. Let's create them now then
            agg = LocationAggregation()
            agg.lat = int(location.lat)
            agg.lon = int(location.lon)
            agg.save()
                
            agg.add(location)
            location.add_aggregation(agg)
        else:
            agg = aggs[0]
            agg.add(location)
            location.add_aggregation(agg)


class LocationNamesAggregation(models.Model):
    prefix = models.CharField(max_length=200)
    names = ListField()
    locations = ListField(py_type=int)

    @staticmethod
    def add_location(location):
        for i in xrange(1, len(location.fullname)):
            prefix = location.fullname[:i].lower()

            agg = LocationNamesAggregation.objects.filter(prefix=prefix)

            if agg:
                agg = agg[0]
                if location.id in agg.locations:
                    continue

                agg.names.append(location.fullname)
                agg.locations.append(location.id)
            else:
                agg = LocationNamesAggregation()
                agg.prefix = prefix
                agg.names.append(location.fullname)
                agg.locations.append(location.id)

            agg.save()

    @staticmethod
    def get_names(prefix):
        prefix = prefix.lower()
        names = cache.get(PREFIX_KEY % prefix, [])
        if names:
            return names

        agg = LocationNamesAggregation.objects.filter(prefix=prefix)
        if agg:
            names = agg[0].names

        cache.set(PREFIX_KEY, names)
        return names

    def __unicode__(self):
        return self.prefix


class Location(models.Model):
    ip_range_ids = ListField(py_type=int)
    fullname = models.CharField(max_length=300, blank=True, null=True)
    country_name = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=2)
    state_region = models.CharField(max_length=2)
    city = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=6)
    lat = models.DecimalField(decimal_places=20, max_digits=23)
    lon = models.DecimalField(decimal_places=20, max_digits=23)
    aggregations = ListField(py_type=int)
    nodes_count = models.IntegerField(default=0, null=True)

    def add_aggregation(self, aggregation):
        if aggregation.id in self.aggregations:
            return

        self.aggregations.append(aggregation.id)
        self.save()

    def __unicode__(self):
        return "%s, %s" % (self.city, self.country_name) \
                                if self.city != '' else self.country_code

    @staticmethod
    def retrieve_location(name):
        """If location is empty we consider this suggestion to be world wide.
        If location doesn't exist in our datastore, we try to get its
        coordinates. If successful, we create a new entry. Otherwise, we
        consider the suggestion to be world wide.
        """
        location = Location.objects.filter(fullname__startswith=name)
        if not location:
            # TODO
            location = Location.objects.filter(fullname__startswith=name)

        if location:
            return location[0]

    @property
    def ip_ranges(self):
        key = IP_RANGES_CACHE_KEY % self.id
        ranges = cache.get(key, False)
        if not ranges:
            ranges = IPRange.objects.filter(location_id=self.id)
            cache.set(key, ranges, CACHE_EXPIRATION)
        return ranges
    
    @staticmethod
    def add_ip_range(ip_range):
        location = ip_range.location
        if location:
            if ip_range.id in location.ip_range_ids:
                return location
            
            location.ip_range_ids.append(ip_range.id)
            location.save()
            return location
        
        #location = Location()
        #location.ip_range_ids = [ip_range.id]
        #location.country_code = ip_range.country_code
        #location.state_region = ip_range.state_region
        #location.city = ip_range.city
        #location.zipcode = ip_range.zipcode
        #location.lat = ip_range.lat
        #location.lon = ip_range.lon
        #location.save()
        
        return location

    def save(self, *args, **kwargs):
        super(Location, self).save(*args, **kwargs)

    def generateAggregations(self):
        # Create proper aggregation for the current lat/lon
        LocationAggregation.add_location(self)
        LocationNamesAggregation.add_location(self)
    
    @staticmethod
    def closest_location(lat, lon):
        """Not necessarily the closest location, but one in the closest range.
        TODO: make sure we save the locations in order of distance inside the
        aggregations so that we can retrieve the closest location rather than a
        random one in the closest range.
        """
        location = cache.get(CLOSEST_LOCATION_KEY % (lat, lon), None)
        if location is None:
            aggs = LocationAggregation.objects.filter(lat=int(lat), lon=int(lon))[:1]
            region = Location.objects.get(pk=aggs.locations[0])
            cache.set(CLOSEST_LOCATION_KEY % (lat, lon), region)
        return region
    
    @staticmethod
    def closest_locations(lat, lon):
        locations = cache.get(CLOSEST_LOCATIONS_KEY % (lat, lon), None)
        if locations is None:
            aggs = LocationAggregation.objects.filter(lat=int(lat), lon=int(lon))
            locations = []
            for agg in aggs:
                locations += [Location.objects.get(pk=id) for id in agg.locations]
            
            cache.set(CLOSEST_LOCATIONS_KEY % (lat, lon), locations)
        
        return locations


try:
    UNKNOWN_LOCATION = Location.objects.get_or_create(fullname='Unknown',
                                                      country_name='Unknown',
                                                      country_code='UN',
                                                      state_region='UN',
                                                      city='Unknown',
                                                      zipcode='',
                                                      lat=decimal.Decimal('0.0'),
                                                      lon=decimal.Decimal('0.0'))[0]
except:
    UNKNOWN_LOCATION = None

class BannedNetworks(models.Model):
    """This is an aggregation of Banned Networks that is built from
    IPRange model. This is in order for making retrieval of ban list faster
    and cheaper.
    """
    location_id = models.IntegerField()
    iprange_id = models.IntegerField()
    start_number = models.IntegerField()
    end_number = models.IntegerField()
    nodes_count = models.IntegerField()
    flags = models.IntegerField()
    
    @property
    def location(self):
        key = LOCATION_CACHE_KEY % self.location_id
        location = cache.get(key, False)
        if not location:
            location = Location.objects.get(id=self.location_id)
            cache.set(key, location, CACHE_EXPIRATION)
        return location
    
    @property
    def iprange(self):
        key = IP_RANGE_CACHE_KEY % self.iprange_id
        iprange = cache.get(key, False)
        if not iprange:
            iprange = IPRange.objects.get(id=self.iprange_id)
            cache.set(key, iprange, CACHE_EXPIRATION)
        return iprange


class IPRange(models.Model):
    location_id = models.IntegerField()
    start_number = models.IntegerField()
    end_number = models.IntegerField()
    nodes_count = models.IntegerField(default=0, null=True)
    banned = models.BooleanField(default=False)
    ban_flags = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s - %s" % (convert_int_ip(self.start_number),
                            convert_int_ip(self.end_number))

    def ban(self, flags):
        self.banned = True
        import pdb; pdb.set_trace()
        if self.ban_flags is None or self.ban_flags == 0:
            self.ban_flags = flags
        else:
            self.ban_flags |= flags
        self.save()

        banet = BannedNetworks.objects.filter(iprange_id=self.id)
        if banet:
            banet.flags |= flags
        else:
            banet = BannedNetworks()
            banet.location_id = self.location_id
            banet.iprange_id = self.id
            banet.start_number = self.start_number
            banet.end_number = self.end_number
            banet.nodes_count = self.nodes_count # the amount of nodes at the moment of the ban
            banet.flags = flags

        banet.save()

    def unban(self):
        self.banned = False
        self.ban_flags = 0
        self.save()

        banet = BannedNetworks.objects.filter(iprange_id=self.id)
        if banet:
            banet.delete()

    @staticmethod
    def ip_location(ip):
        if type(ip) != type(0):
            ip = convert_ip(ip)

        iprange = IPRange.objects.filter(start_number__lte=ip).order_by('-start_number')
        if iprange:
            return iprange[0]
        iprange = IPRange.objects.filter(end_number__gte=ip).order_by('end_number')
        if iprange:
            return iprange[0]

        return IPRange.objects.get_or_create(location_id=UNKNOWN_LOCATION.id,
                                             start_number=ip,
                                             end_number=ip)[0]

    @property
    def location(self):
        key = LOCATION_CACHE_KEY % self.location_id
        location = cache.get(key, False)
        if not location:
            location = Location.objects.get(id=self.location_id)
            cache.set(key, location, CACHE_EXPIRATION)
        return location

    @property
    def logged_agents(self):
        key = NETWORK_LIST_AGENTS_CACHE_KEY % self.id
        logged_agents = cache.get(key, False)
        if not logged_agents:
            count = settings.MAX_AGENTSLIST_RESPONSE
            from agents.models import LoggedAgent

            # TODO: Randomize results
            logged_agents = LoggedAgent.objects.filter(location_id=self.location_id)[:count]
            cache.set(key, logged_agents, CACHE_EXPIRATION)
        return logged_agents

    def save(self, *args, **kwargs):
        new = self.id is None

        super(IPRange, self).save(*args, **kwargs)

        #if new:
        Location.add_ip_range(self)

    def dump(self):
        return dict(
                    start_ip=convert_int_ip(self.start_number),
                    end_ip=convert_int_ip(self.end_number)
                    )





