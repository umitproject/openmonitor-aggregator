#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Author: Adriano Monteiro Marques <adriano@umitproject.org>
## Author: Diogo Pinheiro <diogormpinheiro@gmail.com>
##
## Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

from piston.handler import BaseHandler
from messages import messages_pb2
from suggestions.models import WebsiteSuggestion, ServiceSuggestion
from reports.models import WebsiteReport, ServiceReport
from django.test.client import Client
from versions.models import DesktopAgentVersion, MobileAgentVersion
from ICMtests.models import Test, WebsiteTest, ServiceTest
from decision.decisionSystem import DecisionSystem
from agents.models import Agent
import logging
import base64


class RegisterAgentHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("registerAgent received")
        msg = base64.b64decode(request.POST['msg'])

        receivedAgentRegister = messages_pb2.RegisterAgent()
        receivedAgentRegister.ParseFromString(msg)

        # create agent
        if receivedAgentRegister.HasField('ip'):
            agentIp = receivedAgentRegister.ip
        else:
            agentIp = request.META['REMOTE_ADDR']

        logging.debug("Agent ip is " + agentIp)

        agent = Agent.create(receivedAgentRegister.versionNo, receivedAgentRegister.agentType, agentIp)
        logging.info(agent.agentID)
        keyPair = agent.generateKeys()
        logging.info("agent added")


        # get software version information
        if receivedAgentRegister.agentType=="DESKTOP":
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        elif receivedAgentRegister.agentType=="MOBILE":
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        # create the response
        response = messages_pb2.RegisterAgentResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID
        response.agentID = agent.agentID

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str


class LoginHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("loginAgent received")
        msg = base64.b64decode(request.POST['msg'])

        loginAgent = messages_pb2.Login()
        loginAgent.ParseFromString(msg)

        # login stuff
        # TODO: login

        # get agent info
        agent = Agent.getAgent(loginAgent.header.agentID)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        # create the response
        response = messages_pb2.LoginResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str


class LogoutHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("logoutAgent received")
        msg = base64.b64decode(request.POST['msg'])

        logoutAgent = messages_pb2.Logout()
        logoutAgent.ParseFromString(msg)

        # logout stuff
        # TODO: logout


class GetPeerListHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("getPeerList received")
        msg = base64.b64decode(request.POST['msg'])

        receivedMsg = messages_pb2.GetPeerList()
        receivedMsg.ParseFromString(msg)

        # get agent info
        agent = Agent.getAgent(receivedMsg.header.agentID)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        if receivedMsg.HasField('count'):
            totalPeers = receivedMsg.count
        else:
            totalPeers = 100

        peers = Agent.getPeers(agent.getCurrentLocation(), totalPeers)

        # create the response
        response = messages_pb2.GetPeerListResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID

        for peer in peers:
            logging.info(peer)
            knownPeer = response.knownPeers.add()
            knownPeer.agentID = peer.agentID
            knownPeer.token = "tokenpeer1"
            knownPeer.publicKey.mod = peer.publicKeyMod
            knownPeer.publicKey.exp = peer.publicKeyExp
            knownPeer.peerStatus = "ON"
            knownPeer.agentIP = peer.current_ip
            knownPeer.agentPort = peer.port

        # send back response
        try:
            response_str = base64.b64encode(response.SerializeToString())
        except Exception,e:
            logging.error(e)

        return response_str


class GetSuperPeerListHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("getSuperPeerList received")
        msg = base64.b64decode(request.POST['msg'])

        receivedMsg = messages_pb2.GetSuperPeerList()
        receivedMsg.ParseFromString(msg)

        # get agent info
        agent = Agent.getAgent(receivedMsg.header.agentID)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        if receivedMsg.HasField('count'):
            totalPeers = receivedMsg.count
        else:
            totalPeers = 100

        superpeers = Agent.getSuperPeers(agent.getCurrentLocation(), totalPeers)

        # create the response
        response = messages_pb2.GetSuperPeerListResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID

        for peer in superpeers:
            knownSuperPeer = response.knownSuperPeers.add()
            knownSuperPeer.agentID = peer.agentID
            knownSuperPeer.token = "tokenSuper1"
            knownPeer.publicKey.mod = peer.publicKeyMod
            knownPeer.publicKey.exp = peer.publicKeyExp
            knownSuperPeer.peerStatus = "ON"
            knownSuperPeer.agentIP = peer.current_ip
            knownSuperPeer.agentPort = peer.port

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

        # get agent info
        agent = Agent.getAgent(receivedMsg.header.agentID)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

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
        logging.info("sendWebsiteReport received2")
        msg = base64.b64decode(request.POST['msg'])

        receivedWebsiteReport = messages_pb2.SendWebsiteReport()
        receivedWebsiteReport.ParseFromString(msg)

        # add website report
        webSiteReport = WebsiteReport.create(receivedWebsiteReport)
        # send report to decision system
        DecisionSystem.newReport(webSiteReport)

        # get agent info
        agent = Agent.getAgent(receivedWebsiteReport.header.agentID)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        logging.info("sendWebsiteReport sending response")

        # create the response
        response = messages_pb2.SendReportResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        logging.info("sendWebsiteReport msg encoded")
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

        # get agent info
        agent = Agent.getAgent(receivedServiceReport.header.agentID)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

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
        if receivedMsg.agentType == "DESKTOP":
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        elif receivedMsg.agentType == "MOBILE":
            softwareVersion = MobileAgentVersion.getLastVersionNo()
        # TODO: throw exception if not desktop neither mobile

        # get last test id
        testVersion = Test.getLastTestNo()

        # create the response
        response = messages_pb2.NewVersionResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID
        response.versionNo = softwareVersion.version

        if response.versionNo > receivedMsg.agentVersionNo:
            response.downloadURL = softwareVersion.url
            # TODO: send in bzip ?

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

        # get agent info
        agent = Agent.getAgent(receivedMsg.header.agentID)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

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
            elif isinstance(newTest, ServiceTest):
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

        # get agent info
        agent = Agent.getAgent(receivedWebsiteSuggestion.header.agentID)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        try:
            testVersion = Test.getLastTestNo()
        except Exception, e:
            logging.error(e)

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

        # get agent info
        agent = Agent.getAgent(receivedServiceSuggestion.header.agentID)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        # create the response
        response = messages_pb2.TestSuggestionResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion.testID

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str


class CheckAggregator(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("CheckAggregator received")
        msg = base64.b64decode(request.POST['msg'])

        checkAggregator = messages_pb2.CheckAggregator()
        checkAggregator.ParseFromString(msg)

        # get agent info
        agent = Agent.getAgent(checkAggregator.header.agentID)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        testVersion = Test.getLastTestNo()

        # create the response
        response = messages_pb2.CheckAggregatorResponse()
        response.status = "ON"
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
#
#
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
#
#            msg = base64.b64decode(response.content)
#            tests = messages_pb2.NewTestsResponse()
#            tests.ParseFromString(msg)
#
#            logging.info(tests)
#        except Exception, inst:
#            logging.error(inst)

#        try:
#            c = Client()
#            newversion = messages_pb2.NewVersion()
#            newversion.header.token = "token"
#            newversion.header.agentID = 5
#            newversion.agentVersionNo = 1
#            newversion.agentType = "MOBILE"
#            newt_str = base64.b64encode(newversion.SerializeToString())
#            response = c.post('http://icm-dev.appspot.com/api/checkversion/', {'msg': newt_str})
#
#            msg = base64.b64decode(response.content)
#            nv = messages_pb2.NewVersionResponse()
#            nv.ParseFromString(msg)
#
#            logging.info(nv)
#        except Exception, inst:
#            logging.error(inst)


        # create website report
#        try:
#            c = Client()
#            wreport = messages_pb2.SendWebsiteReport()
#            wreport.header.token = "token"
#            wreport.header.agentID = 3
#            wreport.report.header.reportID = "45457"
#            wreport.report.header.agentID = 5
#            wreport.report.header.testID = 100
#            wreport.report.header.timeZone = -5
#            wreport.report.header.timeUTC = 1310396214
#            wreport.report.report.websiteURL = "www.google.com"
#            wreport.report.report.statusCode = 200
#            wreport.report.report.responseTime = 129
#            wreport.report.report.bandwidth = 2300
#
#            wreport.report.header.passedNode.append("node1")
#            wreport.report.header.passedNode.append("node2")
#
#            wreport.report.header.traceroute.target = "78.43.34.120"
#            wreport.report.header.traceroute.hops = 2
#            wreport.report.header.traceroute.packetSize = 200
#
#            trace = wreport.report.header.traceroute.traces.add()
#            trace.ip = "214.23.54.34"
#            trace.hop = 1
#            trace.packetsTiming.append(120)
#            trace.packetsTiming.append(129)
#
#            trace = wreport.report.header.traceroute.traces.add()
#            trace.ip = "24.63.54.128"
#            trace.hop = 2
#            trace.packetsTiming.append(120)
#
#            wreport_str = base64.b64encode(wreport.SerializeToString())
#            response = c.post('/api/sendwebsitereport/', {'msg': wreport_str})
#        except Exception, inst:
#            logging.error(inst)


        # create service report
#        try:
#            c = Client()
#            sreport = messages_pb2.SendServiceReport()
#            sreport.header.token = "token"
#            sreport.header.agentID = 3
#            sreport.report.header.reportID = "newrep45457"
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

       # check aggregator
#        try:
#            c = Client()
#            wreport = messages_pb2.CheckAggregator()
#            wreport.header.token = "token"
#            wreport.header.agentID = 3
#
#            wreport_str = base64.b64encode(wreport.SerializeToString())
#            response = c.post('/api/checkaggregator/', {'msg': wreport_str})
#
#            msg = base64.b64decode(response.content)
#
#            checkAggregator = messages_pb2.CheckAggregatorResponse()
#            checkAggregator.ParseFromString(msg)
#
#            logging.info("Aggregator is " + checkAggregator.status)
#
#        except Exception, inst:
#            logging.error(inst)


       # register agent
#        try:
#            c = Client()
#            register = messages_pb2.RegisterAgent()
#            register.versionNo = 1
#            register.agentType = "DESKTOP"
#            register.ip = "72.21.214.128"
#
#            register_str = base64.b64encode(register.SerializeToString())
#            response = c.post('/api/registeragent/', {'msg': register_str})
#
#            logging.info("registration done")
#
#            #msg = base64.b64decode(response.content)
#
#            #registerres = messages_pb2.RegisterAgentResponse()
#            #registerres.ParseFromString(msg)
#
#            #logging.info("Register Response " + registerres.)
#
#        except Exception, inst:
#            logging.error(inst)


       # get peers
        try:
            c = Client()
            getpeer = messages_pb2.GetPeerList()
            getpeer.header.token = "token"
            getpeer.header.agentID = 103001

            getpeer_str = base64.b64encode(getpeer.SerializeToString())
            response = c.post('/api/getpeerlist/', {'msg': getpeer_str})

            msg = base64.b64decode(response.content)

            resp = messages_pb2.GetPeerListResponse()
            resp.ParseFromString(msg)

            for peer in resp.knownPeers:
                logging.info("New peer" + str(peer.agentID))

        except Exception, inst:
            logging.error(inst)

#        from geoip import geoip
#        service = geoip.GeoIp()
#        return service.getIPLocation('209.85.146.106')

        #return 'test'