from django.db import models

class Report(models.Model):
    reportId     = models.BigIntegerField()
    senderId     = models.BigIntegerField()
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
    # TODO: missing htmlMEdia. Where to store that info ? bd or harddisk


class ServiceReport(Report):
    serviceName  = models.CharField(max_length=50)
    statusCode   = models.PositiveSmallIntegerField()


class WebsiteReportNodes(models.Model):
    report = models.ForeignKey('WebsiteReport')
    node   = models.CharField(max_length=255)


class ServiceReportNodes(models.Model):
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
    packetsTiming = models.PositiveIntegerField()