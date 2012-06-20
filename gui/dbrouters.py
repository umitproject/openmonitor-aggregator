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

from django.conf import settings


class GeoIPRouter(object):
    """A router that directs GeoIP queries to MySQL"""

    def db_for_read(self, model, **hints):
        "Point all read operations to GeoIP tables to MySQL database"
        if model._meta.app_label == 'geoip':
            return "mysql"
        
        return "default"
        

    def db_for_write(self, model, **hints):
        "Point all write operations to GeoIP tables to MySQL database"
        if model._meta.app_label == 'geoip':
            return "mysql"
        
        return "default"


    def allow_syncdb(self, db, model):
        "Explicitly put all models on all databases."
        print "SyncDB on database %s and model %s" % (db, model) 
        if db == 'mysql' and model._meta.app_label == 'geoip':
            # This will prevent syncdb from creating sentry tables on crowdspring databases.
            print "Sync IT!"
            return True
        elif db == 'mysql' and model._meta.app_label != 'geoip':
            print "Don't sync!"
            return False
        
        print "Sync IT!!"
        return True

