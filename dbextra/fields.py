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

from django.db import models

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
        
        super(ListField, self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        if isinstance(value, list):
            return value

        if value in ['', None]:
            return []

        valueio = StringIO.StringIO(value)

        return [self.py_converter(v[0]) for v in csv.reader(valueio, delimiter=',')]

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

