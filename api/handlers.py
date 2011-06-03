from piston.handler import BaseHandler
from messages import messages_pb2
from suggestions.models import WebsiteSuggestion, ServiceSuggestion
from django.test.client import Client
import base64


class RegisterAgentHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        return "RegisterAgentHandler"


class GetPeerListHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        return "GetPeerListHandler"


class GetSuperPeerListHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        return "GetSuperPeerListHandler"


class GetEventsHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        return "GetEventsHandler"


class SendWebsiteReportHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request, ):
        return "SendWebsiteReportHandler"


class SendServiceReportHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        return "SendServiceReportHandler"


class CheckNewVersionHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        return "CheckNewVersionHandler"


class CheckNewTestHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        return "CheckNewTestHandler"


class WebsiteSuggestionHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request, ):
        msg = base64.b64decode(request.POST['msg'])

        receivedWebsiteSuggestion = messages_pb2.WebsiteSuggestion()
        receivedWebsiteSuggestion.ParseFromString(msg)

        # create the suggestion
        webSiteSuggestion = WebsiteSuggestion.create(receivedWebsiteSuggestion)
        webSiteSuggestion.save()

        # create the response
        response = messages_pb2.TestSuggestionResponse()
        response.currentVersionNo = 1
        response.currentTestVersionNo = 1
        response_str = base64.b32encode(response.SerializeToString())

        # send back response
        return response_str


class ServiceSuggestionHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request, ):
        return "ServiceSuggestionHandler"


class TestsHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, ):
        c = Client()
        suggestion = messages_pb2.WebsiteSuggestion()
        suggestion.header.token = "token"
        suggestion.header.agentID = 5
        suggestion.websiteURL = "www.example.com"
        suggestion.emailAddress = "teste@domain.com"
        sug_str = base64.b64encode(suggestion.SerializeToString())
        response = c.post('/api/websitesuggestion/', {'msg': sug_str})