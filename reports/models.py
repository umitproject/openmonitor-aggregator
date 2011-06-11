from django.db import models

class Report(models.Model):
    reportId     = models.BigIntegerField()
    agentId     = models.BigIntegerField()
    testId       = models.PositiveIntegerField()
    time         = models.DateTimeField()
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

        # read WebsiteReportDetail
        report.url = websiteReportMsg.report.websiteURL
        report.statusCode = websiteReportMsg.report.statusCode
        if websiteReportMsg.report.HasField('responseTime'):
            report.responseTime = websiteReportMsg.report.responseTime
        if websiteReportMsg.report.HasField('bandwidth'):
            report.bandwidth = websiteReportMsg.report.bandwidth

        if websiteReportMsg.HasField('redirectLink'):
            report.redirectLink = websiteReportMsg.redirectLink
        if websiteReportMsg.HasField('htmlResponse'):
            report.htmlResponse = websiteReportMsg.htmlResponse
        if websiteReportMsg.HasField('htmlMedia'):
            # TODO: which name it should have ?
            report.htmlMedia.save(websiteReportMsg.report.websiteURL, websiteReportMsg.htmlResponse)

        # read ICMReport
        report.reportId = websiteReportMsg.header.reportID
        report.agentId = websiteReportMsg.header.agentID
        report.testId = websiteReportMsg.header.testID
        report.time = websiteReportMsg.header.timeUTC
        # TODO: why we need timeZone ?

        # read ICMReport passedNodes
        for node in websiteReportMsg.header.passedNode:
            reportNode = WebsiteReportNode()
            reportNode.node = node
            report.websitereportnode_set.add(reportNode)

        # read ICMReport TraceRoute
        if websiteReportMsg.header.HasField('traceroute'):
            traceRoute = TraceRoute()
            traceRoute.target = websiteReportMsg.header.traceroute.target
            traceRoute.hops = websiteReportMsg.header.traceroute.hops
            traceRoute.packetSize = websiteReportMsg.header.traceroute.packetSize

            # read ICMReport TraceRoute Traces
            for rcvTrace in websiteReportMsg.header.traceroute.traces:
                trace = Trace()
                trace.hop = rcvTrace.hop
                trace.ip = rcvTrace.ip

                # read ICMReport TraceRoute Traces PacketsTiming
                for rcvPacketTime in rcvTrace.packetsTiming:
                    packetTime = PacketTime()
                    packetTime.packetTiming = rcvPacketTime
                    # add packetTime to trace
                    trace.packettime_set.add(packetTime)
                 
                # add trace to traceroute
                traceRoute.trace_set.add(trace)

            # associate traceroute with report
            traceRoute.report_set.add(report)
        

        return report

    create = staticmethod(create)


class ServiceReport(Report):
    serviceName  = models.CharField(max_length=50)
    statusCode   = models.PositiveSmallIntegerField()

    def create(serviceReportMsg):
        report = ServiceReport()

        # read ServiceReportDetail
        report.serviceName = serviceReportMsg.serviceName
        report.statusCode = serviceReportMsg.statusCode
        if serviceReportMsg.report.HasField('responseTime'):
            report.responseTime = serviceReportMsg.report.responseTime
        if serviceReportMsg.report.HasField('bandwidth'):
            report.bandwidth = serviceReportMsg.report.bandwidth

        # read ICMReport
        report.reportId = serviceReportMsg.header.reportID
        report.agentId = serviceReportMsg.header.agentID
        report.testId = serviceReportMsg.header.testID
        report.time = serviceReportMsg.header.timeUTC
        # TODO: why we need timeZone ?

        # read ICMReport passedNodes
        for node in serviceReportMsg.header.passedNode:
            reportNode = ServiceReportNode()
            reportNode.node = node
            report.servicereportnode_set.add(reportNode)

        # read ICMReport TraceRoute
        if serviceReportMsg.header.HasField('traceroute'):
            traceRoute = TraceRoute()
            traceRoute.target = serviceReportMsg.header.traceroute.target
            traceRoute.hops = serviceReportMsg.header.traceroute.hops
            traceRoute.packetSize = serviceReportMsg.header.traceroute.packetSize

            # read ICMReport TraceRoute Traces
            for rcvTrace in serviceReportMsg.header.traceroute.traces:
                trace = Trace()
                trace.hop = rcvTrace.hop
                trace.ip = rcvTrace.ip

                # read ICMReport TraceRoute Traces PacketsTiming
                for rcvPacketTime in rcvTrace.packetsTiming:
                    packetTime = PacketTime()
                    packetTime.packetTiming = rcvPacketTime
                    # add packetTime to trace
                    trace.packettime_set.add(packetTime)

                # add trace to traceroute
                traceRoute.trace_set.add(trace)

            # associate traceroute with report
            traceRoute.report_set.add(report)

        
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


class PacketTime(models.Model):
    trace         = models.ForeignKey('Trace')
    packetTiming  = models.PositiveIntegerField()