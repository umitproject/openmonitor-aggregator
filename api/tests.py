# Django imports
from django.test import TestCase
from django.test.client import Client
from messages import messages_pb2
import base64


class WebsiteSuggestionTestCase(TestCase):

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_sendWebsiteSuggestion(self):
        msg = messages_pb2.WebsiteSuggestion()
        msg.header.token = "token"
        msg.header.agentID = 5
        msg.websiteURL = "www.example.com"
        msg.emailAddress = "teste@domain.com"
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
