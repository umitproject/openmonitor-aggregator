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

# Django imports
from django.test import TestCase
from django.test.client import Client
from messages import messages_pb2
from agents.CryptoLib import *
import base64
import settings
import logging


mod = 109916896023924130410814755146616820050848287195403807165245502023708307057182505344954954927069297885076677369989575235572225938578405052695849113605912075520043830304524405776689005895802218122674008335365710906635693457269579474788929265226007718176605597921238270933430352422527094012100555192243443310437
exp = 65537
d = 53225089572596125525843512131740616511492292813924040166456597139362240024103739980806956293552408080670588466616097320611022630892254518017345493694914613829109122334102313231580067697669558510530796064276699226938402801350068277390981376399696367398946370139716723891915686772368737964872397322242972049953
p = 9311922438153331754523459805685209527234133766003151707083260807995975127756369273827143717722693457161664179598414082626988492836607535481975170401420233
q = 11803888697952041452190425894815849667220518916298985642794987864683223570209190956951707407347610933271302068443002899691276141395264850489845154413900989
u = 4430245984407139797364141151557666474447820733910504072636286162751503313976630067126466513743819690811621510073670844704114936437585335006336955101762559


crypto = CryptoLib()


class AgentTests():

    def __init__(self, agentID=None):
        # create http client
        self.client = Client()

        # keys
        self.aggregatorKey = RSAKey(settings.RSAKEY_MOD, settings.RSAKEY_EXP, settings.RSAKEY_D, settings.RSAKEY_P, settings.RSAKEY_Q, settings.RSAKEY_U)
        self.agentKey = RSAKey(mod, exp, d, p, q, u)
        self.AESKey = crypto.generateAESKey()

        # agent properties
        self.agentVersion = 1
        self.agentType = "DESKTOP"
        self.user_username = "zeux1"
        self.user_password = "123"
        self.register_ip = "192.168.2.1"
        self.login_ip = "209.85.169.99"
        self.port = 9090
        self.last_test = 0

        # need to registerAgent ?
        if agentID==None:
            self.agentID = self.registerAgent()
        else:
            self.agentID = agentID

        # login agent
        self.loginAgent()


    def registerAgent(self):
        registerMsg = messages_pb2.RegisterAgent()
        registerMsg.versionNo = self.agentVersion
        registerMsg.agentType = self.agentType
        registerMsg.credentials.username = self.user_username
        registerMsg.credentials.password = self.user_password
        registerMsg.agentPublicKey.mod = str(mod)
        registerMsg.agentPublicKey.exp = str(exp)
        registerMsg.ip = self.register_ip

        registerMsgSerialized = registerMsg.SerializeToString()
        registerMsg_str = crypto.encodeAES(registerMsgSerialized, self.AESKey)

        key_str = crypto.encodeRSAPublicKey(self.AESKey, self.aggregatorKey)

        response_str = self.client.post('/api/registeragent/', {'msg': registerMsg_str, 'key': key_str})

        response_decoded = crypto.decodeAES(response_str.content, self.AESKey)

        response = messages_pb2.RegisterAgentResponse()
        response.ParseFromString(response_decoded)

        return response.agentID


    def loginAgent(self):

        firstchallenge = crypto.generateChallenge()

        loginMsg = messages_pb2.Login()
        loginMsg.agentID = self.agentID;
        loginMsg.challenge = firstchallenge
        loginMsg.port = self.port
        loginMsg.ip = self.login_ip

        loginMsg_str = base64.b64encode(loginMsg.SerializeToString())

        response_str = self.client.post('/api/loginagent/', {'msg': loginMsg_str})

        # LOGIN STEP 1 done
        # BEGIN LOGIN STEP 2
        msg = base64.b64decode(response_str.content)

        response = messages_pb2.LoginStep1()
        response.ParseFromString(msg)

        challenge = response.challenge
        cipheredChallenge = crypto.signRSA(challenge, self.agentKey)

        # check challenge
        if crypto.verifySignatureRSA(firstchallenge, response.cipheredChallenge, self.aggregatorKey):
            logging.info("AGENT: CHALLENGE OK")
        else:
            logging.info("AGENT: CHALLENGE NOT OK")

        loginMsg = messages_pb2.LoginStep2()
        loginMsg.processID = response.processID
        loginMsg.cipheredChallenge = cipheredChallenge

        loginMsg_str = base64.b64encode(loginMsg.SerializeToString())

        response_str = self.client.post('/api/loginagent2/', {'msg': loginMsg_str})

        logging.info("Agent logged")


    def sendWebsiteSuggestion(self, website="www.website.com"):
        logging.info("Agent: sending website suggestion - %s" % website)
        msg = messages_pb2.WebsiteSuggestion()
        msg.websiteURL = website
        msg_encoded = crypto.encodeAES(msg.SerializeToString(), self.AESKey)
        
        response = self.client.post('/api/websitesuggestion/', {'agentID': self.agentID, 'msg': msg_encoded})

        websiteSuggestResponse = messages_pb2.TestSuggestionResponse()
        websiteSuggestResponse.ParseFromString(crypto.decodeAES(response.content, self.AESKey))

        currentVersionNo = websiteSuggestResponse.header.currentVersionNo
        currentTestVersionNo = websiteSuggestResponse.header.currentTestVersionNo

        logging.info("Agent: response received - last_test=%s last_version=%s" % (currentTestVersionNo, currentVersionNo))


    def sendServiceSuggestion(self, service_name="smtp", hostname="www.host.com", ip="1.2.3.4", port=90):
        logging.info("Agent: sending service suggestion - %s on %s(%s):%s" % (service_name,hostname,ip,port))
        msg = messages_pb2.ServiceSuggestion()
        msg.serviceName = service_name
        msg.hostName = hostname
        msg.ip = ip
        msg.port = port
        msg_encoded = crypto.encodeAES(msg.SerializeToString(), self.AESKey)

        response = self.client.post('/api/servicesuggestion/', {'agentID': self.agentID, 'msg': msg_encoded})

        serviceSuggestResponse = messages_pb2.TestSuggestionResponse()
        serviceSuggestResponse.ParseFromString(crypto.decodeAES(response.content, self.AESKey))

        currentVersionNo = serviceSuggestResponse.header.currentVersionNo
        currentTestVersionNo = serviceSuggestResponse.header.currentTestVersionNo

        logging.info("Agent: response received - last_test=%s last_version=%s" % (currentTestVersionNo, currentVersionNo))


    def checkAggregator(self):
        logging.info("Agent: cheking aggregator status")
        msg = messages_pb2.CheckAggregator()
        msg.agentType = self.agentType

        msg_str = base64.b64encode(msg.SerializeToString())
        response = self.client.post('/api/checkaggregator/', {'msg': msg_str})

        msg = base64.b64decode(response.content)

        checkAggregator = messages_pb2.CheckAggregatorResponse()
        checkAggregator.ParseFromString(msg)

        logging.info("Aggregator is " + checkAggregator.status)


    def checkNewVersion(self):
        logging.info("Agent: checking new version")
        newversion = messages_pb2.NewVersion()
        newversion.agentVersionNo = self.agentVersion
        newversion.agentType = self.agentType
        newt_str = base64.b64encode(newversion.SerializeToString())
        response = self.client.post('/api/checkversion/', {'msg': newt_str})

        msg = base64.b64decode(response.content)
        nv = messages_pb2.NewVersionResponse()
        nv.ParseFromString(msg)

        url = ''
        if nv.HasField('downloadURL'):
            url = nv.downloadURL

        logging.info("Last version available is %s - %s" % (nv.versionNo, url))


    def checkNewTests(self):
        logging.info("Agent: checking new tests")
        newtests = messages_pb2.NewTests()
        newtests.currentTestVersionNo = self.last_test
        newt_str = crypto.encodeAES(newtests.SerializeToString(), self.AESKey)
        response = self.client.post('/api/checktests/', {'agentID': self.agentID, 'msg': newt_str})

        logging.info(response.content)

        msg = crypto.decodeAES(response.content, self.AESKey)
        tests = messages_pb2.NewTestsResponse()
        tests.ParseFromString(msg)

        logging.info("Last available test is %s" % tests.testVersionNo)
        logging.info("New tests are: %s" % tests.tests)


class APITestCase(TestCase):

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.agentID = registerAgent(self.client)

    def test_sendWebsiteSuggestion(self):
        msg = messages_pb2.WebsiteSuggestion()
        msg.header.token = "token"
        msg.header.agentID = 5
        msg.websiteURL = "www.example.com"
        msg_encoded = base64.b64encode(msg.SerializeToString())

        response = self.client.post('/api/websitesuggestion/', {'msg': msg_encoded})

        websiteSuggestResponse = messages_pb2.TestSuggestionResponse()
        websiteSuggestResponse.ParseFromString(base64.b64decode(response.content))

        currentVersionNo = websiteSuggestResponse.header.currentVersionNo
        currentTestVersionNo = websiteSuggestResponse.header.currentTestVersionNo

        self.assertEqual(currentVersionNo, 1, 'incorrect version no')
        self.assertEqual(currentTestVersionNo, 2, 'incorrect test version no')


    def test_sendServiceSuggestion(self):
        msg = messages_pb2.ServiceSuggestion()
        msg.header.token = "token"
        msg.header.agentID = 5
        msg.serviceName = "p2p"
        msg.emailAddress = "teste@domain.com"
        msg.hostName = "www.domain.com"
        msg.ip = "127.0.0.1"
        msg_encoded = base64.b64encode(msg.SerializeToString())

        response = self.client.post('/api/servicesuggestion/', {'msg': msg_encoded})

        serviceSuggestResponse = messages_pb2.TestSuggestionResponse()
        serviceSuggestResponse.ParseFromString(base64.b64decode(response.content))

        currentVersionNo = serviceSuggestResponse.header.currentVersionNo
        currentTestVersionNo = serviceSuggestResponse.header.currentTestVersionNo

        self.assertEqual(currentVersionNo, 1, 'incorrect version no')
        self.assertEqual(currentTestVersionNo, 2, 'incorrect test version no')


    def test_checkNewVersion(self):
        msg = messages_pb2.NewVersion()
        msg.header.token = "token"
        msg.header.agentID = 5
        msg.agentVersionNo = 7
        msg.agentType = "DESKTOP"
        msg_encoded = base64.b64encode(msg.SerializeToString())

        response = self.client.post('/api/checkversion/', {'msg': msg_encoded})

        response_msg = messages_pb2.NewVersionResponse()
        response_msg.ParseFromString(base64.b64decode(response.content))

        currentVersionNo = response_msg.header.currentVersionNo
        currentTestVersionNo = response_msg.header.currentTestVersionNo
        downloadURL = response_msg.downloadURL
        versionNo = response_msg.versionNo

        self.assertEqual(currentVersionNo, 1, 'incorrect version no')
        self.assertEqual(currentTestVersionNo, 2, 'incorrect test version no')
        self.assertEqual(downloadURL, 'www.icm.com/newver', 'incorrect download url')
        self.assertEqual(versionNo, 4, 'incorrect new version no')


    def test_checkNewTests(self):
        msg = messages_pb2.NewTests()
        msg.header.token = "token"
        msg.header.agentID = 5
        msg.currentTestVersionNo = 49
        msg_encoded = base64.b64encode(msg.SerializeToString())

        response = self.client.post('/api/checktests/', {'msg': msg_encoded})

        response_msg = messages_pb2.NewTestsResponse()
        response_msg.ParseFromString(base64.b64decode(response.content))

        currentVersionNo = response_msg.header.currentVersionNo
        currentTestVersionNo = response_msg.header.currentTestVersionNo
        totalTests = len(response_msg.tests)
        testVersionNo = response_msg.testVersionNo
        test = response_msg.tests[0]
        testID = test.testID;
        websiteURL = test.websiteURL;
        executeAtTimeUTC = test.executeAtTimeUTC;

        self.assertEqual(currentVersionNo, 1, 'incorrect version no')
        self.assertEqual(currentTestVersionNo, 2, 'incorrect test version no')
        self.assertEqual(totalTests, 1, 'incorrect number of tests')
        self.assertEqual(testVersionNo, 70, 'incorrect test version no')
        self.assertEqual(testID, 1, 'incorrect test id')
        self.assertEqual(websiteURL, "www.example.com", 'incorrect test website url')
        self.assertEqual(executeAtTimeUTC, 4000, 'incorrect test execute time')


    def test_getEvents(self):
        msg = messages_pb2.GetEvents()
        msg.header.token = "token"
        msg.header.agentID = 5
        msg.geoLat = 20
        msg.geoLon = 10
        msg.locations.append("location1")
        msg_encoded = base64.b64encode(msg.SerializeToString())

        response = self.client.post('/api/getevents/', {'msg': msg_encoded})

        response_msg = messages_pb2.GetEventsResponse()
        response_msg.ParseFromString(base64.b64decode(response.content))

        currentVersionNo = response_msg.header.currentVersionNo
        currentTestVersionNo = response_msg.header.currentTestVersionNo
        event = response_msg.events[0]
        testType = event.testType
        eventType = event.eventType
        timeUTC = event.timeUTC
        sinceTimeUTC = event.sinceTimeUTC

        self.assertEqual(currentVersionNo, 1, 'incorrect version no')
        self.assertEqual(currentTestVersionNo, 2, 'incorrect test version no')
        self.assertEqual(testType, "WEB", 'incorrect event test type')
        self.assertEqual(eventType, "CENSOR", 'incorrect event type')
        self.assertEqual(timeUTC, 20, 'incorrect event timeutc')
        self.assertEqual(sinceTimeUTC, 10, 'incorrect event since time utc')


    def test_registerAgent(self):
        msg = messages_pb2.RegisterAgent()
        msg.ip = "127.0.0.1"
        msg.versionNo = 5
        msg_encoded = base64.b64encode(msg.SerializeToString())

        response = self.client.post('/api/registeragent/', {'msg': msg_encoded})

        response_msg = messages_pb2.RegisterAgentResponse()
        response_msg.ParseFromString(base64.b64decode(response.content))

        currentVersionNo = response_msg.header.currentVersionNo
        currentTestVersionNo = response_msg.header.currentTestVersionNo
        token = response_msg.token
        privateKey = response_msg.privateKey
        publicKey = response_msg.publicKey
        agentId = response_msg.agentID
        cipheredPublicKey = response_msg.cipheredPublicKey

        self.assertEqual(currentVersionNo, 1, 'incorrect version no')
        self.assertEqual(currentTestVersionNo, 2, 'incorrect test version no')
        self.assertEqual(token, 'token', 'incorrect token')
        self.assertEqual(privateKey, 'privatekey', 'incorrect privkey')
        self.assertEqual(publicKey, 'publickey', 'incorrect pubkey')
        self.assertEqual(cipheredPublicKey, 'cpublickey', 'incorrect ciphered pubkey')
        self.assertEqual(agentId, 5, 'incorrect agent id')


    def test_GetPeerList(self):
        msg = messages_pb2.GetPeerList()
        msg.header.token = "token"
        msg.header.agentID = 5
        msg_encoded = base64.b64encode(msg.SerializeToString())

        response = self.client.post('/api/getpeerlist/', {'msg': msg_encoded})

        response_msg = messages_pb2.GetPeerListResponse()
        response_msg.ParseFromString(base64.b64decode(response.content))

        currentVersionNo = response_msg.header.currentVersionNo
        currentTestVersionNo = response_msg.header.currentTestVersionNo
        knownPeer = response_msg.knownPeers[0]
        token = knownPeer.token
        publickey = knownPeer.publicKey
        status = knownPeer.peerStatus
        agentIP = knownPeer.agentIP
        agentPort = knownPeer.agentPort

        self.assertEqual(currentVersionNo, 1, 'incorrect version no')
        self.assertEqual(currentTestVersionNo, 2, 'incorrect test version no')
        self.assertEqual(token, "token", 'incorrect token')
        self.assertEqual(publickey, "publickey", 'incorrect pubkey')
        self.assertEqual(status, "ON", 'incorrect peer status')
        self.assertEqual(agentIP, "80.10.20.30", 'incorrect agent ip')
        self.assertEqual(agentPort, 50, 'incorrect agent port')


    def test_GetSuperPeerList(self):
        msg = messages_pb2.GetPeerList()
        msg.header.token = "token"
        msg.header.agentID = 5
        msg_encoded = base64.b64encode(msg.SerializeToString())

        response = self.client.post('/api/getsuperpeerlist/', {'msg': msg_encoded})

        response_msg = messages_pb2.GetSuperPeerListResponse()
        response_msg.ParseFromString(base64.b64decode(response.content))

        currentVersionNo = response_msg.header.currentVersionNo
        currentTestVersionNo = response_msg.header.currentTestVersionNo
        knownPeer = response_msg.knownSuperPeers[0]
        token = knownPeer.token
        publickey = knownPeer.publicKey
        status = knownPeer.peerStatus
        agentIP = knownPeer.agentIP
        agentPort = knownPeer.agentPort

        self.assertEqual(currentVersionNo, 1, 'incorrect version no')
        self.assertEqual(currentTestVersionNo, 2, 'incorrect test version no')
        self.assertEqual(token, "token", 'incorrect token')
        self.assertEqual(publickey, "publickey", 'incorrect pubkey')
        self.assertEqual(status, "ON", 'incorrect peer status')
        self.assertEqual(agentIP, "80.10.20.30", 'incorrect agent ip')
        self.assertEqual(agentPort, 50, 'incorrect agent port')


    def test_WebsiteReport(self):
        msg = messages_pb2.SendWebsiteReport()
        msg.header.token = "token"
        msg.header.agentID = 5
        msg.report.header.reportID = 1
        msg.report.header.agentID = 2
        msg.report.header.testID = 3
        msg.report.header.timeZone = 4
        msg.report.header.timeUTC = 5
        msg.report.header.passedNode.append("node 1")
        msg.report.report.websiteURL = "www.example.com"
        msg.report.report.statusCode = 200
        msg_encoded = base64.b64encode(msg.SerializeToString())

        response = self.client.post('/api/sendwebsitereport/', {'msg': msg_encoded})

        response_msg = messages_pb2.SendReportResponse()
        response_msg.ParseFromString(base64.b64decode(response.content))

        currentVersionNo = response_msg.header.currentVersionNo
        currentTestVersionNo = response_msg.header.currentTestVersionNo

        self.assertEqual(currentVersionNo, 1, 'incorrect version no')
        self.assertEqual(currentTestVersionNo, 2, 'incorrect test version no')


    def test_ServiceReport(self):
        msg = messages_pb2.SendServiceReport()
        msg.header.token = "token"
        msg.header.agentID = 5
        msg.report.header.reportID = 1
        msg.report.header.agentID = 2
        msg.report.header.testID = 3
        msg.report.header.timeZone = 4
        msg.report.header.timeUTC = 5
        msg.report.header.passedNode.append("node 1")
        msg.report.report.serviceName = "p2p"
        msg.report.report.statusCode = 200
        msg_encoded = base64.b64encode(msg.SerializeToString())

        response = self.client.post('/api/sendservicereport/', {'msg': msg_encoded})

        response_msg = messages_pb2.SendReportResponse()
        response_msg.ParseFromString(base64.b64decode(response.content))

        currentVersionNo = response_msg.header.currentVersionNo
        currentTestVersionNo = response_msg.header.currentTestVersionNo

        self.assertEqual(currentVersionNo, 1, 'incorrect version no')
        self.assertEqual(currentTestVersionNo, 2, 'incorrect test version no')


    def test_CheckAggregator(self):
        wreport = messages_pb2.CheckAggregator()
        wreport.header.token = "token"
        wreport.header.agentID = 3

        wreport_str = base64.b64encode(wreport.SerializeToString())
        response = c.post('/api/checkaggregator/', {'msg': wreport_str})

        msg = base64.b64decode(response.content)

        checkAggregator = messages_pb2.CheckAggregatorResponse()
        checkAggregator.ParseFromString(msg)

        logging.info("Aggregator is " + checkAggregator.status)
