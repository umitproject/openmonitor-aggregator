#!/usr/bin/python
#-*- coding: utf-8 -*-

class DBRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'geoip':
            return 'geoip'
        return None
      
    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'geoip':
            return 'geoip'
        return None
      
    def allow_syncdb(self, db, model):
        if db == 'geoip':
            return model._meta.app_label == 'geoip'
        else: #sync all other apps into default database
            return True