from dbindexer.api import register_index
from dbindexer.lookups import StandardLookup

from icm_tests.models import WebsiteTestsCountryAggregation
from icm_tests.models import WebsiteTestsRegionAggregation
from icm_tests.models import WebsiteTestsCityAggregation
from icm_tests.models import ServiceTestsCountryAggregation
from icm_tests.models import ServiceTestsRegionAggregation
from icm_tests.models import ServiceTestsCityAggregation


register_index(WebsiteTestsCountryAggregation,
               {'location__country_name':StandardLookup()})

register_index(WebsiteTestsRegionAggregation,
               {'location__state_region':StandardLookup()})

register_index(WebsiteTestsCityAggregation,
               {'location__city':StandardLookup()})

register_index(ServiceTestsCountryAggregation,
               {'location__country_name':StandardLookup()})

register_index(ServiceTestsRegionAggregation,
               {'location__state_region':StandardLookup()})

register_index(ServiceTestsCityAggregation,
               {'location__city':StandardLookup()})
