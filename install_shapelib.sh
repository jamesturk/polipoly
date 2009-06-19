#!/bin/sh

wget "http://dl.maptools.org/dl/shapelib/?file=shapelib-1.2.10.tar.gz&ACTION=Download" -O shapelib-1.2.10.tar.gz
wget http://ftp.intevation.de/users/bh/pyshapelib/pyshapelib-0.3.tar.gz
tar xf shapelib-1.2.10.tar.gz
tar -C shapelib-1.2.10 -xf pyshapelib-0.3.tar.gz
cd shapelib-1.2.10/pyshapelib-0.3
python setup.py build
python setup.py install
