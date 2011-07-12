from piston.handler import BaseHandler
from messages import messages_pb2
from suggestions.models import WebsiteSuggestion, ServiceSuggestion
from reports.models import WebsiteReport, ServiceReport
from django.test.client import Client
from versions.models import DesktopAgentVersion, MobileAgentVersion
from ICMtests.models import Test, WebsiteTest, ServiceTest
from decision.decisionSystem import DecisionSystem
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

        # get software version information
        # TODO: filter type of agent
        softwareVersion = DesktopAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        # create the response
        response = messages_pb2.RegisterAgentResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID
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

        # get software version information
        # TODO: filter type of agent
        softwareVersion = DesktopAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        # create the response
        response = messages_pb2.GetPeerListResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID
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

        # get software version information
        # TODO: filter type of agent
        softwareVersion = DesktopAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        # create the response
        response = messages_pb2.GetSuperPeerListResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID
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

        # get software version information
        # TODO: filter type of agent
        softwareVersion = DesktopAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

         # create the response
        response = messages_pb2.GetEventsResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID
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

        # add website report
        webSiteReport = WebsiteReport.create(receivedWebsiteReport)
        # send report to decision system
        DecisionSystem.newReport(webSiteReport)


        # get software version information
        # TODO: filter type of agent
        softwareVersion = DesktopAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        # create the response
        response = messages_pb2.SendReportResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID

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

        # add service report
        serviceReport = ServiceReport.create(receivedServiceReport)
        # send report to decision system
        DecisionSystem.newReport(serviceReport)

        # get software version information
        # TODO: filter type of agent
        softwareVersion = DesktopAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        # create the response
        response = messages_pb2.SendReportResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID

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

        # get software version information
        # TODO: filter type of agent
        softwareVersion = DesktopAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        # create the response
        response = messages_pb2.NewVersionResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID
        response.downloadURL = softwareVersion.url
        response.versionNo = softwareVersion.version

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

        newTests = Test.getUpdatedTests(receivedMsg.currentTestVersionNo)

        # get software version information
        # TODO: filter type of agent
        softwareVersion = DesktopAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        # create the response
        response = messages_pb2.NewTestsResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID
        response.testVersionNo = testVersion.testID

        for newTest in newTests:
            test = response.tests.add()
            test.testID = newTest.test.testID
            # TODO: get execution time
            test.executeAtTimeUTC = 4000

            if isinstance(newTest, WebsiteTest):
                test.testType = "WEB"
                test.websiteURL = newTest.websiteURL
            else:
                test.testType = "SERVICE"
                test.serviceCode = newTest.serviceCode

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

        # get software version information
        # TODO: filter type of agent
        softwareVersion = DesktopAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        # create the response
        response = messages_pb2.TestSuggestionResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID

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

        # get software version information
        # TODO: filter type of agent
        softwareVersion = DesktopAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        # create the response
        response = messages_pb2.TestSuggestionResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str



class TestsHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):

#        try:
#            c = Client()
#            suggestion = messages_pb2.WebsiteSuggestion()
#            suggestion.header.token = "token"
#            suggestion.header.agentID = 5
#            suggestion.websiteURL = "www.facebook.com"
#            suggestion.emailAddress = "diogopinheiro@ua.pt"
#            sug_str = base64.b64encode(suggestion.SerializeToString())
#            response = c.post('/api/websitesuggestion/', {'msg': sug_str})
#        except Exception, inst:
#            logging.error(inst)


#
#        try:
#            suggestion = messages_pb2.ServiceSuggestion()
#            suggestion.header.token = "token"
#            suggestion.header.agentID = 5
#            suggestion.serviceName = "torrent"
#            suggestion.emailAddress = "zeux@hotmail.com"
#            suggestion.ip = "80.92.156.29"
#            suggestion.hostName = "piratebay"
#            sug_str = base64.b64encode(suggestion.SerializeToString())
#            response = c.post('/api/servicesuggestion/', {'msg': sug_str})
#        except Exception, inst:
#            logging.error(inst)


#        try:
#            c = Client()
#            newtests = messages_pb2.NewTests()
#            newtests.header.token = "token"
#            newtests.header.agentID = 5
#            newtests.currentTestVersionNo = 0
#            newt_str = base64.b64encode(newtests.SerializeToString())
#            response = c.post('/api/checktests/', {'msg': newt_str})
#            logging.info(response)
#        except Exception, inst:
#            logging.error(inst)


        # create website report
        try:
            c = Client()
            wreport = messages_pb2.SendWebsiteReport()
            wreport.header.token = "token"
            wreport.header.agentID = 3
            wreport.report.header.reportID = 45457
            wreport.report.header.agentID = 5
            wreport.report.header.testID = 100
            wreport.report.header.timeZone = -5
            wreport.report.header.timeUTC = 1310396214
            wreport.report.report.websiteURL = "www.google.com"
            wreport.report.report.statusCode = 200
            wreport.report.report.responseTime = 129
            wreport.report.report.bandwidth = 2300

            wreport.report.header.passedNode.append("node1")
            wreport.report.header.passedNode.append("node2")

            wreport.report.header.traceroute.target = "78.43.34.120"
            wreport.report.header.traceroute.hops = 2
            wreport.report.header.traceroute.packetSize = 200

            trace = wreport.report.header.traceroute.traces.add()
            trace.ip = "214.23.54.34"
            trace.hop = 1
            trace.packetsTiming.append(120)
            trace.packetsTiming.append(129)

            trace = wreport.report.header.traceroute.traces.add()
            trace.ip = "24.63.54.128"
            trace.hop = 2
            trace.packetsTiming.append(120)

            wreport_str = base64.b64encode(wreport.SerializeToString())
            response = c.post('/api/sendwebsitereport/', {'msg': wreport_str})
        except Exception, inst:
            logging.error(inst)


        # create service report
#        try:
#            c = Client()
#            sreport = messages_pb2.SendServiceReport()
#            sreport.header.token = "token"
#            sreport.header.agentID = 3
#            sreport.report.header.reportID = 45457
#            sreport.report.header.agentID = 5
#            sreport.report.header.testID = 100
#            sreport.report.header.timeZone = -5
#            sreport.report.header.timeUTC = 1310396214
#            sreport.report.report.serviceName = "p2p"
#            sreport.report.report.statusCode = 100
#            sreport.report.report.responseTime = 53
#            sreport.report.report.bandwidth = 9456
#
#            sreport.report.header.passedNode.append("node1")
#            sreport.report.header.passedNode.append("node2")
#
#            sreport.report.header.traceroute.target = "78.43.34.120"
#            sreport.report.header.traceroute.hops = 2
#            sreport.report.header.traceroute.packetSize = 200
#
#            trace = sreport.report.header.traceroute.traces.add()
#            trace.ip = "214.23.54.34"
#            trace.hop = 1
#            trace.packetsTiming.append(120)
#            trace.packetsTiming.append(129)
#
#            sreport_str = base64.b64encode(sreport.SerializeToString())
#            response = c.post('/api/sendservicereport/', {'msg': sreport_str})
#        except Exception, inst:
#            logging.error(inst)

        return 'test1'