from abc import ABCMeta, abstractmethod

class GeoIpInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def getIPLocation(self, address):
        return NotImplemented


class GeoBytesGeoIp:

    def getIPLocation(self, address):
        location = {}
        location['lat'] = '20'
        location['lng'] = '12'
        location['city'] = 'Lisboa'
        location['country'] = 'Portugal'