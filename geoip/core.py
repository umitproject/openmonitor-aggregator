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

import os

from packages import pygeoip
from geoip import splittedDat 

class GeoIp:
    
    def getIPLocation(self, address):
        # get path of data file that contains the locations
        basepath = os.path.dirname(__file__)
        path = os.path.join(basepath, 'dat/GeoLiteCity.dat')

        # get data handler to read splitted files
        datahandler = splittedDat.splitedDat(path)

        #service = pygeoip.GeoIP(path)
        service = pygeoip.GeoIP(filename=path, filehandle=datahandler)
        location = service.record_by_addr(address)

        # remove unused fields
        result = {}
        if 'city' in location:
            result['city'] = location['city']
        else:
            result['city'] = ''
        result['country_name'] = location['country_name']
        result['country_code'] = location['country_code']
        result['latitude'] = location['latitude']
        result['longitude'] = location['longitude']

        return result
