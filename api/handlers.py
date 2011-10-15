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

import logging
import base64

from piston.handler import BaseHandler
from messages import messages_pb2
from suggestions.models import WebsiteSuggestion, ServiceSuggestion
from reports.models import WebsiteReport, ServiceReport

from django.test.client import Client
from django.http import HttpResponse
from django.conf import settings

from versions.models import DesktopAgentVersion, MobileAgentVersion
from icm_tests.models import Test, WebsiteTest, ServiceTest
from decision.decisionSystem import DecisionSystem
from agents.models import Agent, LoggedAgent
from agents.CryptoLib import *

from django.conf import settings
import hashlib
import logging
import base64

from geoip.models import IPRange



class RegisterAgentHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("registerAgent received")

        logging.warning("Creating the crypto instance")
        crypto = CryptoLib()
        aggregatorKey = RSAKey(settings.RSAKEY_MOD, settings.RSAKEY_EXP, settings.RSAKEY_D, settings.RSAKEY_P, settings.RSAKEY_Q, settings.RSAKEY_U)
        logging.warning("Generated the aggregator key")


        AESKey = crypto.decodeRSAPrivateKey(request.POST['key'], aggregatorKey)
        msg = crypto.decodeAES(request.POST['msg'], AESKey)
        logging.warning("Decoded AES from agent")

        receivedAgentRegister = messages_pb2.RegisterAgent()
        receivedAgentRegister.ParseFromString(msg)
        logging.warning("Parsed registeragent message")

        # get agent ip
        if receivedAgentRegister.HasField('ip'):
            agentIp = receivedAgentRegister.ip
        else:
            agentIp = request.META['REMOTE_ADDR']
        
        logging.warning("Agent IP: %s" % agentIp)

        # create agent
        publicKeyMod = receivedAgentRegister.agentPublicKey.mod
        publicKeyExp = receivedAgentRegister.agentPublicKey.exp
        username = receivedAgentRegister.credentials.username
        password = receivedAgentRegister.credentials.password
        agent = Agent.create(receivedAgentRegister.versionNo, receivedAgentRegister.agentType, agentIp, publicKeyMod, publicKeyExp, username, password, AESKey)
        logging.warning("Created agent instance")

        # get software version information
        if receivedAgentRegister.agentType=="DESKTOP":
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        elif receivedAgentRegister.agentType=="MOBILE":
            softwareVersion = MobileAgentVersion.getLastVersionNo()
        
        logging.warning("Software version: %s" % softwareVersion)

        # get last test id
        last_test = Test.get_last_test()
        if last_test!=None:
            testVersion = last_test.test_id
        else:
            testVersion = 0
        
        logging.warning("Test version: %s" % testVersion)

        m = hashlib.sha1()
        m.update(agent.publicKeyMod)
        publicKeyHash = m.digest()
        
        logging.warning("Public key hash: %s" % publicKeyHash)

        # create the response
        try:
            response = messages_pb2.RegisterAgentResponse()
            response.header.currentVersionNo = softwareVersion.version
            response.header.currentTestVersionNo = testVersion
            response.agentID = agent.agentID
            response.publicKeyHash = crypto.encodeRSAPrivateKey(publicKeyHash, aggregatorKey)
        except Exception,e:
            logging.error(e)

        # send back response
        response_str = agent.encodeMessage(response.SerializeToString())
        return response_str


class LoginHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("loginAgent received")
        logging.info("Aggregator: Starting login step1")
        msg = base64.b64decode(request.POST['msg'])

        loginAgent = messages_pb2.Login()
        loginAgent.ParseFromString(msg)

        # get agent
        agent = Agent.getAgent(loginAgent.agentID)

        # get agent ip
        if loginAgent.HasField('ip'):
            agentIp = loginAgent.ip
        else:
            agentIp = request.META['REMOTE_ADDR']

        # initiate login process
        loginProcess = agent.initLogin(agentIp, loginAgent.port)

        logging.info("Challeng received from agent: %s" % loginAgent.challenge)

        # initiate crypto to cipher challenge
        crypto = CryptoLib()
        aggregatorPrivateKey = RSAKey(settings.RSAKEY_MOD, settings.RSAKEY_EXP, settings.RSAKEY_D, settings.RSAKEY_P, settings.RSAKEY_Q, settings.RSAKEY_U)
        cipheredChallenge = crypto.signRSA(loginAgent.challenge, aggregatorPrivateKey)

        logging.info("Challenge generated on aggregator: %s" % loginProcess.challenge)

        # create the response
        response = messages_pb2.LoginStep1()
        response.processID = loginProcess.processID
        response.cipheredChallenge = cipheredChallenge
        response.challenge = loginProcess.challenge

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        logging.info("Sending login step1")
        return response_str


class Login2Handler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("loginAgent2 received")
        logging.info("Aggregator: Starting login step2")
        msg = base64.b64decode(request.POST['msg'])

        loginAgent = messages_pb2.LoginStep2()
        loginAgent.ParseFromString(msg)

        # check login process
        agent = Agent.finishLogin(loginAgent.processID, loginAgent.cipheredChallenge)

        if agent is not None:
            logging.info("PASSED TEST")

            # get software version information
            if agent.agentType=='DESKTOP':
                softwareVersion = DesktopAgentVersion.getLastVersionNo()
            else:
                softwareVersion = MobileAgentVersion.getLastVersionNo()

            # get last test id
            last_test = Test.get_last_test()
            if last_test!=None:
                testVersion = last_test.test_id
            else:
                testVersion = 0

            # create the response
            response = messages_pb2.LoginResponse()
            response.header.currentVersionNo = softwareVersion.version
            response.header.currentTestVersionNo = testVersion

            # send back response
            response_str = base64.b64encode(response.SerializeToString())
            return response_str
        else:
            logging.error('Error in login')


class LogoutHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("logoutAgent received")
        agentID = request.POST['agentID']
        msg = base64.b64decode(request.POST['msg'])

        logoutAgent = messages_pb2.Logout()
        logoutAgent.ParseFromString(msg)

        # get agent
        agent = Agent.getAgent(agentID)
        agent.logout()


class GetPeerListHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("getPeerList received")

        # get agent info
        agentID = request.POST['agentID']
        agent = Agent.getAgent(agentID)

        # decode received message
        msg = agent.decodeMessage(request.POST['msg'])

        receivedMsg = messages_pb2.GetPeerList()
        receivedMsg.ParseFromString(msg)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        last_test = Test.get_last_test()
        if last_test!=None:
            testVersion = last_test.test_id
        else:
            testVersion = 0

        if receivedMsg.HasField('count'):
            totalPeers = receivedMsg.count
        else:
            totalPeers = 100

        peers = Agent.getPeers(agent.agentID, agent.getCurrentLocation(), totalPeers)

        # create the response
        response = messages_pb2.GetPeerListResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion

        for peer in peers:
            knownPeer = response.knownPeers.add()
            knownPeer.agentID = peer.agentID
            knownPeer.token = "tokenpeer1"
            knownPeer.publicKey.mod = peer.publicKeyMod
            knownPeer.publicKey.exp = peer.publicKeyExp
            if isinstance(peer, LoggedAgent):
                knownPeer.agentIP = peer.current_ip
                knownPeer.agentPort = peer.port
                knownPeer.peerStatus = "ON"
            else:
                knownPeer.agentIP = peer.lastKnownIP
                knownPeer.agentPort = peer.lastKnownPort
                knownPeer.peerStatus = "OFF"

        # send back response
        try:
            response_str = agent.encodeMessage(response.SerializeToString())
        except Exception,e:
            logging.error(e)

        return response_str


class GetSuperPeerListHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("getSuperPeerList received")

        # get agent info
        agentID = request.POST['agentID']
        agent = Agent.getAgent(agentID)

        # decode received message
        msg = agent.decodeMessage(request.POST['msg'])

        receivedMsg = messages_pb2.GetSuperPeerList()
        receivedMsg.ParseFromString(msg)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        last_test = Test.get_last_test()
        if last_test!=None:
            testVersion = last_test.test_id
        else:
            testVersion = 0

        if receivedMsg.HasField('count'):
            totalPeers = receivedMsg.count
        else:
            totalPeers = 100

        superpeers = Agent.getSuperPeers(agent.agentID, agent.getCurrentLocation(), totalPeers)

        # create the response
        response = messages_pb2.GetSuperPeerListResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion

        for peer in superpeers:
            knownSuperPeer = response.knownSuperPeers.add()
            knownSuperPeer.agentID = peer.agentID
            knownSuperPeer.token = "tokenSuper1"
            knownSuperPeer.publicKey.mod = peer.publicKeyMod
            knownSuperPeer.publicKey.exp = peer.publicKeyExp
            if isinstance(peer, LoggedAgent):
                knownSuperPeer.agentIP = peer.current_ip
                knownSuperPeer.agentPort = peer.port
                knownSuperPeer.peerStatus = "ON"
            else:
                knownSuperPeer.agentIP = peer.lastKnownIP
                knownSuperPeer.agentPort = peer.lastKnownPort
                knownSuperPeer.peerStatus = "OFF"

        # send back response
        response_str = agent.encodeMessage(response.SerializeToString())
        return response_str


class GetEventsHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("getEvents received")

        # get agent info
        agentID = request.POST['agentID']
        agent = Agent.getAgent(agentID)

        # decode received message
        msg = agent.decodeMessage(request.POST['msg'])

        receivedMsg = messages_pb2.GetEvents()
        receivedMsg.ParseFromString(msg)

        # TODO: get events

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        last_test = Test.get_last_test()
        if last_test!=None:
            testVersion = last_test.test_id
        else:
            testVersion = 0

        # create the response
        response = messages_pb2.GetEventsResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion
        event = response.events.add()
        event.testType = "WEB"
        event.eventType = "CENSOR"
        event.timeUTC = 20
        event.sinceTimeUTC = 10

        # send back response
        response_str = agent.encodeMessage(response.SerializeToString())
        return response_str


class SendWebsiteReportHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("sendWebsiteReport received")

        # get agent info
        agentID = request.POST['agentID']
        agent = Agent.getAgent(agentID)

        # decode received message
        msg = agent.decodeMessage(request.POST['msg'])

        receivedWebsiteReport = messages_pb2.SendWebsiteReport()
        receivedWebsiteReport.ParseFromString(msg)

        # add website report
        webSiteReport = WebsiteReport.create(receivedWebsiteReport, agent.user)
        # send report to decision system
        DecisionSystem.newReport(webSiteReport)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        last_test = Test.get_last_test()
        if last_test!=None:
            testVersion = last_test.test_id
        else:
            testVersion = 0

        # create the response
        response = messages_pb2.SendReportResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion

        # send back response
        response_str = agent.encodeMessage(response.SerializeToString())
        return response_str


class SendServiceReportHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("sendServiceReport received")

        # get agent info
        agentID = request.POST['agentID']
        agent = Agent.getAgent(agentID)

        # decode received message
        msg = agent.decodeMessage(request.POST['msg'])

        receivedServiceReport = messages_pb2.SendServiceReport()
        receivedServiceReport.ParseFromString(msg)

        # add service report
        serviceReport = ServiceReport.create(receivedServiceReport, agent.user)

        # send report to decision system
        DecisionSystem.newReport(serviceReport)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        last_test = Test.get_last_test()
        if last_test!=None:
            testVersion = last_test.test_id
        else:
            testVersion = 0

        # create the response
        response = messages_pb2.SendReportResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion

        # send back response
        response_str = agent.encodeMessage(response.SerializeToString())
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
        last_test = Test.get_last_test()
        if last_test!=None:
            testVersion = last_test.test_id
        else:
            testVersion = 0

        # create the response
        response = messages_pb2.NewVersionResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion
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

        # get agent info
        agentID = request.POST['agentID']
        agent = Agent.getAgent(agentID)

        # decode received message
        msg = agent.decodeMessage(request.POST['msg'])

        receivedMsg = messages_pb2.NewTests()
        receivedMsg.ParseFromString(msg)

        newTests = Test.getUpdatedTests(receivedMsg.currentTestVersionNo)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        last_test = Test.get_last_test()
        if last_test!=None:
            testVersion = last_test.test_id
        else:
            testVersion = 0

        # create the response
        response = messages_pb2.NewTestsResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion
        response.testVersionNo = testVersion

        for newTest in newTests:
            test = response.tests.add()
            test.testID = newTest.test.testID
            # TODO: get execution time
            test.executeAtTimeUTC = 4000

            if isinstance(newTest, WebsiteTest):
                test.testType = "WEB"
                test.website.url = newTest.website_url
            elif isinstance(newTest, ServiceTest):
                test.testType = "SERVICE"
                test.service.name = newTest.service_name
                test.service.port = newTest.port
                test.service.ip = newTest.ip

        # send back response
        response_str = agent.encodeMessage(response.SerializeToString())
        return response_str


class WebsiteSuggestionHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("websiteSuggestion received")

        # get agent info
        agentID = request.POST['agentID']
        agent = Agent.getAgent(agentID)

        # decode received message
        msg = agent.decodeMessage(request.POST['msg'])

        receivedWebsiteSuggestion = messages_pb2.WebsiteSuggestion()
        receivedWebsiteSuggestion.ParseFromString(msg)

        logging.info("Aggregator: registering website suggestion %s from agent %s" % (receivedWebsiteSuggestion.websiteURL, agentID))

        # create the suggestion
        webSiteSuggestion = WebsiteSuggestion.create(receivedWebsiteSuggestion, agent.user)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        last_test = Test.get_last_test()
        if last_test!=None:
            testVersion = last_test.test_id
        else:
            testVersion = 0

        # create the response
        response = messages_pb2.TestSuggestionResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion

        # send back response
        response_str = agent.encodeMessage(response.SerializeToString())
        return response_str


class ServiceSuggestionHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("serviceSuggestion received")

        # get agent info
        agentID = request.POST['agentID']
        agent = Agent.getAgent(agentID)

        # decode received message
        msg = agent.decodeMessage(request.POST['msg'])

        receivedServiceSuggestion = messages_pb2.ServiceSuggestion()
        receivedServiceSuggestion.ParseFromString(msg)

        logging.info("Aggregator: registering service suggestion %s on %s(%s):%s from agent %s" %
                     (receivedServiceSuggestion.serviceName, receivedServiceSuggestion.hostName,
                         receivedServiceSuggestion.ip, receivedServiceSuggestion.port, agentID))

        # create the suggestion
        serviceSuggestion = ServiceSuggestion.create(receivedServiceSuggestion, agent.user)

        # get software version information
        if agent.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        last_test = Test.get_last_test()
        if last_test!=None:
            testVersion = last_test.test_id
        else:
            testVersion = 0

        # create the response
        response = messages_pb2.TestSuggestionResponse()
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion

        # send back response
        response_str = agent.encodeMessage(response.SerializeToString())
        return response_str


class CheckAggregator(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        logging.info("CheckAggregator received")
        
        msg = base64.b64decode(request.POST['msg'])

        checkAggregator = messages_pb2.CheckAggregator()
        checkAggregator.ParseFromString(msg)

        # get software version information
        if checkAggregator.agentType=='DESKTOP':
            softwareVersion = DesktopAgentVersion.getLastVersionNo()
        else:
            softwareVersion = MobileAgentVersion.getLastVersionNo()

        # get last test id
        last_test = Test.get_last_test()
        if last_test!=None:
            testVersion = last_test.test_id
        else:
            testVersion = 0

        # create the response
        response = messages_pb2.CheckAggregatorResponse()
        response.status = "ON"
        response.header.currentVersionNo = softwareVersion.version
        response.header.currentTestVersionNo = testVersion

        # send back response
        response_str = base64.b64encode(response.SerializeToString())
        return response_str


class TestsHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
#
#        # create website report
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
#
#
#
#        # create service report
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

#
#
#
#
#        # get peers
#        try:
#            c = Client()
#            getpeer = messages_pb2.GetPeerList()
#            getpeer.header.token = "token"
#            getpeer.header.agentID = 1309
#
#            getpeer_str = base64.b64encode(getpeer.SerializeToString())
#            response = c.post('/api/getpeerlist/', {'msg': getpeer_str})
#
#            msg = base64.b64decode(response.content)
#
#            resp = messages_pb2.GetPeerListResponse()
#            resp.ParseFromString(msg)
#
#            for peer in resp.knownPeers:
#                msg = "Peer %s - %s:%s - %s (%s,%s)" % (peer.agentID, peer.agentIP, peer.agentPort, peer.peerStatus, peer.publicKey.mod, peer.publicKey.exp)
#                logging.info(msg)
#
#        except Exception, inst:
#            logging.error(inst)
#
#
#
#        try:
#            c = Client()
#            getpeer = messages_pb2.GetSuperPeerList()
#            getpeer.header.token = "token"
#            getpeer.header.agentID = 103
#            getpeer.count = 10
#
#            getpeer_str = base64.b64encode(getpeer.SerializeToString())
#            logging.debug(getpeer_str)
#            response = c.post('/api/getsuperpeerlist/', {'msg': getpeer_str})
#
#            msg = base64.b64decode(response.content)
#
#            resp = messages_pb2.GetSuperPeerListResponse()
#            resp.ParseFromString(msg)
#
#            for peer in resp.knownPeers:
#                logging.info("New peer" + str(peer.agentID))
#
#        except Exception, inst:
#            logging.error(inst)
#
#        from geoip import core
#        service = core.GeoIp()
#
#        return HttpResponse(str(service.getIPLocation('209.85.146.106')))

        try:
            c = Client()
            crypto = CryptoLib()

            mod = 109916896023924130410814755146616820050848287195403807165245502023708307057182505344954954927069297885076677369989575235572225938578405052695849113605912075520043830304524405776689005895802218122674008335365710906635693457269579474788929265226007718176605597921238270933430352422527094012100555192243443310437
            exp = 65537
            d = 53225089572596125525843512131740616511492292813924040166456597139362240024103739980806956293552408080670588466616097320611022630892254518017345493694914613829109122334102313231580067697669558510530796064276699226938402801350068277390981376399696367398946370139716723891915686772368737964872397322242972049953
            p = 9311922438153331754523459805685209527234133766003151707083260807995975127756369273827143717722693457161664179598414082626988492836607535481975170401420233
            q = 11803888697952041452190425894815849667220518916298985642794987864683223570209190956951707407347610933271302068443002899691276141395264850489845154413900989
            u = 4430245984407139797364141151557666474447820733910504072636286162751503313976630067126466513743819690811621510073670844704114936437585335006336955101762559


            # generate AES key
            AESKey = crypto.generateAESKey()
            agentKey = RSAKey(mod, exp, d, p, q, u)
            aggregatorKey = RSAKey(settings.RSAKEY_MOD, settings.RSAKEY_EXP, settings.RSAKEY_D, settings.RSAKEY_P, settings.RSAKEY_Q, settings.RSAKEY_U)

            registerMsg = messages_pb2.RegisterAgent()
            registerMsg.versionNo = 1
            registerMsg.agentType = "DESKTOP"
            registerMsg.credentials.username = "zeux1"
            registerMsg.credentials.password = "123"
            registerMsg.agentPublicKey.mod = str(mod)
            registerMsg.agentPublicKey.exp = str(exp)
            registerMsg.ip = "192.168.2.1"

            registerMsgSerialized = registerMsg.SerializeToString()
            registerMsg_str = crypto.encodeAES(registerMsgSerialized, AESKey)

            key_str = crypto.encodeRSAPublicKey(AESKey, aggregatorKey)


            response_str = c.post('/api/registeragent/', {'msg': registerMsg_str, 'key': key_str})


            # REGISTRATION DONE
            # BEGIN LOGIN STEP 1

            response_decoded = crypto.decodeAES(response_str.content, AESKey)

            response = messages_pb2.RegisterAgentResponse()
            response.ParseFromString(response_decoded)

            logging.info("Registered: %d" % response.agentID)

            firstchallenge = crypto.generateChallenge()
            logging.info("Challenge generated on agent: %s" % firstchallenge)

            loginMsg = messages_pb2.Login()
            loginMsg.agentID = response.agentID;
            loginMsg.challenge = firstchallenge
            loginMsg.port = 9090
            loginMsg.ip = "209.85.169.99"

            loginMsg_str = base64.b64encode(loginMsg.SerializeToString())

            response_str = c.post('/api/loginagent/', {'msg': loginMsg_str})


            # LOGIN STEP 1 done
            # BEGIN LOGIN STEP 2

            msg = base64.b64decode(response_str.content)

            logging.info("Login step1 received")

            response = messages_pb2.LoginStep1()
            response.ParseFromString(msg)

            challenge = response.challenge
            cipheredChallenge = crypto.signRSA(challenge, agentKey)

            logging.info("Challenge received from aggregator: %s" % challenge)

            # check challenge
            if crypto.verifySignatureRSA(firstchallenge, response.cipheredChallenge, aggregatorKey):
                logging.info("AGENT: CHALLENGE OK")
            else:
                logging.info("AGENT: CHALLENGE NOT OK")

            loginMsg = messages_pb2.LoginStep2()
            loginMsg.processID = response.processID
            loginMsg.cipheredChallenge = cipheredChallenge

            loginMsg_str = base64.b64encode(loginMsg.SerializeToString())

            response_str = c.post('/api/loginagent2/', {'msg': loginMsg_str})

            logging.info("Login response received")




        except Exception,e:
            logging.error(e)

        
        return HttpResponse(str(IPRange.ip_location('209.85.146.106').dump()))

