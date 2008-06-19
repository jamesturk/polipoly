"""Python library for working with political boundaries

Political boundaries are defined by one or more polygons and obtained
from census.gov shapefiles.  Census boundary shapefiles are available at
http://www.census.gov/geo/www/cob/bdy_files.html.

At the moment this library has only been used with State and Congressional
District boundaries.
"""

__author__ = "James Turk (james.p.turk@gmail.com)"
__version__ = "0.1.5"
__copyright__ = "Copyright (c) 2007-2008 Sunlight Labs"
__license__ = "BSD"

import urllib
from shapelib import ShapeFile
from dbflib import DBFFile

### General Utilities ###

# internally used helper function
def left_of_edge(point, ep1, ep2):
    """Determine if point is left of infinite line touching ep1 and ep2"""
    return ((ep1[0]-point[0])*(ep2[1]-point[1]) -
            (ep2[0]-point[0])*(ep1[1]-point[1])) < 0


class Polygon(object):
    ''' Simple polygon class used for point containment testing and conversion

    Allows for testing if a polygon contains a point as well as conversion
    to various portable representations '''

    def __init__(self, vertices):
        self.vertices = vertices

    def contains(self, point):
        ''' Determine if point lies within the polygon. '''

        # initially winds is 0
        winds = 0

        # iterate over edges
        for i in xrange(len(self.vertices)-1):

            # add wind if edge crosses point going up and point is to left
            if (self.vertices[i][1] < point[1] < self.vertices[i+1][1] and
                left_of_edge(point, self.vertices[i], self.vertices[i+1])):
                winds += 1
            # end wind if edge crosses point going down and point is to right
            elif (self.vertices[i][1] > point[1] > self.vertices[i+1][1] and
                not left_of_edge(point, self.vertices[i], self.vertices[i+1])):
                winds -= 1

        # point is contained if net winds is not zero
        return winds != 0

    def to_kml(self):
        ''' get KML polygon representation '''

        coordstr = ' '.join("%.15f,%.15f" % v for v in self.vertices)

        return '''<Polygon><outerBoundaryIs><LinearRing>
<coordinates>%s</coordinates>
</LinearRing></outerBoundaryIs></Polygon>''' % coordstr

### Exceptions ###

class GeocodingError(Exception):
    """Custom exception which maps possible google geocoder error codes to
    human readable strings.

    See http://www.google.com/apis/maps/documentation/reference.html#GGeoStatusCode
    """

    STATUS_CODES = {500: 'Unknown Geocoding Server Error',
                    601: 'Empty Address',
                    602: 'Unknown Address',
                    603: 'Prohibited Address',
                    610: 'Bad API Key',
                    620: 'Too Many Requests'}

    def __init__(self, code, extra=None):
        Exception.__init__(self)
        self.code = int(code)
        self.extra = extra

    def __str__(self):
        desc = 'GeocodingError: %d - %s' % (self.code,
                                            self.STATUS_CODES[self.code])
        if self.extra:
            desc += ' (%s)' % self.extra


class ShapefileError(Exception):
    """ Exception for problems with census shapefiles."""
    def __init__(self, message):
        Exception.__init__(self, message)

    def __str__(self):
        return 'ShapefileError: %s' % (self.message)


### Census Shapefiles ###

# Mapping of FIPS codes to Postal Abbreviations
# obtained from http://www.itl.nist.gov/fipspubs/fip5-2.htm
FIPS_TO_STATE = {
    '01':'AL', '02':'AK', '04':'AZ', '05':'AR', '06':'CA', '08':'CO', '09':'CT',
    '10':'DE', '11':'DC', '12':'FL', '13':'GA', '15':'HI', '16':'ID', '17':'IL',
    '18':'IN', '19':'IA', '20':'KS', '21':'KY', '22':'LA', '23':'ME', '24':'MD',
    '25':'MA', '26':'MI', '27':'MN', '28':'MS', '29':'MO', '30':'MT', '31':'NE',
    '32':'NV', '33':'NH', '34':'NJ', '35':'NM', '36':'NY', '37':'NC', '38':'ND',
    '39':'OH', '40':'OK', '41':'OR', '42':'PA', '44':'RI', '45':'SC', '46':'SD',
    '47':'TN', '48':'TX', '49':'UT', '50':'VT', '51':'VA', '53':'WA', '54':'WV',
    '55':'WI', '56':'WY', '72':'PR' }



class Entity(object):
    """ A named list of polygons associated with a political boundary.

        eg. a state, congressional district, or school district"""

    def __init__(self, name, entity, vertices, extents):
        self.name = name
        self.entity = entity
        self.polygons = [Polygon(vlist) for vlist in vertices]
        self.extents = extents

    @staticmethod
    def from_shapefile(obj, rec):
        """ Factory function that creates a Entity (or derived class) from
            a census.gov shapefile. """

        # by using the LSAD determine if a subclass is defined for this entity
        lsad_mapping = {
            ('01'): State,
            ('C1', 'C2', 'C3', 'C4'): CongressDistrict
        }
        for lsads, cls in lsad_mapping.iteritems():
            if rec['LSAD'] in lsads:
                return cls.from_shapefile(obj, rec)

        # if there is no mapping for the LSAD just construct a Entity
        return Entity('', rec['LSAD_TRANS'], obj.vertices(), obj.extents())

    def in_rect(self, point):
        """ Check if a point lies within the bounding extents of the entity """
        return self.extents[0][0] < point[0] < self.extents[1][0] and \
                self.extents[0][1] < point[1] < self.extents[1][1]

    def contains(self, point):
        """ Check if a point lies within any of the entities polygons """
        if self.in_rect(point):
            for poly in self.polygons:
                if poly.contains(point):
                    return True
        return False

    def to_kml(self):
        """ Return a KML Placemark representing the entity """
        return """<Placemark><name>%s</name>
<MultiGeometry>%s</MultiGeometry>
</Placemark>""" % (self.name, ''.join(poly.to_kml() for poly in self.polygons))

class CongressDistrict(Entity):
    """ Entity with state and district properties. """

    def __init__(self, entity, vertices, extents, state, district):
        Entity.__init__(self, '%s-%s' % (state, district),
                                entity, vertices, extents)
        self.state = state
        self.district = district

    @staticmethod
    def from_shapefile(obj, rec):
        """ Construct a CongressDistrict from a census.gov shapefile """
        return CongressDistrict(rec['LSAD_TRANS'], obj.vertices(),
                                obj.extents(), FIPS_TO_STATE[rec['STATE']],
                                rec['CD'])

class State(Entity):
    """ Entity for states, adds a state property """

    def __init__(self, vertices, extents, state):
        Entity.__init__(self, 'State', state, vertices, extents)
        self.state = state

    @staticmethod
    def from_shapefile(obj, rec):
        """ Construct a State from a census.gov shapefile """
        return State(obj.vertices(), obj.extents(), rec['NAME'])

def read_census_shapefile(filename):
    """Read census shapefile and return list of entity-derived objects.

    Given the base name of a census .shp/.dbf file returns a list of all
    Entity-derived objects described by the the file.
    """

    try:
        shp = ShapeFile(filename)
    except IOError:
        raise ShapefileError('Could not open %s.shp' % filename)

    try:
        dbf = DBFFile(filename)
    except IOError:
        raise ShapefileError('Could not open %s.dbf' % filename)

    shape_count = shp.info()[0]

    # shape_count should always equal dbf.record_count()
    if shape_count != dbf.record_count():
        raise ShapefileError('SHP/DBF record count mismatch (SHP=%d, DBF=%d)' %
                                (shape_count, dbf.record_count()))

    # generator version
    #for i in xrange(shp.info()[0]):
    #    yield Entity.fromShapefile(shp.read_object(i), dbf.read_record(i))

    # shp.info()[0] is the number of objects
    return [Entity.from_shapefile(shp.read_object(i), dbf.read_record(i))
            for i in xrange(shape_count)]


### Geocoding ###

class AddressToDistrictService(object):
    """Abstract base class for service which maps addresses to districts using
    the census data and a geocoder."""

    GEOCODER_GMAPS = 1
    GEOCODER_US = 2

    def __init__(self, census_file, geocoder=GEOCODER_US, apikey=None):
        """AddressToDistrictService constructor

        Initialize given a path to a census.gov all congressional districts
        (cd99) dataset.

        The cd99_110 dataset is available from:
            http://www.census.gov/geo/www/cob/cd110.html
        """
        if geocoder == self.GEOCODER_GMAPS and not apikey:
            raise GeocodingError(610)   # bad api key

        self.boundaries = read_census_shapefile(census_file)
        self.geocoder = geocoder
        self.apikey = apikey

    def _google_geocode(self, address):
        """Convert an address into a latitude/longitude via google maps"""

        url = 'http://maps.google.com/maps/geo?output=csv&q=%s&key=%s' % \
         (urllib.quote(address), self.apikey)
        # returns status,level-of-detail,lat,long
        status, _, lat, lng = urllib.urlopen(url).read().split(',')

        # 200 - OK
        if status == '200':
            return lat, lng
        else:
            raise GeocodingError(status)

    def _geocoderus_geocode(self, address):
        """Convert an address into a latitude/longitude via geocoder.us"""

        if not address:
            raise GeocodingError(601)   # empty address

        url = 'http://rpc.geocoder.us/service/csv?address=%s' % \
              urllib.quote(address)
        data = urllib.urlopen(url).readline()   # only get first line for now

        # returns lat,long,street,city,state,zip or #: errmsg
        if data.startswith('2:'):
            raise GeocodingError(602)   # address not found

        try:
            lat, lng, _, _, _, _ = data.split(',')
            return lat, lng
        except ValueError:
            raise GeocodingError(500, data) # unmapped error

    def lat_long_to_district(self, lat, lng):
        """ Obtain the district containing a given latitude and longitude."""
        flat, flng = float(lat), -abs(float(lng))
        districts = []
        for cb in self.boundaries:
            if cb.contains((flng,flat)):
                if cb.district == '98':
                    cb.district = '00'
                elif cb.district[0] == '0':
                    cb.district = cb.district[1]
                districts.append((cb.state, cb.district))
        return lat, lng, districts

    def address_to_district(self, address):
        """Given an address returns the congressional district it lies within.

        This function works by geocoding the address and then finding the point
        that the returned lat/long returned lie within.
        """
        if self.geocoder == self.GEOCODER_GMAPS:
            lat, lng = self._google_geocode(address)
        elif self.geocoder == self.GEOCODER_US:
            lat, lng = self._geocoderus_geocode(address)

        return self.lat_long_to_district(lat, lng)
