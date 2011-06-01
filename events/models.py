from django.db import models


class Event(models.Model):
    targetType        = models.PositiveSmallIntegerField()
    eventType         = models.PositiveSmallIntegerField()
    firstDetectionUTC = models.DateTimeField()
    lastDetectionUTC  = models.DateTimeField()
    activated         = models.BooleanField()    # indicate if the event is still happening

    def getActiveEvents(self):
        return self.activated==True


class EventLocation(models.Model):
    event    = models.ForeignKey('Event')
    city     = models.CharField(max_length=100)
    country  = models.CharField(max_length=100)


class EventISP(models.Model):
    event = models.ForeignKey('Event')
    isp   = models.CharField(max_length=100)


class EventWebsiteReport(models.Model):
    event  = models.ForeignKey('Event')
    report = models.ForeignKey('reports.WebsiteReport')


class EventServiceReport(models.Model):
    event  = models.ForeignKey('Event')
    report = models.ForeignKey('reports.WebsiteReport')