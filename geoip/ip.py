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
import re

from types import StringTypes, ListType, IntType, GeneratorType


MAX_IP_INT = 4294967295 # This is equivalent to all 32 bits set to 1

NET_RANGE_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)\.(\d+)/(\d+)")
IP_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)\.(\d+)")

def convert_mask(mask):
    """Receives a mask in /# format (# is any number in range [1-31]) and
    returns an integer representing the mask
    """
    int_mask = 1
    for i in xrange(mask-1):
        int_mask = (int_mask << 1) | 1
    int_mask <<= (32 - mask)
    
    return int_mask

def printf_bits(num):
    """Receives a 32 bits integer and returns a string with the binary
    representation of it.
    """
    if num <= MAX_IP_INT:
        bin_rep = []
        mask = (1 << 31)
        for i in xrange(32):
            bit = num & mask
            if bit > 0:
                bit = 1
                
            bin_rep.append(bit)
            mask >>= 1
        
        return ("%d%d%d%d%d%d%d%d %d%d%d%d%d%d%d%d " \
                "%d%d%d%d%d%d%d%d %d%d%d%d%d%d%d%d") % tuple(bin_rep)
    else:
        raise ValueError("Can't print values bigger than 4294967295")

def convert_ip(ip):
    """Receives the IP as a list of ints:
    [192, 168, 0, 0] representing "192.168.0.0"
    
    Or, receives as a string, and converts it for internal use:
    "192.168.0.0" to [192, 168, 0, 0] and then uses it
    """
    ip = sanitize_ip(ip)
    int_ip = 0
    int_ip |= (ip[0] << 24)
    int_ip |= (ip[1] << 16)
    int_ip |= (ip[2] << 8)
    int_ip |= ip[3]
    
    return int_ip

def convert_int_ip(i_ip):
    """Received the IP as an integer, and returns string,
    representing the ip in a human readable format.
    """
    
    ip = []
    ip.append(str((i_ip >> 24) & 255))
    ip.append(str((i_ip >> 16) & 255))
    ip.append(str((i_ip >> 8) & 255))
    ip.append(str(i_ip & 255))
    
    return ".".join(ip)

def sanitize_ip(ip):
    _ip = []
    
    if type(ip) in StringTypes:
        _ip = [int(i) for i in IP_RE.findall(ip)[0]]
    elif type(ip) is ListType:
        for i in ip:
            assert type(i) is IntType, "IP Provided in wrong format; Should "\
                                 "be a list of integers, but received %s" % ip
        _ip = ip
    else:
        raise TypeError("IP Provided in wrong format; Should be a list of "\
                        "integers or a string, but received %s" % ip)
    
    return _ip
