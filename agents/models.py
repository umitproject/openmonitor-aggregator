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
import logging, random


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

    def _getPeers(country, superPeer, totalPeers):
        selectedPeers = []
        peers = list(Agent.objects.filter(country=country, superPeer=superPeer))

        neededPeers = totalPeers-len(peers)
        if neededPeers>0:
            # create list with already selected agent ids
            peersIDs = []
            for peer in peers:
                peersIDs.append(peer.agentID)

            # select more peers
            morePeers = list(Agent.objects.filter(~Q(agentID__in=peersIDs), Q(superPeer=superPeer)))
            # shuffle peers
            random.shuffle(morePeers)

            if len(peers)>0:
                selectedPeers.append(peers)
            if len(morePeers)>0:
                selectedPeers.append(morePeers[:neededPeers])

        else:
            # shuffle peers
            random.shuffle(peers)
            # just select totalPeers
            selectedPeers = peers[:totalPeers]

        return selectedPeers

    def getPeers(country, totalPeers=100):
        return Agent._getPeers(country, False, totalPeers)

    def getSuperPeers(country, totalPeers=100):
        return Agent._getPeers(country, True, totalPeers)

    def __unicode__(self):
        return "Agent %s (%s %s) - %s - %s" % (self.agentID, self.agentType, self.agentVersion, self.registered_at, self.registered_ip)

    create = staticmethod(create)
    _getPeers = staticmethod(_getPeers)
    getPeers = staticmethod(getPeers)
    getSuperPeers = staticmethod(getSuperPeers)


class AgentRSAKey(models.Model):
    mod = models.TextField()
    exp = models.TextField()