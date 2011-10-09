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

from django.core.cache import cache

from dbextra.cache_utils import get_cache_key

DEFAULT_CACHE_TIME=60

class cache_model_method(object):
    """This decorator should be used only on instance methods for models.Model
    classes, when you want to cache the return value of a method.
    """
    def __init__(self, prefix, cache_time=DEFAULT_CACHE_TIME, id_attribute='id'):
        self.prefix = prefix
        self.cache_time = cache_time
        self.id_attribute = id_attribute
    
    def __call__(self, method):
        def new_method(method_self, *args, **kwargs):
            cache_key = "%s_%s" % (self.prefix,
                                   get_cache_key(method,
                                                 getattr(method_self,
                                                         self.id_attribute)))
            result = cache.get(cache_key, False)
            if not result:
                result = method(method_self, *args, **kwargs)
                cache.set(cache_key, result, self.cache_time)
            return result
        
        new_method
