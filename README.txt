NOTE: polipoly is deprecated and no longer maintained.  Due to the wide
availability of better tools like GEOS <http://trac.osgeo.org/geos/> and
GeoDjango <http://geodjango.org> it is no longer in use nor will it see
any further development.

~~~~~~~~~~
old readme
~~~~~~~~~~

polipoly - Python library for dealing with political boundaries.  Enables 
    programatic conversion of latitudes/longitudes to political districts.

http://polipoly.googlecode.com/

polipoly is a project of Sunlight Labs (C) 2007-2008 see LICENSE.txt for details

Files Included
==============
polipoly.py - The polipoly library
examples/address_to_district.py - Implementation of a webservice for an address
     to district webservice. This is based on the code that runs
     http://api.sunlightlabs.com/places.getDistrictFromAddress
examples/csvtest.py - Example of batch processing addresses from a csv file.


Requirements
============

python >= 2.4
pyShapeLib 0.3 (see http://code.google.com/p/polipoly/wiki/ShapeLib)


Installation
============
To install run

    python setup.py install

which will install the bindings into python's site-packages directory.

Documentation
=============
For documentation view the source itself and the examples included in the 
examples/ subdirectory.

