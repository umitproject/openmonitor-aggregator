from piston.handler import BaseHandler
from google.protobuf import descriptor
from messages import messages_pb2


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
        websiteSuggestion = messages_pb2.WebsiteReport()
        websiteSuggestion.ParseFromString(request.POST['data'])
        return "WebsiteSuggestionHandler"


class ServiceSuggestionHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request, ):
        return "WebsiteSuggestionHandler"