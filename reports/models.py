from django.db import models
import logging
import datetime

class Report(models.Model):
    reportId     = models.TextField()
    agentId      = models.BigIntegerField()
    testId       = models.PositiveIntegerField()
    time         = models.DateTimeField()
    timeZone     = models.SmallIntegerField()
    responseTime = models.PositiveIntegerField(null=True)
    bandwidth    = models.FloatField(null=True)
    traceRoute   = models.ForeignKey('TraceRoute', null=True)
    
    class Meta:
        abstract = True


class WebsiteReport(Report):
    url          = models.URLField(max_length=255)
    statusCode   = models.PositiveSmallIntegerField()
    redirectLink = models.URLField(max_length=255, blank=True)
    htmlResponse = models.TextField(blank=True)
    htmlMedia    = models.FileField(upload_to='reports/')
    # TODO: this is the correct path ?

    def create(websiteReportMsg):
        report = WebsiteReport()

        logging.info(websiteReportMsg)

        websiteReport = websiteReportMsg.report
        icmReport     = websiteReport.header
        websiteReportDetail = websiteReport.report

        # read WebsiteReportDetail
        report.url = websiteReportDetail.websiteURL
        report.statusCode = websiteReportDetail.statusCode

        if websiteReportDetail.HasField('responseTime'):
            report.responseTime = websiteReportDetail.responseTime
        if websiteReportDetail.HasField('bandwidth'):
            report.bandwidth = websiteReportDetail.bandwidth

        if websiteReportDetail.HasField('redirectLink'):
            report.redirectLink = websiteReportDetail.redirectLink
        if websiteReportDetail.HasField('htmlResponse'):
            report.htmlResponse = websiteReportDetail.htmlResponse
        if websiteReportDetail.HasField('htmlMedia'):
            # TODO: which name it should have ?
            report.htmlMedia.save(websiteReportDetail.websiteURL, websiteReportDetail.htmlResponse)

        # read ICMReport
        report.reportId = icmReport.reportID
        report.agentId = icmReport.agentID
        report.testId = icmReport.testID
        report.time = datetime.datetime.utcfromtimestamp(icmReport.timeUTC)
        report.timeZone = icmReport.timeZone

        report.save()

        # read ICMReport passedNodes
        for node in icmReport.passedNode:
            report.websitereportnode_set.create(node=node)

        # read ICMReport TraceRoute
        if icmReport.HasField('traceroute'):

            try:
                traceRoute = TraceRoute()
                traceRoute.target = icmReport.traceroute.target
                traceRoute.hops = icmReport.traceroute.hops
                traceRoute.packetSize = icmReport.traceroute.packetSize
                traceRoute.save()

                logging.info("traceroute created")

                # read ICMReport TraceRoute Traces
                for rcvTrace in icmReport.traceroute.traces:
                    trace = Trace()
                    trace.traceRoute = traceRoute
                    trace.hop = rcvTrace.hop
                    trace.ip = rcvTrace.ip
                    trace.save()

                    logging.info("trace created")

                    # read ICMReport TraceRoute Traces PacketsTiming
                    for rcvPacketTime in rcvTrace.packetsTiming:
                        packetTime = PacketTime()
                        packetTime.packetTiming = rcvPacketTime
                        # add packetTime to trace
                        trace.packettime_set.add(packetTime)

                    # add trace to traceroute
                    traceRoute.trace_set.add(trace)

                # associate traceroute with report
                report.traceRoute = traceRoute
            except Exception,ex:
                logging.error(ex)

        report.save()
        return report

    create = staticmethod(create)
    

class ServiceReport(Report):
    serviceName  = models.CharField(max_length=50)
    statusCode   = models.PositiveSmallIntegerField()

    def create(serviceReportMsg):
        report = ServiceReport()

        serviceReport = serviceReportMsg.report
        icmReport     = serviceReport.header
        serviceReportDetail = serviceReport.report

        # read ServiceReportDetail
        report.serviceName = serviceReportDetail.serviceName
        report.statusCode = serviceReportDetail.statusCode
        if serviceReportDetail.HasField('responseTime'):
            report.responseTime = serviceReportDetail.responseTime
        if serviceReportDetail.HasField('bandwidth'):
            report.bandwidth = serviceReportDetail.bandwidth

        # read ICMReport
        try:
            report.reportId = icmReport.reportID
            report.agentId = icmReport.agentID
            report.testId = icmReport.testID
            report.time = datetime.datetime.utcfromtimestamp(icmReport.timeUTC)
            report.timeZone = icmReport.timeZone
        except Exception,ex:
            logging.error(ex)

        report.save()

        # read ICMReport passedNodes
        for node in icmReport.passedNode:
            report.servicereportnode_set.create(node=node)

        # read ICMReport TraceRoute
        if icmReport.HasField('traceroute'):
            traceRoute = TraceRoute()
            traceRoute.target = icmReport.traceroute.target
            traceRoute.hops = icmReport.traceroute.hops
            traceRoute.packetSize = icmReport.traceroute.packetSize
            traceRoute.save()

            # read ICMReport TraceRoute Traces
            for rcvTrace in icmReport.traceroute.traces:
                trace = Trace()
                trace.traceRoute = traceRoute
                trace.hop = rcvTrace.hop
                trace.ip = rcvTrace.ip
                trace.save()

                # read ICMReport TraceRoute Traces PacketsTiming
                for rcvPacketTime in rcvTrace.packetsTiming:
                    packetTime = PacketTime()
                    packetTime.packetTiming = rcvPacketTime
                    # add packetTime to trace
                    trace.packettime_set.add(packetTime)

                # add trace to traceroute
                traceRoute.trace_set.add(trace)

            # associate traceroute with report
            report.traceRoute = traceRoute

        report.save()
        return report

    create = staticmethod(create)


class WebsiteReportNode(models.Model):
    report = models.ForeignKey('WebsiteReport')
    node   = models.CharField(max_length=255)


class ServiceReportNode(models.Model):
    report = models.ForeignKey('ServiceReport')
    node   = models.CharField(max_length=255)

class TraceRoute(models.Model):
    target     = models.CharField(max_length=255)
    hops       = models.PositiveSmallIntegerField()
    packetSize = models.PositiveIntegerField()


class Trace(models.Model):
    traceRoute = models.ForeignKey('TraceRoute')
    hop        = models.PositiveSmallIntegerField()
    ip         = models.CharField(max_length=255)
    #city       = models.CharField(max_length=100)
    #country    = models.CharField(max_length=100)
    #latitude   = models.FloatField()
    #longitude  = models.FloatField()
    #isp        = models.CharField(max_length=100)


class PacketTime(models.Model):
    trace         = models.ForeignKey('Trace')
    packetTiming  = models.PositiveIntegerField()