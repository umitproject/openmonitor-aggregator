#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Author: Adriano Monteiro Marques <adriano@umitproject.org>
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

from agents.models import Agent
from agents.CryptoLib import crypto, aggregatorKey, aes_decrypt


class message_handler(object):
    def __init__(self, message_type, response_type=None):
        """This decorator will deal with decrypting and encrypting the request
        and the response for the api requests received, using the provided key,
        aes_key or figuring the aes_key when agentID is present in the request.
        
        response_type isn't always necessary.
        """
        self.message_type = message_type
        self.response_type = response_type
    
    def __call__(self, method):
        def new_method(handler, request, *args, **kwargs):
            aes_key = None
            agent = None
            
            key = request.POST.get('key', None)
            message = request.POST.get('msg', None)
            agent_id = request.POST.get('agentID', None)
            
            logging.debug("Agent ID: %s" % agent_id)
            
            # If key is not provided, then agent_id must be present.
            if key is None:
                assert agent_id
                
                agent = Agent.get_agent(agent_id)
                aes_key = agent.AESKey
            else:
                aes_key = crypto.decodeRSAPrivateKey(key, aggregatorKey)
            
            
            aes_key, msg_obj = aes_decrypt(message,
                                           self.message_type,
                                           aes_key=aes_key)
            
            # Processing the request
            #try:
            response = method(handler,
                                  request,
                                  msg_obj,
                                  aes_key,
                                  agent,
                                  *args, **kwargs)
            #except Exception, e:
            #    logging.critical("Failed to execute api request: %s" % e)
            #    raise e
            
            # Need to encrypt and return the response now
            return crypto.encodeAES(response, aes_key)
        
        return new_method


