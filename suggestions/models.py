from django.db import models
from messages.messages_pb2 import WebsiteSuggestion, ServiceSuggestion


class WebsiteSuggestion(models.Model):
    websiteUrl = models.URLField(max_length=100)
    email      = models.EmailField(blank=True)

    def create(websiteSuggestionMsg):
        suggestion = WebsiteSuggestion()
        suggestion.websiteUrl = websiteSuggestionMsg.websiteURL
        suggestion.email = websiteSuggestionMsg.emailAddress
        return suggestion

    create = staticmethod(create)


class ServiceSuggestion(models.Model):
    serviceName = models.CharField(max_length=100)
    hostName    = models.CharField(max_length=100)
    ip          = models.CharField(max_length=60)
    email       = models.EmailField(blank=True)

    def create(serviceSuggestionMsg):
        suggestion = ServiceSuggestion()
        suggestion.serviceName = serviceSuggestionMsg.serviceName
        suggestion.hostName = serviceSuggestionMsg.hostName
        suggestion.ip = serviceSuggestionMsg.ip
        suggestion.email = serviceSuggestionMsg.emailAddress
        return suggestion

    create = staticmethod(create)
    

