from django.db import models


class SoftwareVersion(models.Model):
    version  = models.IntegerField()
    url      = models.URLField(max_length=255)

    class Meta:
        abstract = True


class DesktopAgentVersion(SoftwareVersion):

    def getLastVersionNo():
        return DesktopAgentVersion.objects.order_by('-version')[0:1].get()

    getLastVersionNo = staticmethod(getLastVersionNo)


class MobileAgentVersion(SoftwareVersion):

    def getLastVersionNo():
        return MobileAgentVersion.objects.order_by('-version')[0:1].get()

    getLastVersionNo = staticmethod(getLastVersionNo)