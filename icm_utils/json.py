from django.utils import simplejson
from decimal import Decimal

class ICMJSONEncoder(simplejson.JSONEncoder):
    """JSON encoder which understands decimals."""

    def default(self, obj):
        '''Convert object to JSON encodable type.'''
        if isinstance(obj, Decimal):
            return "%d" % obj
        return simplejson.JSONEncoder.default(self, obj)
