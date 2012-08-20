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

import csv
import decimal
import cStringIO, StringIO
from collections import deque

from django.db import models


class FIFOList(deque):
    """A FIFO list that pops the oldest for the newest when size is reached.
    """

    def __init__(self, size):
        deque.__init__(self)
        self.size = size
        
    def full_append(self, item):
        deque.append(self, item)
        # full, pop the oldest item, left most item
        self.popleft()
        
    def append(self, item):
        deque.append(self, item)
        # max size reached, append becomes full_append
        if len(self) == self.size:
            self.append = self.full_append
    
    def get(self):
        """returns a list of size items (newest items)"""
        return list(self)


class ListField(models.TextField):
    description = "A ListField is actually a TextField with comma-separated " \
                  "values. The value types can be string, integer and decimal."
    
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        kwargs['default'] = ""
        
        self.db_converter = kwargs.get('db_type', str)
        if 'db_type' in kwargs:
            del(kwargs['db_type'])
        
        self.py_converter = kwargs.get('py_type', str)
        if 'py_type' in kwargs:
            del(kwargs['py_type'])

        self.max_size = kwargs.get('max_size', None)
        if 'max_size' in kwargs:
            del(kwargs['max_size'])


        super(ListField, self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        if isinstance(value, list) or isinstance(value, FIFOList):
            return value

        if value in ['', None]:
            return []

        # Field returns a FIFOList (which is a deque) when size is limited
        # FIFOList tweaks performance at push-fronts and pop-backs
        if self.max_size:
            lst = FIFOList(self.max_size)
        else: # Otherwise, returns a default Python list
            lst = []

        valueio = StringIO.StringIO(value)

        for v in csv.reader(valueio, delimiter=','):
            lst.append(self.py_converter(v[0]))

        return lst

    def get_prep_value(self, value):
        valueio = cStringIO.StringIO()
        writer = csv.writer(valueio, delimiter=',')
        [writer.writerow([self.db_converter(v)]) for v in value]
        return valueio.getvalue()


class CassandraKeyField(models.CharField):
    """This field is a CharField with predefined max_length=128.
    """

    def __init__(self):
        kwargs = {'max_length': 128}
        super(CassandraKeyField, self).__init__(**kwargs)

