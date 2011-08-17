from django.db import models


class SoftwareVersion(models.Model):
    released_at = models.DateTimeField(auto_now_add=True)
    version  = models.IntegerField()
    url      = models.URLField(max_length=255)

    class Meta:
        abstract = True


class DesktopAgentVersion(SoftwareVersion):

    def getLastVersionNo():
        # TODO (Adriano): Use memcache to store this version indefinitely and
        # create signals to revogate cache once a new version is added
        return DesktopAgentVersion.objects.order_by('-version')[0:1].get()

    def __unicode__(self):
        return "Desktop Agent v" + str(self.version)

    getLastVersionNo = staticmethod(getLastVersionNo)


class MobileAgentVersion(SoftwareVersion):

    def getLastVersionNo():
        # TODO (Adriano): Use memcache to store this version indefinitely and create signals 
        # to revogate cache once a new version is added
        return MobileAgentVersion.objects.order_by('-version')[0:1].get()

    def __unicode__(self):
        return "Mobile Agent v" + str(self.version)

    getLastVersionNo = staticmethod(getLastVersionNo)