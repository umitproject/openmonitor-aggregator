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
        suggestion = messages_pb2.WebsiteSuggestion()
        suggestion.header.token = "token"
        suggestion.header.agentID = 5
        suggestion.websiteURL = "www.example.com"
        suggestion.emailAddress = "teste@domain.com"
        sug_str = base64.urlsafe_b64encode(suggestion.SerializeToString())

        response = self.client.post('/api/websitesuggestion/', {'msg': sug_str})

        #print response.content
        self.assertEqual(response.content, suggestion.websiteURL, 'not ok')
  