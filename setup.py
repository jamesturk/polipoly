from distutils.core import setup
from polipoly import __version__,__license__

# don't worry about classifiers hack for Python 2.2, polipoly requires >= 2.4

setup(name="polipoly",
      version=__version__,
      py_modules=["polipoly"],
      description="Library for working with political boundary polygons.",
      author="James Turk",
      author_email = "james.p.turk@gmail.com",
      license=__license__,
      url="http://code.google.com/p/polipoly/",
      long_description="""polipoly is a library for working with political boundary polygons such as those obtained from census shapefiles.""",
      platforms=["any"],
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Scientific/Engineering :: GIS",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ]
      )

