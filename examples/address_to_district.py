#!/usr/bin/env python

''' Implementation of a webservice for an address to district webservice.

This is the code that http://api.sunlightlabs.com/places.getDistrictFromAddress
uses.

Be sure to set GMAPS_API_KEY and PATH_TO_CDFILES appropriately:
    GMAPS_API_KEY: Google Maps key (http://www.google.com/apis/maps/signup.html)
    PATH_TO_CDFILES: copy of cd99 (http://www.census.gov/geo/www/cob/cd110.html)

The CGI script takes two parameters:
    addr -- address string in any format the google geocoder can handle
    output -- optional parameter specifying formatting ('xml' or default 'json')
'''

import cgi
import re
from polipoly import AddressToDistrictService, GeocodingError

GMAPS_API_KEY = 'define-me'
PATH_TO_CDFILES = 'cd99_110'

class ApiException(Exception):

    # these codes are in the 300s to fit the sunlight API
    STATUS_CODES = {
        300: 'Google returned a server error when attempting to geocode',
        301: 'Empty address string',
        302: 'Unknown address',
        303: 'Prohibited address',
        304: 'Unknown geocoding error',
        305: 'Address refers to a PO Box',
        306: 'Address does not fall within a congressional district',
        320: 'Too many requests to geocoding service'}

    def __init__(self, code):
        self.code = code
       
    def __str__(self):
        return '%d: %s' % (self.code, self.STATUS_CODES[self.code])

def main():
    # get address field and output type
    fields = cgi.FieldStorage()
    addr = fields.getvalue('address') or ''
    output = fields.getvalue('output')
    
    # discard blank addresses as error 301
    if re.match('^\s*$', addr):
        raise ApiException(301)
    
    # discard PO Box addresses as error 305
    pobox = re.compile('[Pp]\.?[Oo]\.?\s*(?:box|Box|BOX)')
    if pobox.search(addr):
        raise ApiException(305)

    # create service and get a district
    service = AddressToDistrictService(GMAPS_API_KEY, PATH_TO_CDFILES)
    try:
        lat, lng, districts = service.address_to_district(addr)
    except GeocodingError, ge:
        # convert GeocodingError to API error code (300-303 and 320)
        err_dict = {500: 300, 601: 301, 602: 302, 603: 303, 620: 320}
        raise ApiException(err_dict.get(ge.code,304))
    
    # 306: address did not fall within congressional district
    if len(districts) == 0:
        raise ApiException(306)

    # XML output
    if output == 'xml':
        dist_str = '\n'.join(['  <district state="%s">%s</district>' % dist 
                              for dist in districts])
        print 'Content-type: text/xml\n'
        print '''<results>
<address>%s</address>
<latitude>%s</latitude>
<longitude>%s</longitude>
<districts>
%s
</districts>
</results>''' % (addr, lat, lng, dist_str)
    
    # JSON output (default)
    else:
        dist_str = ','.join(['{"state":"%s", "district":"%s"}' % dist 
                                for dist in districts])
        print 'Content-type: application/json\n'
        print '''{"address":"%s", "latitude":"%s", "longitude":"%s",
"districts": [ %s ] }''' % (addr, lat, lng, dist_str)


if __name__ == '__main__':
    try:
        main()
    except ApiException,e:
        print 'Content-type: text/plain\n'
        print e
