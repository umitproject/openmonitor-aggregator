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


import datetime
import logging

from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from gui.decorators import staff_member_required
from agents.forms import BanAgentForm
from agents.models import Agent, BAN_FLAGS


@staff_member_required
def ban_agent(request):
    form = BanAgentForm(request.POST)
    msg = ""
    error = False
    if form.is_valid():
        agent = get_object_or_404(Agent, pk=form.cleaned_data['agent'])
        try:
            agent.ban(BAN_FLAGS.get(form.cleaned_data['flag']))
        except Exception, err:
            error = str(err)
            msg = "Failed to ban agent %s with flag %s" % \
                                        (form.cleaned_data['agent'],
                                         form.cleaned_data['flag'])
        else:
            msg = "Banned agent %s with flag %s successfuly!" % \
                                        (form.cleaned_data['agent'],
                                         form.cleaned_data['flag'])
        
    form = BanAgentForm()
    return render_to_response('agents/ban_agent.html', locals())
    



