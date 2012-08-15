#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Author: Adriano Monteiro Marques <adriano@umitproject.org>
## Author: Orcun Avsar <orc.avs[at]gmail.com>
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

"""Standalone script for pointing reserved IP ranges into Unknown location.
"""

import sys
from os.path import dirname, abspath

AGG_DIR =  dirname(dirname(dirname(abspath(__file__))))
sys.path.insert(0, AGG_DIR)

from django.core.management import setup_environ
import settings
setup_environ(settings)

from geoip.models import Location
from geoip.models import IPRange


def main():
    # We assume 'Unknown' location is already created
    unknown_location = Location.objects.get(country_code='UN')

    # Update IP ranges whose location_id=0 (means a reserved or non-used IP)
    IPRange.objects.filter(location_id=0).update(location_id=unknown_location.id)


if __name__ == '__main__':
    main()
