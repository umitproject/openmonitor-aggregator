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
import time

from piston.handler import BaseHandler
from messages import messages_pb2
from suggestions.models import WebsiteSuggestion, ServiceSuggestion
from reports.models import WebsiteReport, ServiceReport

from django.test.client import Client
from django.http import HttpResponse
from django.conf import settings

from events.models import Event
from versions.models import DesktopAgentVersion, MobileAgentVersion
from icm_tests.models import Test, WebsiteTestUpdateAggregation, ServiceTestUpdateAggregation
from decision.decisionSystem import DecisionSystem
from agents.models import *
from agents.CryptoLib import *
from api.decorators import message_handler

import hashlib

from geoip.models import *



class RegisterAgentHandler(BaseHandler):
    allowed_methods = ('POST',)

    @message_handler(messages_pb2.RegisterAgent,
                     messages_pb2.RegisterAgentResponse)
    def create(self, request, register_obj, aes_key, agent,
               software_version, test_version, response):
        try:
            # get agent ip
            agent_ip = request.META['REMOTE_ADDR']
    
            # create agent
            publicKeyMod = register_obj.agentPublicKey.mod
            publicKeyExp = register_obj.agentPublicKey.exp
            username = register_obj.credentials.username
            password = register_obj.credentials.password
            agent = Agent.create(register_obj.versionNo,
                                 register_obj.agentType,
                                 agent_ip, publicKeyMod, publicKeyExp,
                                 username, password, aes_key)
            
            m = hashlib.sha1()
            m.update(agent.publicKeyMod)
            publicKeyHash = m.digest()
            
            try:
                response.agentID = agent.id
                response.publicKeyHash = crypto.encodeRSAPrivateKey(publicKeyHash,
                                                                    aggregatorKey)
            except Exception, e:
                logging.error("Failed while creating the register response: %s" % e)
    
            # send back response
            response_str = response.SerializeToString()
            return response_str
        except Exception, err:
            import pdb; pdb.set_trace()
            print err


class LoginHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        msg = base64.b64decode(request.POST['msg'])

        loginAgent = messages_pb2.Login()
        loginAgent.ParseFromString(msg)

        # get agent
        agent = Agent.get_agent(loginAgent.agentID)

        # get agent ip
        agentIp = request.META['REMOTE_ADDR']

        # initiate login process
        loginProcess = agent.initLogin(agentIp, loginAgent.port)
        
        if loginProcess:
            # initiate crypto to cipher challenge
            cipheredChallenge = crypto.signRSA(loginAgent.challenge, aggregatorKey)
    
            # create the response
            response = messages_pb2.LoginStep1()
            response.processID = loginProcess.processID
            response.cipheredChallenge = cipheredChallenge
            response.challenge = loginProcess.challenge
    
            # send back response
            response_str = base64.b64encode(response.SerializeToString())
            return response_str
        
        return "TRY AGAIN IN 1000 YEARS."


class Login2Handler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        msg = base64.b64decode(request.POST['msg'])

        loginAgent = messages_pb2.LoginStep2()
        loginAgent.ParseFromString(msg)

        # check login process
        agent = Agent.finishLogin(loginAgent.processID,
                                  loginAgent.cipheredChallenge)

        if agent is not None:
            # get software version information
            if agent.agent_type=='DESKTOP':
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

    @message_handler(messages_pb2.Logout,
                     messages_pb2.LogoutResponse)
    def create(self, request, logout_agent, aes_key, agent,
               software_version, test_version, response):
        agent.logout()
        
        response.status = "logged out"
        response_str = response.SerializeToString()
        
        return response_str


class GetPeerListHandler(BaseHandler):
    allowed_methods = ('POST',)

    @message_handler(messages_pb2.GetPeerList,
                     messages_pb2.GetPeerListResponse)
    def create(self, request, received_msg, aes_key, agent,
               software_version, test_version, response):
        if received_msg.HasField('count'):
            totalPeers = received_msg.count
        else:
            totalPeers = 100

        peers = agent.getPeers(totalPeers)
        for peer in peers:
            knownPeer = response.knownPeers.add()
            knownPeer.agentID = peer.agent_id
            knownPeer.token = peer.token
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
            response_str = response.SerializeToString()
        except Exception,e:
            logging.critical("Failed to serialize response for GetPeerList request. %s" % e)

        return response_str


class GetSuperPeerListHandler(BaseHandler):
    allowed_methods = ('POST',)

    @message_handler(messages_pb2.GetSuperPeerList,
                     messages_pb2.GetSuperPeerListResponse)
    def create(self, request, received_msg, aes_key, agent,
               software_version, test_version, response):
        if received_msg.HasField('count'):
            totalPeers = received_msg.count
        else:
            totalPeers = 100

        superpeers = agent.getSuperPeers(totalPeers)

        for peer in superpeers:
            knownSuperPeer = response.knownSuperPeers.add()
            knownSuperPeer.agentID = peer.agent_id
            knownSuperPeer.token = knownSuperPeer.token
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
        response_str = response.SerializeToString()
        
        return response_str

class GetNetlistHandler(BaseHandler):
    allowed_methods = ('POST',)

    @message_handler(messages_pb2.GetPeerList,
                     messages_pb2.GetNetlistResponse)
    def create(self, request, received_msg, aes_key, agent,
               software_version, test_version, response):
        count = received_msg.count if received_msg.count < settings.MAX_NETLIST_RESPONSE else settings.MAX_NETLIST_RESPONSE
        
        # TODO: Retrieve randomized list 
        netlist = IPRange.objects.all().order_by("-nodes_count")[:count]
        
        for net in netlist:
            network = response.networks.add()
            # NEED TO REFORMULATE THE MESSAGE AND AVOID SENDING SENSITIVE DATA
            network.start_ip =net.start_number
            network.end_ip = net.end_number
            network.nodesCount = net.nodes_count
            
            for agent in net.logged_agents:
                ag = network.nodes.add()
                ag.agentID = agent.id
                ag.agentIP = agent.current_ip
                ag.agentPort = agent.port
                ag.token = agent.token
                ag.peerStatus = "ON"
                
                ag.publicKey.mod = agent.publicKeyMod
                ag.publicKey.exp = agent.publicKeyExp
        
        try:
            response_str = response.SerializeToString()
        except Exception,e:
            logging.critical("Failed to serialize response for GetNetlist request. %s" % e)
        
        return response_str


class GetBanlistHandler(BaseHandler):
    allowed_methods = ('POST',)

    @message_handler(messages_pb2.GetBanlist,
                     messages_pb2.GetBanlistResponse)
    def create(self, request, received_msg, aes_key, agent,
               software_version, test_version, response):
        banned_agents = BannedAgents.banned_agent_ids()
        response.nodes_count = len(banned_agents)
        for ban in banned_agents:
            response.agent_ids.append(ban)
        
        # send back response
        try:
            response_str = response.SerializeToString()
        except Exception,e:
            logging.critical("Failed to serialize response for GetBanlist request. %s" % e)

        return response_str


class GetBannetsHandler(BaseHandler):
    allowed_methods = ('POST',)

    @message_handler(messages_pb2.GetPeerList,
                     messages_pb2.GetPeerListResponse)
    def create(self, request, received_msg, aes_key, agent,
               software_version, test_version, response):
        banets = BannedNetworks.objects.all()
        for bn in banets:
            net = response.networks.add()
            net.start_ip = bn.start_number
            net.end_ip = bn.end_number
            net.nodes_count = bn.nodes_count
            net.flags = bn.flags
        
        # send back response
        try:
            response_str = response.SerializeToString()
        except Exception,e:
            logging.critical("Failed to serialize response for GetBannets request. %s" % e)

        return response_str


class GetEventsHandler(BaseHandler):
    allowed_methods = ('POST',)

    @message_handler(messages_pb2.GetEvents,
                     messages_pb2.GetEventsResponse)
    def create(self, request, received_msg, aes_key, agent,
               software_version, test_version, response):
        regions = received_msg.locations
        events = Event.get_active_events_region(regions)

        for event in events:
            e = response.events.add()
            e.testType = event.get_target_type()
            e.eventType = event.get_event_type()
            e.timeUTC = int(event.last_detection_utc.strftime("%s"))
            e.sinceTimeUTC = int(event.first_detection_utc.strftime("%s"))
            for i in range(0,len(event.lats)):
                location = e.locations.add()
                location.longitude = event.lons[i]
                location.latitude = event.lats[i]

        # send back response
        response_str = response.SerializeToString()
        
        return response_str


class SendWebsiteReportHandler(BaseHandler):
    allowed_methods = ('POST',)

    @message_handler(messages_pb2.SendWebsiteReport,
                     messages_pb2.SendReportResponse)
    def create(self, request, received_website_report, aes_key, agent,
               software_version, test_version, response):
        # add website report
        webSiteReport = WebsiteReport.create(received_website_report, agent)

        # send report to decision system
        DecisionSystem.newReport(webSiteReport)

        # send back response
        response_str = response.SerializeToString()
        
        return response_str


class SendServiceReportHandler(BaseHandler):
    allowed_methods = ('POST',)

    @message_handler(messages_pb2.SendServiceReport,
                     messages_pb2.SendReportResponse)
    def create(self, request, received_service_report, aes_key, agent,
               software_version, test_version, response):
        # add service report
        serviceReport = ServiceReport.create(received_service_report, agent)

        # send report to decision system
        DecisionSystem.newReport(serviceReport)
        
        # send back response
        response_str = response.SerializeToString()
        
        return response_str


class CheckNewVersionHandler(BaseHandler):
    allowed_methods = ('POST',)

    @message_handler(messages_pb2.NewVersion,
                     messages_pb2.NewVersionResponse)
    def create(self, request, received_msg, aes_key, agent,
               software_version, test_version, response):
        response.versionNo = software_version.version
        
        if response.versionNo > received_msg.agentVersionNo:
            response.downloadURL = software_version.url
        
        # send back response
        response_str = response.SerializeToString()
        return response_str


class CheckNewTestHandler(BaseHandler):
    allowed_methods = ('POST',)

    @message_handler(messages_pb2.NewTests,
                     messages_pb2.NewTestsResponse)
    def create(self, request, received_msg, aes_key, agent,
               software_version, test_version, response):
        newTests = Test.get_updated_tests(received_msg.currentTestVersionNo)

        response.testVersionNo = test_version

        for newTest in newTests:
            test = response.tests.add()
            test.testID = newTest.test_id
            # TODO: get execution time
            test.executeAtTimeUTC = 4000

            if isinstance(newTest, WebsiteTestUpdateAggregation):
                test.testType = "WEB"
                test.website.url = newTest.website_url
            elif isinstance(newTest, ServiceTestUpdateAggregation):
                test.testType = "SERVICE"
                test.service.name = newTest.service_name
                test.service.port = newTest.port
                test.service.ip = newTest.ip

        # send back response
        response_str = response.SerializeToString()
        
        return response_str


class WebsiteSuggestionHandler(BaseHandler):
    allowed_methods = ('POST',)

    @message_handler(messages_pb2.WebsiteSuggestion,
                     messages_pb2.TestSuggestionResponse)
    def create(self, request, received_website_suggestion, aes_key, agent,
               software_version, test_version, response):
        # create the suggestion
        webSiteSuggestion = WebsiteSuggestion.create(received_website_suggestion, agent.user)

        # send back response
        response_str = response.SerializeToString()
        
        return response_str


class ServiceSuggestionHandler(BaseHandler):
    allowed_methods = ('POST',)

    @message_handler(messages_pb2.ServiceSuggestion,
                     messages_pb2.TestSuggestionResponse)
    def create(self, request, received_service_suggestion, aes_key, agent,
               software_version, test_version, response):
        # create the suggestion
        serviceSuggestion = ServiceSuggestion.create(received_service_suggestion,
                                                     agent.user)

        # send back response
        response_str = response.SerializeToString()
        
        return response_str


class CheckAggregator(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
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
#        try:
#            c = Client()
#            crypto = CryptoLib()
#
#            mod = 109916896023924130410814755146616820050848287195403807165245502023708307057182505344954954927069297885076677369989575235572225938578405052695849113605912075520043830304524405776689005895802218122674008335365710906635693457269579474788929265226007718176605597921238270933430352422527094012100555192243443310437
#            exp = 65537
#            d = 53225089572596125525843512131740616511492292813924040166456597139362240024103739980806956293552408080670588466616097320611022630892254518017345493694914613829109122334102313231580067697669558510530796064276699226938402801350068277390981376399696367398946370139716723891915686772368737964872397322242972049953
#            p = 9311922438153331754523459805685209527234133766003151707083260807995975127756369273827143717722693457161664179598414082626988492836607535481975170401420233
#            q = 11803888697952041452190425894815849667220518916298985642794987864683223570209190956951707407347610933271302068443002899691276141395264850489845154413900989
#            u = 4430245984407139797364141151557666474447820733910504072636286162751503313976630067126466513743819690811621510073670844704114936437585335006336955101762559
#
#
#            # generate AES key
#            AESKey = crypto.generateAESKey()
#            agentKey = RSAKey(mod, exp, d, p, q, u)
#            aggregatorKey = RSAKey(settings.RSAKEY_MOD, settings.RSAKEY_EXP, settings.RSAKEY_D, settings.RSAKEY_P, settings.RSAKEY_Q, settings.RSAKEY_U)
#
#            registerMsg = messages_pb2.RegisterAgent()
#            registerMsg.versionNo = 1
#            registerMsg.agentType = "DESKTOP"
#            registerMsg.credentials.username = "zeux1"
#            registerMsg.credentials.password = "123"
#            registerMsg.agentPublicKey.mod = str(mod)
#            registerMsg.agentPublicKey.exp = str(exp)
#            registerMsg.ip = "192.168.2.1"
#
#            registerMsgSerialized = registerMsg.SerializeToString()
#            registerMsg_str = crypto.encodeAES(registerMsgSerialized, AESKey)
#
#            key_str = crypto.encodeRSAPublicKey(AESKey, aggregatorKey)
#
#
#            response_str = c.post('/api/registeragent/', {'msg': registerMsg_str, 'key': key_str})
#
#
#            # REGISTRATION DONE
#            # BEGIN LOGIN STEP 1
#
#            response_decoded = crypto.decodeAES(response_str.content, AESKey)
#
#            response = messages_pb2.RegisterAgentResponse()
#            response.ParseFromString(response_decoded)
#
#            logging.info("Registered: %d" % response.agentID)
#
#            firstchallenge = crypto.generateChallenge()
#            logging.info("Challenge generated on agent: %s" % firstchallenge)
#
#            loginMsg = messages_pb2.Login()
#            loginMsg.agentID = response.agentID;
#            loginMsg.challenge = firstchallenge
#            loginMsg.port = 9090
#            loginMsg.ip = "209.85.169.99"
#
#            loginMsg_str = base64.b64encode(loginMsg.SerializeToString())
#
#            response_str = c.post('/api/loginagent/', {'msg': loginMsg_str})
#
#
#            # LOGIN STEP 1 done
#            # BEGIN LOGIN STEP 2
#
#            msg = base64.b64decode(response_str.content)
#
#            logging.info("Login step1 received")
#
#            response = messages_pb2.LoginStep1()
#            response.ParseFromString(msg)
#
#            challenge = response.challenge
#            cipheredChallenge = crypto.signRSA(challenge, agentKey)
#
#            logging.info("Challenge received from aggregator: %s" % challenge)
#
#            # check challenge
#            if crypto.verifySignatureRSA(firstchallenge, response.cipheredChallenge, aggregatorKey):
#                logging.info("AGENT: CHALLENGE OK")
#            else:
#                logging.info("AGENT: CHALLENGE NOT OK")
#
#            loginMsg = messages_pb2.LoginStep2()
#            loginMsg.processID = response.processID
#            loginMsg.cipheredChallenge = cipheredChallenge
#
#            loginMsg_str = base64.b64encode(loginMsg.SerializeToString())
#
#            response_str = c.post('/api/loginagent2/', {'msg': loginMsg_str})
#
#            logging.info("Login response received")
#
#
#        except Exception,e:
#            logging.error(e)

        
        return HttpResponse(str(IPRange.ip_location('78.43.34.120').dump()))

