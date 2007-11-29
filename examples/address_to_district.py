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
from polipoly import AddressToDistrictService

GMAPS_API_KEY = 'define-me'
PATH_TO_CDFILES = 

# run as a module
if __name__ == '__main__':

    # get address field and output type
    fields = cgi.FieldStorage()
    addr = fields.getvalue('address')
    output = fields.getvalue('output')

    # plaintext error if no address is provided
    if addr is None:
        print 'Content-type: text/plain\n'
        print 'error: must provide address parameter'
    else:
        # create service and find out districts
        service = AddressToDistrictService(GMAPS_API_KEY, PATH_TO_CDFILES)
        lat, lng, districts = service.address_to_district(addr)       
        
        # JSON output (default)
        if output is None or output == 'json':
            print 'Content-type: application/json\n'
            dist_str = ','.join(['{"state":"%s", "district":"%s"}' % dist 
                                    for dist in districts])
            print '''{"address":"%s", "latitude":"%s", "longitude":"%s",
"districts": [ %s ] }''' % (addr, lat, lng, dist_str)

        # XML output
        elif output == 'xml':
            print 'Content-type: text/xml\n'
            dist_str = '\n'.join(['  <district state="%s">%s</district>' % dist 
                                    for dist in districts])
            print '''<results>
  <address>%s</address>
  <latitude>%s</latitude>
  <longitude>%s</longitude>
  <districts>
  %s
  </districts>
</results>''' %  (addr, lat, lng, dist_str)

        else:
            print 'Content-type: text/plain\n'
            print 'error: invalid output parameter specified'

