from piston.handler import BaseHandler
from messages import messages_pb2
from suggestions.models import WebsiteSuggestion, ServiceSuggestion
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
        msg = base64.urlsafe_b64decode(request.POST['msg'])

        receivedWebsiteSuggestion = messages_pb2.WebsiteSuggestion()
        receivedWebsiteSuggestion.ParseFromString(msg)

        #webSiteSuggestion = WebsiteSuggestion(receivedWebsiteSuggestion)
        return receivedWebsiteSuggestion.websiteURL


class ServiceSuggestionHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request, ):
        return "ServiceSuggestionHandler"