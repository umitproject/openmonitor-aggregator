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
import datetime
import tarfile
import decimal

from django.db import models
from django.utils import simplejson as json
from django.core.files import File

from dbextra.fields import ListField
from dbextra.decorators import cache_model_method
from geoip.models import Location, IPRange

REPORT_PERIOD = datetime.timedelta(days=1)

def Trace(object):
    def __init__(self, hop, ip, timings, location_id=None, location_name=None,
                 country_name=None, country_code=None, state_region=None,
                 city=None, zipcode=None, lat=None, lon=None):
        
        self.hop = hop
        self.ip = ip
        self.timings = timings
        
        if location_id is not None:
            self.location_id = location_id
            self.location_name = location_name
            self.country_name = country_name
            self.country_code = country_code
            self.state_region = state_region
            self.city = city
            self.zipcode = zipcode
            self.lat = decimal.Decimal(lat)
            self.lon = decimal.Decimal(lon)
        else:
            iprange = IPRange.ip_location(ip)
            self.location_id = iprange.location_ip
            self.location_name = iprange.location_name
            self.country_name = iprange.country_name
            self.country_code = iprange.country_code
            self.state_region = iprange.state_region
            self.city = iprange.city
            self.zipcode = iprange.zipcode
            self.lat = iprange.lat
            self.lon = iprange.lon
    
    @staticmethod
    def from_dump(dump):
        return Trace(**json.loads(dump))
    
    @cache_model_method('trace_', 300, 'location_id')
    @property
    def location(self):
        return Location.objects.get(id=self.location_id)
    
    def __unicode__(self):
        return json.dumps(dict(hop=self.hop,
                               ip=self.ip,
                               timing=self.timing,
                               location_ip=self.location_ip,
                               location_name=self.location_name,
                               country_name=self.country_name,
                               country_code=self.country_code,
                               state_region=self.state_region,
                               city=self.city,
                               zipcode=self.zipcode,
                               lat=self.lat,
                               lon=self.lon))

def py_convert_trace(trace):
    return Trace.from_dump(trace)

def db_convert_trace(trace):
    return str(trace)


class Report(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    test_id = models.IntegerField()
    time = models.DateTimeField()
    time_zone = models.SmallIntegerField()
    response_time = models.PositiveIntegerField(null=True)
    nodes = ListField()
    
    #############
    # Traceroute
    target = models.CharField(max_length=255)
    hops = models.PositiveSmallIntegerField()
    packet_size = models.PositiveIntegerField()
    
    #############################
    # Trace Nodes
    # Is a list of Trace objects
    trace = ListField(py_type=py_convert_trace, db_type=db_convert_trace)
    
    #################################
    # Location of the reporting node
    ip = models.CharField(max_length=100)
    location_id = models.IntegerField()
    location_name = models.CharField(max_length=300)
    country_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    state_region = models.CharField(max_length=2)
    city = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=6)
    lat = models.DecimalField(decimal_places=20, max_digits=23)
    lon = models.DecimalField(decimal_places=20, max_digits=23)
    
    #################################
    # Occurrences of similar reports
    count = models.IntegerField()
    
    user_reports_ids = ListField(py_type=int)
    
    @cache_model_method('report_', 300, 'id')
    @property
    def user_reports(self):
        return UserReport.objects.filter(id__in=self.user_reports_ids)
    
    @cache_model_method('report_', 300, 'location_id')    
    @property
    def location(self):
        """The location of the reporting node"""
        return Location.objects.get(id=self.location_id)
    
    @staticmethod
    def create_or_count(user_report):
        report = Report.objects.filter(
                        test_id=user_report.test_id,
                        location_id=user_report.location_id,
                        created_at__gte=user_report.created_at-REPORT_PERIOD,
                        created_at__lte=user_report.created_at+REPORT_PERIOD
        )
        if not report:
            report = Report()
            report.test_id = user_report.test_id
            report.time = user_report.time
            report.time_zone = user_report.time_zone
            report.response_time = user_report.response_time
            report.nodes = user_report.nodes
            report.target = user_report.target
            report.hops = user_report.hops
            report.packet_size = user_report.packet_size
            report.trace = user_report.trace
            report.ip = user_report.ip
            report.location_id = user_report.location_id
            report.location_name = user_report.location_name
            report.country_name = user_report.country_name
            report.country_code = user_report.country_code
            report.state_region = user_report.state_region
            report.city = user_report.city
            report.zipcode = user_report.zipcode
            report.lat = user_report.lat
            report.lon = user_report.lon
            report.count = 1
            report.user_reports_ids = [user_report.id]
        else:
            report.count += 1
            report.user_reports_ids.append(user_report.id)
            report.response_time = (report.response_time + user_report.response_time)/2
        
        report.save()
        return Report


class UserReport(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    report_id = models.IntegerField()
    agent_id = models.BigIntegerField()
    test_id = models.PositiveIntegerField()
    time = models.DateTimeField()
    time_zone = models.SmallIntegerField()
    response_time = models.PositiveIntegerField(null=True)
    bandwidth = models.FloatField(null=True)
    nodes = ListField()
    
    #############
    # Traceroute
    target = models.CharField(max_length=255)
    hops = models.PositiveSmallIntegerField()
    packet_size = models.PositiveIntegerField()
    
    #############################
    # Trace Nodes
    # Is a list of Trace objects
    trace = ListField(py_type=py_convert_trace, db_type=db_convert_trace)
    
    #################################
    # Location of the reporting node
    ip = models.CharField(max_length=100)
    location_id = models.IntegerField()
    location_name = models.CharField(max_length=300)
    country_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    state_region = models.CharField(max_length=2)
    city = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=6)
    lat = models.DecimalField(decimal_places=20, max_digits=23)
    lon = models.DecimalField(decimal_places=20, max_digits=23)
    
    class Meta:
        abstract = True

    @cache_model_method('user_report_', 300, 'location_id')    
    @property
    def location(self):
        """The location of the reporting node"""
        return Location.objects.get(id=self.location_id)
    
    @cache_model_method('user_report_', 300, 'id')
    def get_blocked_node(self):
        return self.trace_set.order_by('-hop')[0:1].get()
    
    def add_trace(self, hop, ip, timing):
        self.trace.append(Trace(hop, ip, timing))
    
    def save(self, *args, **kwargs):
        new = self.id is None
        
        super(UserReport, self).save(*args, **kwargs)
        
        if new:
            Report.create_or_count(self)


class WebsiteReport(UserReport):
    url = models.URLField(max_length=255)
    status_code = models.PositiveSmallIntegerField()
    redirect_link = models.URLField(max_length=255, blank=True)
    html_response = models.TextField(blank=True)
    media_ids = ListField(py_type=int)
    
    @cache_model_method('website_report_', 300, 'id')
    @property
    def media(self):
        return WebsiteReportMedia.objects.filter(id__in=self.media_ids)

    @staticmethod
    def create(websiteReportMsg):
        report = WebsiteReport()

        website_report = websiteReportMsg.report
        icm_report     = website_report.header
        website_report_detail = website_report.report

        # read WebsiteReportDetail
        report.url = website_report_detail.websiteURL
        report.status_code = website_report_detail.statusCode

        if website_report_detail.HasField('responseTime'):
            report.response_time = website_report_detail.responseTime
        if website_report_detail.HasField('bandwidth'):
            report.bandwidth = website_report_detail.bandwidth

        if website_report_detail.HasField('redirectLink'):
            report.redirect_link = website_report_detail.redirectLink
        if website_report_detail.HasField('htmlResponse'):
            report.html_response = website_report_detail.htmlResponse
        
        if website_report_detail.HasField('htmlMedia'):
            html_media = tarfile.open(mode='r:gz',
                                      fileobj=website_report_detail.htmlResponse)
            for member in html_media.getmembers():
                f = File(html_media.extractfile(member))
                media_obj = WebsiteReportMedia()
                media_obj.file.save(member.name, f)
                media_obj.save()
                
                report.media_ids.append(media_obj.id)
                
                ##################################################################
                # TODO: Need to adapt the html code to link to these media files #
                ##################################################################

        # read ICMReport
        report.report_id = icm_report.reportID
        report.agent_id = icm_report.agentID
        report.test_id = icm_report.testID
        report.time = datetime.datetime.utcfromtimestamp(icm_report.timeUTC)
        report.time_zone = icm_report.timeZone

        # read ICMReport passedNodes
        for node in icm_report.passedNode:
            report.nodes.append(node)

        # read ICMReport TraceRoute
        if icm_report.HasField('traceroute'):
            try:
                report.target = icm_report.traceroute.target
                report.hops = icm_report.traceroute.hops
                report.packet_size = icm_report.traceroute.packetSize

                # read ICMReport TraceRoute Traces
                for rcvTrace in icm_report.traceroute.traces:
                    report.trace.append(
                            Trace(hop=rcvTrace.hop,
                                  ip=rcvTrace.ip,
                                  timings=[t for t in rcvTrace.packetsTiming])
                    )
            except Exception,ex:
                logging.error(ex)

        report.save()
        
        return report


class WebsiteReportMedia(models.Model):
    report_id = models.IntegerField()
    file = models.FileField(upload_to='wsrdata/')
    
    @cache_model_method('website_report_media_', 300, 'report_id')
    @property
    def report(self):
        return WebsiteReport.objects.get(id=self.report_id)
    

class ServiceReport(UserReport):
    service_name = models.CharField(max_length=50)
    host_name = models.CharField(max_length=512)
    port = models.IntegerField()
    status_code = models.PositiveSmallIntegerField()
    
    @staticmethod
    def create(serviceReportMsg):
        report = ServiceReport()

        service_report = serviceReportMsg.report
        icm_report     = service_report.header
        service_report_detail = service_report.report

        # read ServiceReportDetail
        report.service_name = service_report_detail.serviceName
        report.status_code = service_report_detail.statusCode
        if service_report_detail.HasField('responseTime'):
            report.response_time = service_report_detail.responseTime
        if service_report_detail.HasField('bandwidth'):
            report.bandwidth = service_report_detail.bandwidth

        # read ICMReport
        try:
            report.report_id = icm_report.reportID
            report.agent_id = icm_report.agentID
            report.test_id = icm_report.testID
            report.time = datetime.datetime.utcfromtimestamp(icm_report.timeUTC)
            report.time_zone = icm_report.timeZone
        except Exception,ex:
            logging.error(ex)

        # read ICMReport passedNodes
        for node in icm_report.passedNode:
            report.nodes.append(node)

        # read ICMReport TraceRoute
        if icm_report.HasField('traceroute'):
            report.target = icm_report.traceroute.target
            report.hops = icm_report.traceroute.hops
            report.packet_size = icm_report.traceroute.packetSize

            # read ICMReport TraceRoute Traces
            for rcvTrace in icm_report.traceroute.traces:
                report.trace.append(
                        Trace(hop=rcvTrace.hop,
                              ip=rcvTrace.ip,
                              timings=[t for t in rcvTrace.packetsTiming])
                )
        
        report.save()
        return report

