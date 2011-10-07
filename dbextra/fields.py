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
import cStringIO

from django.db import models

class ListField(models.TextField):
    description = "A ListField is actually a TextField with comma-separated " \
                  "values. The value types can be string, integer and decimal."
    
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        kwargs['default'] = ""
        super(ListField, self).__init__(*args, **kwargs)
        self.converter = kwargs.get('field_type', str)
    
    def to_python(self, value):
        if isinstance(value, list):
            return list
        
        return [self.converter(v[0]) for v in csv.reader([value], delimiter=',')]

    def get_prep_value(self, value):
        valueio = cStringIO.StringIO()
        writer = csv.writer(valueio, delimiter=',')
        [writer.writerow([v]) for v in value]
        return valueio.getvalue()





