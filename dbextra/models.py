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
from django.core.cache import cache


USER_KEY = "user_%s"

class UserModel(models.Model):
    user_id = models.IntegerField(null=True, blank=True, default=None)
    
    class Meta:
        abstract = True
    
    def get_user(self):
        user = cache.get(USER_KEY % self.user_id, False)
        if not user and self.user_id is not None:
            user = models.User.objects.get(id=self.user_id)
            cache.set(USER_KEY % self.user_id, user)
        return user
    
    def set_user(self, user):
        self.user_id = user.id
        
        # Just cache it so that next time we ask we don't go after datastore
        cache.set(USER_KEY % self.user_id, user)
    
    user = property(get_user, set_user)
