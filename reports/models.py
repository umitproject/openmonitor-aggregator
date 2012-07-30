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
from icm_utils.json import ICMJSONEncoder

from dbextra.fields import ListField
from dbextra.decorators import cache_model_method
from geoip.models import Location, IPRange

REPORT_PERIOD = datetime.timedelta(days=1)

class Trace(object):
    def __init__(self, hop, ip, timings, location_id=None, location_name=None,
                 country_name=None, country_code=None, state_region=None,
                 city=None, zipcode=None, lat=None, lon=None, is_final=0):
        
        self.hop = hop
        self.ip = ip
        self.timings = timings
        self.is_final = is_final
        
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
            self.location_id = iprange.location_id
            self.location_name = iprange.location.fullname
            self.country_name = iprange.location.country_name
            self.country_code = iprange.location.country_code
            self.state_region = iprange.location.state_region
            self.city = iprange.location.city
            self.zipcode = iprange.location.zipcode
            self.lat = decimal.Decimal(iprange.location.lat)
            self.lon = decimal.Decimal(iprange.location.lon)
    
    @staticmethod
    def from_dump(dump):
        dump = eval(dump)
        logging.debug("Trace Dump %s" % dump)
        if len(dump):
            return Trace(**json.loads(dump[0]))
    
    @cache_model_method('trace_', 300, 'location_id')
    @property
    def location(self):
        return Location.get_location_or_unknown(self.location_id)
    
    def __unicode__(self):
        return self.toJson()

    def toJson(self):
        return json.dumps(self.get_dict(), cls=ICMJSONEncoder)

    def get_dict(self):
        return dict(hop=self.hop,
                   ip=self.ip,
                   timings=self.timings,
                   location_id=self.location_id,
                   location_name=self.location_name,
                   country_name=self.country_name,
                   country_code=self.country_code,
                   state_region=self.state_region,
                   city=self.city,
                   zipcode=self.zipcode,
                   is_final=self.is_final,
                   lat=str(decimal.Decimal(self.lat)),
                   lon=str(decimal.Decimal(self.lon)))

def py_convert_trace(trace):
    return Trace.from_dump(trace)

def db_convert_trace(traces):
    traces_json = []
    if not isinstance(traces, list):
        traces = [traces]
    for trace in traces:
        if trace is not None:
            traces_json.append(trace.toJson())
    return traces_json


class Report(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    test_id = models.IntegerField(null=True, blank=True, default=None)
    time = models.DateTimeField()
    time_zone = models.SmallIntegerField()
    response_time = models.PositiveIntegerField(null=True)
    nodes = ListField()
    
    #############
    # Traceroute
    target = models.CharField(max_length=255)
    hops = models.PositiveSmallIntegerField(blank=True, null=True)
    packet_size = models.PositiveIntegerField()
    
    #############################
    # Trace Nodes
    # Is a list of Trace objects
    trace = ListField(py_type=py_convert_trace, db_type=db_convert_trace)
    
    #################################
    # Location of the reporting node
    agent_ip = models.CharField(max_length=100)
    agent_location_id = models.IntegerField()
    agent_location_name = models.CharField(max_length=300)
    agent_country_name = models.CharField(max_length=100)
    agent_country_code = models.CharField(max_length=2)
    agent_state_region = models.CharField(max_length=2)
    agent_city = models.CharField(max_length=255)
    agent_zipcode = models.CharField(max_length=6)
    agent_lat = models.DecimalField(decimal_places=20, max_digits=23)
    agent_lon = models.DecimalField(decimal_places=20, max_digits=23)

    #########################
    # Location of the target
    target = models.CharField(max_length=100, null=True)
    target_location_id = models.IntegerField(null=True)
    target_location_name = models.CharField(max_length=300, null=True)
    target_country_name = models.CharField(max_length=100, null=True)
    target_country_code = models.CharField(max_length=2, null=True)
    target_state_region = models.CharField(max_length=2, null=True)
    target_city = models.CharField(max_length=255, null=True)
    target_zipcode = models.CharField(max_length=6, null=True)
    target_lat = models.DecimalField(decimal_places=20, max_digits=23, null=True)
    target_lon = models.DecimalField(decimal_places=20, max_digits=23, null=True)
    
    #################################
    # Occurrences of similar reports
    count = models.IntegerField(default=1)
    
    user_reports_ids = ListField(py_type=str)

    def __unicode__(self):
        return "(%s) %s" % (self.updated_at, self.target)
    
    @cache_model_method('report_', 300, 'id')
    @property
    def user_reports(self):
        return UserReport.objects.filter(id__in=self.user_reports_ids)
    
    @cache_model_method('report_', 300, 'location_id')    
    @property
    def location(self):
        """The location of the reporting node"""
        return Location.get_location_or_unknown(self.location_id)
    
    @staticmethod
    def create_or_count(user_report):
        from decision.decisionSystem import DecisionSystem

        report = Report.objects.filter(
                        test_id=user_report.test_id,
                        agent_location_id=user_report.agent_location_id,
                        created_at__gte=user_report.created_at-REPORT_PERIOD,
                        created_at__lte=user_report.created_at+REPORT_PERIOD
        )
        if not report:
            report = Report()
            report.test_id = user_report.test_id
            report.time = user_report.time
            report.time_zone = user_report.time_zone
            report.response_time = user_report.response_time
            nodes = user_report.nodes
            report.nodes.append(nodes)
            report.target = user_report.target
            report.hops = user_report.hops
            report.packet_size = user_report.packet_size
            trace = user_report.trace
            report.trace = user_report.trace
            report.agent_ip = user_report.agent_ip
            report.agent_location_id = user_report.agent_location_id
            report.agent_location_name = user_report.agent_location_name
            report.agent_country_name = user_report.agent_country_name
            report.agent_country_code = user_report.agent_country_code
            report.agent_state_region = user_report.agent_state_region
            report.agent_city = user_report.agent_city
            report.agent_zipcode = user_report.agent_zipcode
            report.agent_lat = user_report.agent_lat
            report.agent_lon = user_report.agent_lon
            report.target_location_id = user_report.target_location_id
            report.target_location_name = user_report.target_location_name
            report.target_country_name = user_report.target_country_name
            report.target_country_code = user_report.target_country_code
            report.target_state_region = user_report.target_state_region
            report.target_city = user_report.target_city
            report.target_zipcode = user_report.target_zipcode
            report.target_lat = user_report.target_lat
            report.target_lon = user_report.target_lon
            report.count = 1
            report.user_reports_ids.append(user_report.id)
            DecisionSystem.newReport(user_report)
        else:
            report = report[0]
            report.count += 1
            report.user_reports_ids.append(user_report.id)
            if report.response_time and user_report.response_time:
                report.response_time = (report.response_time + user_report.response_time)/2
            elif not report.response_time and user_report.response_time:
                report.response_time = user_report.response_time

        report.save()
        return Report


class UserReport(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    #report_id = CassandraKeyField()
    agent_id = models.IntegerField(null=True, blank=True, default=None)
    test_id = models.IntegerField(null=True, blank=True, default=None)
    time = models.DateTimeField()
    time_zone = models.SmallIntegerField()
    response_time = models.PositiveIntegerField(null=True)
    bandwidth = models.FloatField(null=True)
    nodes = ListField()
    user_id = models.IntegerField(null=True, blank=True, default=None)
    
    #############
    # Traceroute
    target = models.CharField(max_length=255, null=True)
    hops = models.PositiveSmallIntegerField()
    packet_size = models.PositiveIntegerField()

    #########################
    # Location of the target
    target_location_id = models.IntegerField(null=True)
    target_location_name = models.CharField(max_length=300, null=True)
    target_country_name = models.CharField(max_length=100, null=True)
    target_country_code = models.CharField(max_length=2, null=True)
    target_state_region = models.CharField(max_length=2, null=True)
    target_city = models.CharField(max_length=255, null=True)
    target_zipcode = models.CharField(max_length=6, null=True)
    target_lat = models.DecimalField(decimal_places=20, max_digits=23, null=True)
    target_lon = models.DecimalField(decimal_places=20, max_digits=23, null=True)

    
    #############################
    # Trace Nodes
    # Is a list of Trace objects
    trace = ListField(py_type=py_convert_trace, db_type=db_convert_trace)
    
    #################################
    # Location of the reporting node
    agent_ip = models.CharField(max_length=100)
    agent_location_id = models.IntegerField()
    agent_location_name = models.CharField(max_length=300)
    agent_country_name = models.CharField(max_length=100)
    agent_country_code = models.CharField(max_length=2)
    agent_state_region = models.CharField(max_length=2)
    agent_city = models.CharField(max_length=255)
    agent_zipcode = models.CharField(max_length=6)
    agent_lat = models.DecimalField(decimal_places=20, max_digits=23)
    agent_lon = models.DecimalField(decimal_places=20, max_digits=23)
    
    class Meta:
        abstract = True

    @cache_model_method('user_report_', 300, 'location_id')    
    @property
    def location(self):
        """The location of the reporting node"""
        return Location.get_location_or_unknown(self.location_id)

    @property
    def user(self):
        return models.User.objects.get(id=self.user_id)
    
    @cache_model_method('user_report_', 300, 'id')
    def get_blocked_node(self):
        return self.trace_set.order_by('-hop')[0:1].get()
    
    def add_trace(self, hop, ip, timing, **kwargs):
        self.trace.append(Trace(hop, ip, timing, **kwargs))
    
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
    media_ids = ListField(py_type=str)

    def __unicode__(self):
        return "(%s) %s - %s" % (self.created_at, self.url, self.status_code)
    
    @cache_model_method('website_report_', 300, 'id')
    @property
    def media(self):
        return WebsiteReportMedia.objects.filter(id__in=self.media_ids)

    @staticmethod
    def create(websiteReportMsg, agent):
        report = WebsiteReport()

        website_report = websiteReportMsg.report
        icm_report     = website_report.header
        website_report_detail = website_report.report

        # read WebsiteReportDetail
        report.url = website_report_detail.websiteURL
        report.status_code = website_report_detail.statusCode
        print "Report status code: '%s'" % report.status_code

        if website_report_detail.HasField('responseTime'):
            report.response_time = website_report_detail.responseTime
            print "Response time: '%s'" % report.response_time
        if website_report_detail.HasField('bandwidth'):
            report.bandwidth = website_report_detail.bandwidth
            print "Bandwidth: '%s'" % report.bandwidth

        if website_report_detail.HasField('redirectLink'):
            report.redirect_link = website_report_detail.redirectLink
            print "Redirect link: '%s'" % report.redirect_link
        if website_report_detail.HasField('htmlResponse'):
            report.html_response = website_report_detail.htmlResponse
            print "Html response: '%s'" % report.hml_response
        
        if website_report_detail.HasField('htmlMedia'):
            html_media = tarfile.open(mode='r:gz',
                                      fileobj=website_report_detail.htmlResponse)
            for member in html_media.getmembers():
                f = File(html_media.extractfile(member))
                media_obj = WebsiteReportMedia()
                media_obj.file.save(member.name, f)
                media_obj.save()
                
                report.media_ids.append(media_obj.id)
                print "Adding media id: %s" % media_obj.id
                
                ##################################################################
                # TODO: Need to adapt the html code to link to these media files #
                ##################################################################

        report.user_id = agent.user.id
        print "User id: '%s'" % agent.user.id

        # read ICMReport
        logging.critical("STATUS CODE: %s" % website_report_detail.statusCode)
        #report.report_id = icm_report.reportID
        report.agent_id = icm_report.agentID
        print "Agent id: '%s'" % report.agent_id
        report.test_id = icm_report.testID if icm_report.testID else None
        print "Test id: '%s'" % report.test_id
        report.time = datetime.datetime.utcfromtimestamp(icm_report.timeUTC)
        report.time_zone = icm_report.timeZone

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
                              timings=[t for t in rcvTrace.packetsTiming],
                              is_final=(report.target==rcvTrace.ip and 1 or 0))
                )

            # update target location
            iprange = IPRange.ip_location(report.target)
            report.target_country_code = iprange.location.country_code
            print "Target country code: '%s'" % report.target_country_code
            report.target_country_name = iprange.location.country_name
            report.target_lat = iprange.location.lat
            report.target_lon = iprange.location.lon
            report.target_location_id = iprange.location_id
            print "Target location id: '%s'" % iprange.location_id
            report.target_location_name = iprange.location.fullname
            report.target_zipcode = iprange.location.zipcode
            report.target_state_region = iprange.location.state_region
            report.target_city = iprange.location.city

        # get info about target ip
        loggedAgent = agent.getLoginInfo()
        report.agent_ip = loggedAgent.current_ip
        report.agent_location_id = loggedAgent.location_id if loggedAgent.location_id != '' else None
        print "Agent location id: %s" % report.agent_location_id
        report.agent_location_name = loggedAgent.location_name
        report.agent_country_name = loggedAgent.country_name
        report.agent_country_code = loggedAgent.country_code
        report.agent_state_region = loggedAgent.state_region
        report.agent_city = loggedAgent.city
        report.agent_zipcode = loggedAgent.zipcode
        report.agent_lat = loggedAgent.latitude
        report.agent_lon = loggedAgent.longitude
        
        report.save()
        
        return report


class WebsiteReportMedia(models.Model):
    report_id = models.IntegerField(null=True, blank=True, default=None)
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
    def create(serviceReportMsg, agent):
        report = ServiceReport()

        service_report = serviceReportMsg.report
        icm_report     = service_report.header
        service_report_detail = service_report.report

        # read ServiceReportDetail
        report.service_name = service_report_detail.serviceName
        report.status_code = service_report_detail.statusCode
        report.port = service_report_detail.port
        if service_report_detail.HasField('responseTime'):
            report.response_time = service_report_detail.responseTime
        if service_report_detail.HasField('bandwidth'):
            report.bandwidth = service_report_detail.bandwidth

        report.user_id = agent.user.id

        # read ICMReport
        try:
            #report.report_id = icm_report.reportID
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
                              timings=[t for t in rcvTrace.packetsTiming],
                              is_final=(report.target==rcvTrace.ip and 1 or 0))
                )

            # update target location
            iprange = IPRange.ip_location(report.target)
            report.target_country_code = iprange.location.country_code
            report.target_country_name = iprange.location.country_name
            report.target_lat = iprange.location.lat
            report.target_lon = iprange.location.lon
            report.target_location_id = iprange.location_id
            report.target_location_name = iprange.location.fullname
            report.target_zipcode = iprange.location.zipcode
            report.target_state_region = iprange.location.state_region
            report.target_city = iprange.location.city

        # get info about target ip
        loggedAgent = agent.getLoginInfo()
        report.agent_ip = loggedAgent.current_ip
        report.agent_location_id = loggedAgent.location_id
        report.agent_location_name = loggedAgent.location_name
        report.agent_country_name = loggedAgent.country_name
        report.agent_country_code = loggedAgent.country_code
        report.agent_state_region = loggedAgent.state_region
        report.agent_city = loggedAgent.city
        report.agent_zipcode = loggedAgent.zipcode
        report.agent_lat = loggedAgent.latitude
        report.agent_lon = loggedAgent.longitude
        
        report.save()
        return report

