from packages import pygeoip
import os, splittedDat

class GeoIp:
    
    def getIPLocation(self, address):
        # get path of data file that contains the locations
        basepath = os.path.dirname(__file__)
        path = os.path.join(basepath, 'dat/GeoLiteCity.dat')

        # get data handler to read splitted files
        datahandler = splittedDat.splitedDat(path)

        #service = pygeoip.GeoIP(path)
        service = pygeoip.GeoIP(filename=path, filehandle=datahandler)
        location = service.record_by_addr(address)

        # remove unused fields
        result = {}
        result['city'] = location['city']
        result['country_name'] = location['country_name']
        result['country_code'] = location['country_code']
        result['latitude'] = location['latitude']
        result['longitude'] = location['longitude']

        return result
