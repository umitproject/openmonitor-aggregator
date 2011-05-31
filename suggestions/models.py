from django.db import models


class WebsiteSuggestion(models.Model):
    websiteUrl = models.URLField(max_length=100)
    email      = models.EmailField(blank=True)


class ServiceSuggestion(models.Model):
    serviceName = models.CharField(max_length=100)
    hostName    = models.CharField(max_length=100)
    ip          = models.CharField(max_length=60)
    email       = models.EmailField(blank=True)
    

