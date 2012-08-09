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
import random
import hashlib
import datetime

from django.db import models
from django.db.models import Q
from django.contrib.auth import authenticate
from django.core.cache import cache

from dbextra.fields import ListField
from dbextra.fields import CassandraKeyField

from agents.CryptoLib import *
from geoip.models import *



BAN_FLAGS = dict(
    abuse=1,
    robots=2,
    other=4
)

class LoginProcess(models.Model):
    processID     = models.AutoField(primary_key=True)
    agent_id       = CassandraKeyField()
    loginTime     = models.DateTimeField(auto_now_add=True)
    ip            = models.CharField(max_length=255)
    port          = models.PositiveIntegerField()
    challenge     = models.TextField()


class LoggedAgent(models.Model):
    agent_id = CassandraKeyField()
    country_code = models.CharField(max_length=2)
    country_name = models.CharField(max_length=100)
    location_id = models.IntegerField()
    location_name = models.CharField(max_length=300)
    state_region = models.CharField(max_length=2)
    city = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=6)
    latitude = models.DecimalField(decimal_places=20, max_digits=23)
    longitude = models.DecimalField(decimal_places=20, max_digits=23)
    current_ip = models.CharField(max_length=255)
    port = models.PositiveIntegerField() 
    superPeer = models.BooleanField()
    AESKey = models.TextField()
    publicKeyMod = models.TextField()
    publicKeyExp = models.TextField()
    token = models.CharField(max_length=56)
    
    @property
    def location(self):
        key = LOCATION_CACHE_KEY % self.location_id
        location = cache.get(key, False)
        if not location:
            location = Location.objects.get(id=self.location_id)
            cache.set(key, location, CACHE_EXPIRATION)
        return location

    @property
    def agent(self):
        key = AGENT_CACHE_KEY % self.agent_id
        agent = cache.get(key, False)
        if not agent:
            agent = Agent.objects.get(id=self.agent_id)
            cache.set(key, agent, CACHE_EXPIRATION)
        return agent

    def _getPeers(agent_id, country_code, superPeer, totalPeers):
        selectedPeers = []
        
        peersIDs = []

        # select near peers
        nearPeers = list(LoggedAgent.objects.filter(Q(country_code=country_code),
                                                    Q(superPeer=superPeer),
                                                    ~Q(agent_id=agent_id)))

        # if more peers are needed, get far peers
        neededPeers = totalPeers-len(nearPeers)
        if neededPeers>0:

            # list of peer ids to exclude
            for peer in nearPeers:
                peersIDs.append(peer.agent_id)

            # select far peers
            farPeers = list(LoggedAgent.objects.filter(~Q(agent_id=agent_id),
                                                       Q(superPeer=superPeer)))
            # shuffle peers
            random.shuffle(farPeers)

            if len(nearPeers)>0:
                selectedPeers.extend(nearPeers)
            if len(farPeers)>0:
                selectedPeers.extend(farPeers[:neededPeers])

            # if more peers are needed, get offline peers with best uptime
            neededPeers = totalPeers-len(nearPeers)-len(farPeers)
            if neededPeers>0:

                # list of peers ids to exclude
                for peer in farPeers:
                    peersIDs.append(peer.agent_id)

                # select offline peers sorted by uptime
                offlinePeers = list(Agent.objects.filter(\
                                    Q(superPeer=superPeer),
                                    ~Q(id=agent_id),
                                    Q(uptime__gt=0)).order_by('-uptime'))

                if len(offlinePeers)>0:
                    selectedPeers.extend(offlinePeers[:neededPeers])

        else:
            # shuffle peers
            random.shuffle(nearPeers)
            # just select totalPeers
            selectedPeers.extend(nearPeers[:totalPeers])

        return selectedPeers

    @staticmethod
    def getLoggedAgent(agent_id):
      return LoggedAgent.objects.get(agent_id=agent_id)

    def __unicode__(self):
        return "Agent %s at %s" % (self.agent_id, self.country_name)

    _getPeers = staticmethod(_getPeers)

class BannedAgents(models.Model):
    agent_ids = ListField(py_type=str)
    
    @classmethod
    def banned_agents(cls):
        banned = cls.objects.all()
        if len(banned) == 0:
            banned = cls()
            banned.save()
        else:
            banned = banned[0]
        return banned
    
    @classmethod
    def banned_agent_ids(cls):
        return cls.banned_agents().agent_ids
    
    @classmethod
    def add(cls, agent):
        banned = cls.banned_agents()
        if banned.agent_ids.count(agent.id):
            return False
        banned.agent_ids.append(agent.id)
        banned.save()
        
        return True
    
    @classmethod
    def remove(cls, agent):
        banned = cls.banned_agents()
        if banned.agent_ids.count(agent.id):
            return False
        
        banned.agent_ids.remove(agent.id)
        banned.save()
        
        return True

class Agent(models.Model):
    agent_type     = models.CharField(max_length=10)
    agentVersion  = models.PositiveIntegerField()
    registered_at = models.DateTimeField(auto_now_add=True)
    registered_ip = models.CharField(max_length=255)
    publicKeyMod  = models.TextField()
    publicKeyExp  = models.TextField()
    AESKey        = models.TextField()
    country       = models.CharField(max_length=2, null=True)
    superPeer     = models.BooleanField(default=False)
    latitude      = models.FloatField(null=True)
    longitude     = models.FloatField(null=True)
    uptime        = models.BigIntegerField(default=0)
    user          = models.ForeignKey('auth.user', null=True)
    lastKnownIP   = models.CharField(max_length=255, null=True)
    lastKnownPort = models.PositiveIntegerField(null=True)
    lastKnownCountry   = models.CharField(max_length=2, null=True)
    lastKnownLatitude  = models.DecimalField(decimal_places=20, max_digits=23, null=True)
    lastKnownLongitude = models.DecimalField(decimal_places=20, max_digits=23, null=True)
    # flag to know if agent has finished the register process
    activated     = models.BooleanField(default=False)
    # flag to mark agent as blocked (if blocked agent will not be able to login)
    banned = models.BooleanField(default=False)
    ban_flags = models.IntegerField(default=0)
    token = models.CharField(max_length=56)
    iprange_id = models.IntegerField(null=True)
    location_id = models.IntegerField(null=True)
    
    
    def ban(self, flags):
        self.banned = True
        if self.ban_flags is None or self.ban_flags == 0:
            self.ban_flags = flags
        else:
            self.ban_flags |= flags
        self.save()
        
        BannedAgents.add(self)
    
    def unban(self):
        self.banned = False
        self.ban_flags = 0
        self.save()
        
        BannedAgents.remove(self)
    
    @staticmethod
    def create(versionNo, agentType, ip,
               publicKeyMod, publicKeyExp,
               username, password, AESKey):
        from geoip.models import IPRange
        # check username and password
        user = authenticate(username=username, password=password)
        if user is not None and agentType in ["MOBILE", "DESKTOP"]:
            agent = Agent()
            agent.agentVersion = versionNo
            agent.agent_type = agentType
            agent.registered_ip = ip
            agent.uptime = 0
            agent.publicKeyMod = publicKeyMod
            agent.publicKeyExp = publicKeyExp
            agent.user = user
            agent.AESKey = AESKey
            agent.activated = True

            # get country by geoip
            iprange = IPRange.ip_location(ip)
            agent.country = iprange.location.country_code
            agent.latitude = iprange.location.lat
            agent.longitude = iprange.location.lon
            agent.iprange_id = iprange.id
            agent.location_id = iprange.location_id
            if agent.registered_at is None:
                agent.registered_at = datetime.datetime.now()

            agent.token = Agent.gen_token(agent)

            agent.save()
            
            return agent
        else:
            raise Exception("User not registered or login failed: user '%s'" % username)
    
    @staticmethod
    def gen_token(agent):
        return hashlib.sha224(\
            "%(username)s%(agent_id)s%(agent_type)s%(registered_ip)s%(registered_at)s" % \
                dict(username=agent.user.username,
                     agent_id=agent.id,
                     agent_type=agent.agent_type,
                     registered_ip=agent.registered_ip,
                     registered_at=agent.registered_at.strftime("%Y%m%d%H%M%S%z"))).hexdigest()

    def promoteToSuperPeer(self):
        self.superPeer = True
        self.save()

    def demoteToPeer(self):
        self.superPeer = False
        self.save()

    def initLogin(self, ip, port, crypto_v1):
        from geoip.models import IPRange

        if crypto_v1:
            from agents.CryptoLib_v1 import crypto, CryptoLib, aggregatorKey, aes_decrypt
        else:
            from agents.CryptoLib import crypto, CryptoLib, aggregatorKey, aes_decrypt

        # get new challenge
        if self.banned:
            return False

        from geoip.models import IPRange

        # Check if network is banned
        iprange = IPRange.ip_location(ip)
        if iprange and iprange.banned:
            return False
        
        crypto = CryptoLib()
        challenge = crypto.generateChallenge()
        
        loginProcess = LoginProcess()
        loginProcess.agent_id = self.id
        loginProcess.ip = ip
        loginProcess.port = port
        loginProcess.challenge = challenge
        loginProcess.save()

        return loginProcess
    
    @staticmethod
    def finishLogin(loginProcessID, cipheredChallenge, crypto_v1=False):
        from geoip.models import IPRange
        # get login process
        loginProcess = LoginProcess.objects.get(processID=loginProcessID)

        # get agent instance
        agent = Agent.get_agent(loginProcess.agent_id)

        # check challenge
        if agent.checkChallenge(str(loginProcess.challenge), cipheredChallenge,crypto_v1=crypto_v1):
            # delete already logged agent info
            LoggedAgent.objects.filter(agent_id=agent.id).delete()

            loggedAgent = LoggedAgent()
            loggedAgent.agent_id = agent.id
            loggedAgent.agentInfo = agent
            loggedAgent.current_ip = loginProcess.ip
            loggedAgent.port = loginProcess.port
            loggedAgent.superPeer = agent.superPeer
            loggedAgent.publicKeyMod = agent.publicKeyMod
            loggedAgent.publicKeyExp = agent.publicKeyExp
            loggedAgent.AESKey = agent.AESKey

            # get country by geoip
            from geoip.models import IPRange
            iprange = IPRange.ip_location(loginProcess.ip)
            loggedAgent.country_code = iprange.location.country_code
            loggedAgent.country_name = iprange.location.country_name
            loggedAgent.latitude = iprange.location.lat
            loggedAgent.longitude = iprange.location.lon
            loggedAgent.location_id = iprange.location_id
            loggedAgent.location_name = iprange.location.fullname
            loggedAgent.zipcode = iprange.location.zipcode
            loggedAgent.state_region = iprange.location.state_region
            loggedAgent.city = iprange.location.city
            loggedAgent.save()
            
            
            iprange.nodes_count += 1
            iprange.save()
            
            location = iprange.location
            location.nodes_count += 1
            location.save()
            
            
            # update agent information
            agent.lastKnownCountry = iprange.location.country_code
            agent.lastKnownLatitude = iprange.location.lat
            agent.lastKnownLongitude = iprange.location.lon
            agent.lastKnownIP = loginProcess.ip
            agent.lastKnownPort = loginProcess.port
            agent.save()

            # delete login process
            loginProcess.delete()
            
            return agent

        else:
            logging.error('Challenge not ok')
            raise Exception('Challenge not ok')
            return None

    def logout(self):
        # TODO: update uptime
        LoggedAgent.objects.filter(agent_id=self.id).delete()
        
        # Remove from networks list
        iprange = IPRange.ip_location(self.lastKnownIP)
        iprange.nodes_count -= 1
        iprange.save()
        
        location = iprange.location
        location.nodes_count -= 1
        location.save()

    def getPeers(self, totalPeers=100):
        #return Agent._getPeers(country, False, totalPeers)
        return LoggedAgent._getPeers(self.id,
                                     self.lastKnownCountry,
                                     False, totalPeers)

    def getSuperPeers(self, totalPeers=100):
        #return Agent._getPeers(country, True, totalPeers)
        return LoggedAgent._getPeers(self.id, self.lastKnownCountry, True, totalPeers)

    def encodeMessage(self, message):
        # get cryptolib instance
        crypt = CryptoLib()
        encoded = crypt.encodeAES(message, self.AESKey)
        return encoded

    def encodeMessageRSA(self, message):
        # get cryptolib instance
        crypt = CryptoLib()
        encoded = crypt.encodeRSAPublicKey(message, self.public_key)
        return encoded

    def decodeMessage(self, encodedMessage):
        # get cryptolib instance
        crypt = CryptoLib()
        message = crypt.decodeAES(encodedMessage, self.AESKey)
        return message

    def checkChallenge(self, originalChallenge, cipheredChallenge, crypto_v1=0):
        if crypto_v1:
            from agents.CryptoLib_v1 import crypto, CryptoLib, aggregatorKey, aes_decrypt
        else:
            from agents.CryptoLib import crypto, CryptoLib, aggregatorKey, aes_decrypt
        # get cryptolib instance
        crypt = CryptoLib()
        return crypt.verifySignatureRSA(originalChallenge,
                                        cipheredChallenge,
                                        self.public_key(crypto_v1))

    def getLoginInfo(self):
        return LoggedAgent.getLoggedAgent(self.id)

    def public_key(self, crypto_v1=False):
        if crypto_v1:
            from agents.CryptoLib_v1 import RSAKey
        else:
            from agents.CryptoLib import RSAKey
        key = PUBLIC_KEY_AGENT_CACHE_KEY % self.id
        pkey = cache.get(key, False)
        if not pkey:
            pkey = RSAKey(self.publicKeyMod, self.publicKeyExp)
            cache.set(key, pkey, CACHE_EXPIRATION)
        return pkey
    
    @property
    def iprange(self):
        key = IP_RANGE_CACHE_KEY % self.iprange_id
        iprange = cache.get(key, False)
        if not iprange:
            iprange = IPRange.objects.get(pk=self.iprange_id)
            cache.set(key, iprange, CACHE_EXPIRATION)
        return iprange
    
    @property
    def location(self):
        key = LOCATION_CACHE_KEY % self.location_id
        location = cache.get(key, False)
        if not location:
            location = Location.objects.get(pk=self.location_id)
            cache.set(key, location, CACHE_EXPIRATION)
        return location
    
    @staticmethod
    def get_agent(agent_id):
        return Agent.objects.get(id=agent_id)

    def __unicode__(self):
        return "Agent %s (%s %s) - %s at %s - up %s" % (self.id,
                                                        self.agent_type,
                                                        self.agentVersion,
                                                        self.registered_ip,
                                                        self.country,
                                                        self.uptime)


class BannedNetworks(models.Model):
    location_id = models.IntegerField()
    iprange_id = models.IntegerField()
    offending_nodes_count = models.IntegerField(default=0, null=True)


    @property
    def location(self):
        key = LOCATION_CACHE_KEY % self.location_id
        location = cache.get(key, False)
        if not location:
            location = Location.objects.get(id=self.location_id)
            cache.set(key, location, CACHE_EXPIRATION)
        return location
    
    @property
    def iprange(self):
        key = IP_RANGE_CACHE_KEY % self.iprange_id
        iprange = cache.get(key, False)
        if not iprange:
            iprange = IPRange.objects.get(id=self.iprange_id)
            cache.set(key, iprange, CACHE_EXPIRATION)
        return iprange


