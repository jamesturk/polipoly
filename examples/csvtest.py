#!/usr/bin/env python

''' Example of a mass lookup using the AddressToDistrictService

Be sure to set GMAPS_API_KEY and PATH_TO_CDFILES appropriately:
    GMAPS_API_KEY: Google Maps key (http://www.google.com/apis/maps/signup.html)
    PATH_TO_CDFILES: copy of cd99 (http://www.census.gov/geo/www/cob/cd110.html)
'''


import csv
from polipoly import AddressToDistrictService

PATH_TO_CDFILES = 'congdist/cd99_110'
GEOCODER = AddressToDistrictService.GEOCODER_US
GMAPS_API_KEY = None

# This sample data was collected from Project Vote Smart

SAMPLE_DATA = ['representative,state,district,address',
'Josiah Bonner,AL,01,"1141 Montlimar Drive, Suite 3010, Mobile, AL 36609"',
'Terry Everett,AL,02,"101 North Main Street, Opp, AL 36467"',
'Michael Rogers,AL,03,"7550 Halcyon Summit Drive, Montgomery, AL 36117"',
'Robert Aderholt,AL,04,"1710 Alabama Avenue, Jasper, AL 35501"',
'Robert Cramer,AL,05,"1011 George Wallace Boulevard, Tuscumbia, AL 35674"',
'Spencer Bachus,AL,06,"1900 International Park Drive, Suite 107, Birmingham, AL 35243"',
'Artur Davis,AL,07,"102 East Washington Street, Suite F, Demopolis, AL 36732"',
'Rick Renzi,AZ,01,"501 North Florence Street, Suite 102, Casa Grande, AZ 85222"',
'Trent Franks,AZ,02,"7121 West Bell Road, Suite 200, Glendale, AZ 85308"',
'John Shadegg,AZ,03,"301 East Bethany Home Road, Suite C-178, Phoenix, AZ 85012"',
'Ed Pastor,AZ,04,"411 North Central Avenue, Suite 150, Phoenix, AZ 85004"',
'Harry Mitchell,AZ,05,"7201 East Camelback Road, Suite 335, Scottsdale, AZ 85251"',
'Jeff Flake,AZ,06,"1640 South Stapley, Suite 215, Mesa, AZ 85204"',
'Raul Grijalva,AZ,07,"1455 South Fourth Avenue, Suite 4, Yuma, AZ 85364"',
'Gabrielle Giffords,AZ,08,"1661 North Swan, Suite 112, Tucson, AZ 85712"']

service = AddressToDistrictService(PATH_TO_CDFILES, GEOCODER, GMAPS_API_KEY)

records = csv.DictReader(SAMPLE_DATA)
for rec in records:
    lat, lng, dists = service.address_to_district(rec['address'])
    print '%s\tcorrect: %s-%s\tfound: %s-%s' % (rec['representative'],
        rec['state'], rec['district'], dists[0][0], dists[0][1])
