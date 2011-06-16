from piston.handler import BaseHandler
from messages import messages_pb2
from suggestions.models import WebsiteSuggestion, ServiceSuggestion
from django.test.client import Client
import logging
import base64


class RegisterAgentHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("registerAgent received")
        msg = base64.b64decode(request.POST['msg'])

        receivedAgentRegister = messages_pb2.RegisterAgent()
        receivedAgentRegister.ParseFromString(msg)

        # TODO: register the agent
        token = "token"
        privateKey = "privatekey"
        publicKey = "publickey"
        cipheredPublicKey = "cpublickey"
        agentId = 5

        # create the response
        response = messages_pb2.RegisterAgentResponse()
        response.header.currentVersionNo = 1
        response.header.currentTestVersionNo = 1
        response.token = token
        response.privateKey = privateKey
        response.publicKey = publicKey
        response.agentID = agentId
        response.cipheredPublicKey = cipheredPublicKey

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str


class GetPeerListHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("getPeerList received")
        msg = base64.b64decode(request.POST['msg'])

        receivedMsg = messages_pb2.GetPeerList()
        receivedMsg.ParseFromString(msg)

        # TODO: get peer list

        # create the response
        response = messages_pb2.GetPeerListResponse()
        response.header.currentVersionNo = 1
        response.header.currentTestVersionNo = 1
        knownPeer = response.knownPeers.add()
        knownPeer.token = "token"
        knownPeer.publicKey = "publickey"
        knownPeer.peerStatus = "ON"
        knownPeer.agentIP = "80.10.20.30"
        knownPeer.agentPort = 50

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str


class GetSuperPeerListHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("getSuperPeerList received")
        msg = base64.b64decode(request.POST['msg'])

        receivedMsg = messages_pb2.GetSuperPeerList()
        receivedMsg.ParseFromString(msg)

        # TODO: get super peer list

        # create the response
        response = messages_pb2.GetSuperPeerListResponse()
        response.header.currentVersionNo = 1
        response.header.currentTestVersionNo = 1
        knownSuperPeer = response.knownSuperPeers.add()
        knownSuperPeer.token = "token"
        knownSuperPeer.publicKey = "publickey"
        knownSuperPeer.peerStatus = "ON"
        knownSuperPeer.agentIP = "80.10.20.30"
        knownSuperPeer.agentPort = 50

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str


class GetEventsHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("getEvents received")
        msg = base64.b64decode(request.POST['msg'])

        receivedMsg = messages_pb2.GetEvents()
        receivedMsg.ParseFromString(msg)

        # TODO: get events

         # create the response
        response = messages_pb2.GetEventsResponse()
        response.header.currentVersionNo = 1
        response.header.currentTestVersionNo = 1
        event = response.events.add()
        event.testType = "WEB"
        event.eventType = "CENSOR"
        event.timeUTC = 20
        event.sinceTimeUTC = 10

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str


class SendWebsiteReportHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("sendWebsiteReport received")
        msg = base64.b64decode(request.POST['msg'])

        receivedWebsiteReport = messages_pb2.SendWebsiteReport()
        receivedWebsiteReport.ParseFromString(msg)

        # TODO: add website report

        # create the response
        response = messages_pb2.SendReportResponse()
        response.header.currentVersionNo = 1
        response.header.currentTestVersionNo = 1

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str


class SendServiceReportHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("sendServiceReport received")
        msg = base64.b64decode(request.POST['msg'])

        receivedServiceReport = messages_pb2.SendServiceReport()
        receivedServiceReport.ParseFromString(msg)

        # TODO: add service report

        # create the response
        response = messages_pb2.SendReportResponse()
        response.header.currentVersionNo = 1
        response.header.currentTestVersionNo = 1

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str


class CheckNewVersionHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("checkNewVersion received")
        msg = base64.b64decode(request.POST['msg'])

        receivedMsg = messages_pb2.NewVersion()
        receivedMsg.ParseFromString(msg)

        # TODO: check for last software version

        # create the response
        response = messages_pb2.NewVersionResponse()
        response.header.currentVersionNo = 1
        response.header.currentTestVersionNo = 1
        response.downloadURL = "www.icm.com/newver"
        response.versionNo = 4

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str


class CheckNewTestHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("checkNewTest received")
        msg = base64.b64decode(request.POST['msg'])

        receivedMsg = messages_pb2.NewTests()
        receivedMsg.ParseFromString(msg)

        # TODO: check for last tests

        # create the response
        response = messages_pb2.NewTestsResponse()
        response.header.currentVersionNo = 1
        response.header.currentTestVersionNo = 1
        response.testVersionNo = 1
        test = response.tests.add()
        test.testID = 1;
        test.websiteURL = "www.example.com";
        test.executeAtTimeUTC = 4000;

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str


class WebsiteSuggestionHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("websiteSuggestion received")
        msg = base64.b64decode(request.POST['msg'])

        receivedWebsiteSuggestion = messages_pb2.WebsiteSuggestion()
        receivedWebsiteSuggestion.ParseFromString(msg)

        # create the suggestion
        webSiteSuggestion = WebsiteSuggestion.create(receivedWebsiteSuggestion)
        webSiteSuggestion.save()

        # create the response
        response = messages_pb2.TestSuggestionResponse()
        response.header.currentVersionNo = 1
        response.header.currentTestVersionNo = 1

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str


class ServiceSuggestionHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("serviceSuggestion received")
        msg = base64.b64decode(request.POST['msg'])

        receivedServiceSuggestion = messages_pb2.ServiceSuggestion()
        receivedServiceSuggestion.ParseFromString(msg)

        # create the suggestion
        serviceSuggestion = ServiceSuggestion.create(receivedServiceSuggestion)
        serviceSuggestion.save()

        # create the response
        response = messages_pb2.TestSuggestionResponse()
        response.header.currentVersionNo = 1
        response.header.currentTestVersionNo = 1

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str



class TestsHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):

        try:
            c = Client()
            suggestion = messages_pb2.WebsiteSuggestion()
            suggestion.header.token = "token"
            suggestion.header.agentID = 5
            suggestion.websiteURL = "www.example.com"
            suggestion.emailAddress = "teste@domain.com"
            sug_str = base64.b64encode(suggestion.SerializeToString())
            response = c.post('/api/websitesuggestion/', {'msg': sug_str})
        except Exception, inst:
            logging.error(inst)

        try:
            suggestion = messages_pb2.ServiceSuggestion()
            suggestion.header.token = "token"
            suggestion.header.agentID = 5
            suggestion.serviceName = "p2p"
            suggestion.emailAddress = "teste@domain.com"
            suggestion.ip = "192.168.2.1"
            suggestion.hostName = "newtestpc"
            sug_str = base64.b64encode(suggestion.SerializeToString())
            response = c.post('/api/servicesuggestion/', {'msg': sug_str})
        except Exception, inst:
            logging.error(inst)

        return 'test1'