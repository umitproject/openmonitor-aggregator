from django.db import models

class Test(models.Model):
    testID       = models.IntegerField(primary_key=True)
    description  = models.TextField(blank=True)

    def getLastTestNo():
        return Test.objects.order_by('-testID')[0:1].get()

    def getUpdatedTests(lastTestNo):
        newTests = []
        websiteTests = WebsiteTest.objects.filter(test__testID__gt=lastTestNo)
        serviceTests = ServiceTest.objects.filter(test__testID__gt=lastTestNo)
        newTests.extend(websiteTests)
        newTests.extend(serviceTests)
        return newTests

    getLastTestNo   = staticmethod(getLastTestNo)
    getUpdatedTests = staticmethod(getUpdatedTests)


class WebsiteTest(models.Model):
    test       = models.ForeignKey('Test')
    websiteURL = models.URLField()


class ServiceTest(models.Model):
    test        = models.ForeignKey('Test')
    serviceCode = models.PositiveIntegerField()
