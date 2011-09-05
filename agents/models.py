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

from django.db import models
from django.db.models import Q
from agents.RSACrypto import *
from geoip import geoip
from django.contrib.auth.models import User
import logging, random


class LoggedAgent(models.Model):
    agentID       = models.IntegerField(primary_key=True)
    country       = models.CharField(max_length=2)
    latitude      = models.FloatField()
    longitude     = models.FloatField()
    current_ip    = models.CharField(max_length=255)
    port          = models.PositiveIntegerField()
    agentInfo     = models.ForeignKey('Agent')
    superPeer     = models.BooleanField()
    publicKeyMod  = models.TextField()
    publicKeyExp  = models.TextField()

    def getAgent(agentID):
        return LoggedAgent.objects.get(agentID=agentID)

    def _getPeers(agentID, country, superPeer, totalPeers):
        selectedPeers = []
        # create list with already selected agent ids
        peersIDs = [agentID]

        # select near peers
        nearPeers = list(LoggedAgent.objects.filter(Q(country=country), Q(superPeer=superPeer), ~Q(agentID__in=peersIDs)))

        # if more peers are needed, get far peers
        neededPeers = totalPeers-len(nearPeers)
        if neededPeers>0:

            # list of peer ids to exclude
            for peer in nearPeers:
                peersIDs.append(peer.agentID)

            # select far peers
            farPeers = list(LoggedAgent.objects.filter(~Q(agentID__in=peersIDs), Q(superPeer=superPeer)))
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
                    peersIDs.append(peer.agentID)

                # select offline peers sorted by uptime
                offlinePeers = list(Agent.objects.filter(Q(superPeer=superPeer), ~Q(agentID__in=peersIDs), Q(uptime__gt=0)).order_by('-uptime'))

                if len(offlinePeers)>0:
                    selectedPeers.extend(offlinePeers[:neededPeers])

        else:
            # shuffle peers
            random.shuffle(nearPeers)
            # just select totalPeers
            selectedPeers.extend(nearPeers[:totalPeers])

        return selectedPeers

    def __unicode__(self):
        return "Agent %s at %s" % (self.agentID, self.country)

    getAgent = staticmethod(getAgent)
    _getPeers = staticmethod(_getPeers)


class Agent(models.Model):
    agentID       = models.AutoField(primary_key=True)
    agentType     = models.CharField(max_length=10)
    agentVersion  = models.PositiveIntegerField()
    registered_at = models.DateTimeField(auto_now_add=True)
    registered_ip = models.CharField(max_length=255)
    publicKeyMod  = models.TextField()
    publicKeyExp  = models.TextField()
    country       = models.CharField(max_length=2)
    superPeer     = models.BooleanField(default=False)
    latitude      = models.FloatField()
    longitude     = models.FloatField()
    uptime        = models.BigIntegerField(default=0)
    user          = models.ForeignKey('auth.user', null=True)
    lastKnownIP   = models.CharField(max_length=255, null=True)
    lastKnownPort = models.PositiveIntegerField(null=True)
    lastKnownCountry   = models.CharField(max_length=2, null=True)
    lastKnownLatitude  = models.FloatField(null=True)
    lastKnownLongitude = models.FloatField(null=True)
    # flag to know if agent has finished the register process
    activated     = models.BooleanField(default=False)
    # flag to mark agent as blocked (if blocked agent will not be able to login)
    blocked       = models.BooleanField(default=False)

    def create(versionNo, agentType, ip):
        agent = Agent()
        agent.agentVersion = versionNo
        agent.agentType = agentType
        agent.registered_ip = ip
        agent.uptime = random.randint(100, 10000)

        # get country by geoip
        service = geoip.GeoIp()
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

        # save public key
        self.publicKeyMod = str(keyPair['public'].mod)
        self.publicKeyExp = str(keyPair['public'].exp)
        self.save()

        return keyPair

    def promoteToSuperPeer(self):
        self.superPeer = True
        self.save()

    def demoteToPeer(self):
        self.superPeer = False
        self.save()

    def login(self, ip, port):
        # TODO: check login
        LoggedAgent.objects.filter(agentID=self.agentID).delete()
        loggedAgent = LoggedAgent()
        loggedAgent.agentID = self.agentID
        loggedAgent.agentInfo = self
        loggedAgent.current_ip = ip
        loggedAgent.port = port
        loggedAgent.superPeer = self.superPeer
        loggedAgent.publicKeyMod = self.publicKey.mod
        loggedAgent.publicKeyExp = self.publicKey.exp

        # get country by geoip
        service = geoip.GeoIp()
        location = service.getIPLocation(ip)
        loggedAgent.country = location['country_code']
        loggedAgent.latitude = location['latitude']
        loggedAgent.longitude = location['longitude']

        loggedAgent.save()

        # update agent information
        self.lastKnownCountry = location['country_code']
        self.lastKnownLatitude = location['latitude']
        self.lastKnownLongitude = location['longitude']
        self.lastKnownIP = ip
        self.lastKnownPort = port
        self.save()

    def logout(self):
        # TODO: update uptime
        LoggedAgent.objects.filter(agentID=self.agentID).delete()

    def getPeers(agentID, country, totalPeers=100):
        #return Agent._getPeers(country, False, totalPeers)
        return LoggedAgent._getPeers(agentID, country, False, totalPeers)

    def getSuperPeers(agentID, country, totalPeers=100):
        #return Agent._getPeers(country, True, totalPeers)
        return LoggedAgent._getPeers(agentID, country, True, totalPeers)

    def getAgent(agentID):
        return Agent.objects.get(agentID=agentID)

    def getCurrentLocation(self):
        try:
            loggedAgent = LoggedAgent.getAgent(self.agentID)
        except Exception, e:
            logging.error(e)
        return loggedAgent.country
        

    def __unicode__(self):
        return "Agent %s (%s %s) - %s at %s - up %s" % (self.agentID, self.agentType, self.agentVersion, self.registered_ip, self.country, self.uptime)

    create = staticmethod(create)
    getPeers = staticmethod(getPeers)
    getSuperPeers = staticmethod(getSuperPeers)
    getAgent = staticmethod(getAgent)