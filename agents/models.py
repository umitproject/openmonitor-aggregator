from django.db import models
from agents.RSACrypto import *
from geoip import geoip
import logging


class Agent(models.Model):
    agentID       = models.AutoField(primary_key=True)
    agentType     = models.CharField(max_length=10)
    agentVersion  = models.PositiveIntegerField()
    registered_at = models.DateTimeField(auto_now_add=True)
    registered_ip = models.CharField(max_length=255)
    publicKey     = models.ForeignKey('AgentRSAKey', null=True)
    country       = models.CharField(max_length=2)
    superPeer     = models.BooleanField(default=False)
    latitude      = models.FloatField()
    longitude     = models.FloatField()

    def create(versionNo, agentType, ip):
        agent = Agent()
        agent.agentVersion = versionNo
        agent.agentType = agentType
        agent.registered_ip = ip

        # get country by geoip
        service = geoip.GeoIp()
        logging.debug(service)
        location = service.getIPLocation(ip)
        agent.country = location['country_code']
        agent.latitude = location['latitude']
        agent.longitude = location['longitude']

        agent.save()
        return agent

    def generateKeys(self):
        # get new RSAKey pair
        crypto = RSACrypto()
        keyPair = crypto.getNewRSAKey()

        # save public key to datastore
        pk = AgentRSAKey()
        pk.mod = str(keyPair['public'].mod)
        pk.exp = str(keyPair['public'].exp)
        pk.save()

        # associate key with agent
        self.publicKey = pk
        self.save()

        return keyPair

    def promoteToSuperPeer(self):
        self.superPeer = True
        self.save()

    def demoteToPeer(self):
        self.superPeer = False
        self.save()

    def __unicode__(self):
        return "Agent %s (%s %s) - %s - %s" % (self.agentID, self.agentType, self.agentVersion, self.registered_at, self.registered_ip)

    create = staticmethod(create)


class AgentRSAKey(models.Model):
    mod = models.TextField()
    exp = models.TextField()