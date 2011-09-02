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

from Crypto.PublicKey import RSA
import os

class RSACrypto:

    def __init__(self):
        self.keyPair = None

    def generateKeyPair(self):
        self.keyPair = RSA.generate(1024, os.urandom)

    def getNewRSAKey(self):
        # generate new RSA key
        self.generateKeyPair()
        # export keys
        key = {}
        key['public'] = RSAKey(self.keyPair.n, self.keyPair.e)
        key['private'] = RSAKey(self.keyPair.n, self.keyPair.d)
        return key


class RSAKey:

    def __init__(self, mod, exp):
        self.mod = mod
        self.exp = exp
  