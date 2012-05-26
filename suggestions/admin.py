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

from suggestions.models import *
from django.contrib import admin


class AggregationAdmin(admin.ModelAdmin):

    actions = ['accept_and_delete']

    def accept_and_delete(self, request, queryset):
        for aggregation in queryset:
            aggregation.accept_aggregation()


admin.site.register(WebsiteSuggestion)
admin.site.register(ServiceSuggestion)
admin.site.register(WebsiteUrlAggregation, AggregationAdmin)
admin.site.register(WebsiteLocationAggregation, AggregationAdmin)
admin.site.register(WebsiteAggregation, AggregationAdmin)
admin.site.register(ServiceNameAggregation, AggregationAdmin)
admin.site.register(ServiceHostAggregation, AggregationAdmin)
admin.site.register(ServiceIPAggregation, AggregationAdmin)
admin.site.register(ServicePortAggregation, AggregationAdmin)
admin.site.register(ServiceLocationAggregation, AggregationAdmin)
admin.site.register(ServiceAggregation, AggregationAdmin)
