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

"""Report processing tasks.
"""

import datetime
import logging

from django.conf import settings
from djcelery import celery


@celery.task()
def save_report_task(user_report_id):
    """Grabs the received report and have it saved and processed by the
    DecisionSystem.
    """
    from reports.models import UserReport, REPORT_PERIOD
    from decision.decisionSystem import DecisionSystem

    logging.info("Processing user report %s" % user_report_id)
    user_report = UserReport.get(id=user_report_id)

    report = Report.objects.filter(
        test_id=user_report.test_id,
        agent_location_id=user_report.agent_location_id,
        created_at__gte=user_report.created_at-REPORT_PERIOD,
        created_at__lte=user_report.created_at+REPORT_PERIOD
    )

    if not report:
        logging.info("Report is brand new. Creating one.")
        report = Report()
        report.test_id = user_report.test_id
        report.time = user_report.time
        report.time_zone = user_report.time_zone
        report.response_time = user_report.response_time
        nodes = user_report.nodes
        report.nodes.append(nodes)
        report.target = user_report.target
        report.hops = user_report.hops
        report.packet_size = user_report.packet_size
        trace = user_report.trace
        report.trace = user_report.trace
        report.agent_ip = user_report.agent_ip
        report.agent_location_id = user_report.agent_location_id
        report.agent_location_name = user_report.agent_location_name
        report.agent_country_name = user_report.agent_country_name
        report.agent_country_code = user_report.agent_country_code
        report.agent_state_region = user_report.agent_state_region
        report.agent_city = user_report.agent_city
        report.agent_zipcode = user_report.agent_zipcode
        report.agent_lat = user_report.agent_lat
        report.agent_lon = user_report.agent_lon
        report.target_location_id = user_report.target_location_id
        report.target_location_name = user_report.target_location_name
        report.target_country_name = user_report.target_country_name
        report.target_country_code = user_report.target_country_code
        report.target_state_region = user_report.target_state_region
        report.target_city = user_report.target_city
        report.target_zipcode = user_report.target_zipcode
        report.target_lat = user_report.target_lat
        report.target_lon = user_report.target_lon
        report.count = 1
        report.user_reports_ids.append(user_report.id)
        DecisionSystem.newReport(user_report)
    else:
        logging.info("Similar report exists. Updating.")
        report = report[0]
        report.count += 1
        report.user_reports_ids.append(user_report.id)
        if report.response_time and user_report.response_time:
            report.response_time = (report.response_time + user_report.response_time)/2
        elif not report.response_time and user_report.response_time:
            report.response_time = user_report.response_time
        DecisionSystem.updateReport(user_report)

    logging.info("Saving report.")
    report.save()
    
