#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2011/12/22 12:30:36

u"""
... Put description here ...
"""

import os
import pickle
import re

from osgeo import ogr
from shapely.wkb import loads

from habitat import Habitat, HabitatType, Species


# defining constants
# prefix to site urls at www.bfn.de
URL_PREFIX = "http://www.bfn.de/4624.html?tx_n2gebiete_pi1[detail]=ffh&tx_n2gebiete_pi1[sitecode]="
# regular expression to retrieve sitecode and name from area webpage
NAME_REGEX = "\d{4}-\d{3}\s(.+)\s\(FFH-Gebiet.+\)"
# regular expression to retrieve region type and size of a habitat
REGION_SIZE_REGEX = "(.+)\sRegion(.+)\sha"

SITECODE_FIELD = 'SITECODE'



if __name__ == '__main__':

    # input data sources
    hab_area_shp_src = r"data\natura_2000_de.shp"
    hab_type_pkl_src = r"data\_habitat_types.pkl"
    # output data target
    hab_area_pkl_tgt = r"data\_natura_2000_de.pkl"

    # loading available habitat types
    habitat_types = pickle.load(open(hab_type_pkl_src))[1]

    # restoring available habitat data from pickle file
    if os.path.exists(hab_area_pkl_tgt):
        print "Restoring habitat area data from %s..." % (hab_area_pkl_tgt),
        habitats = pickle.load(open(hab_area_pkl_tgt))
        print "Done"
    else:
        # otherwise creating a new dictionary to contain habitat data
        habitats = dict()

    # opening source data shape file
    src_ds = ogr.Open(hab_area_shp_src)
    src_ly = src_ds.GetLayer(0)

    # finding index for field holding sitecode information
    sitecode_index = src_ly.GetLayerDefn().GetFieldIndex(SITECODE_FIELD)
    print "Sitecode information is contained in field with index %d ('%s')" \
        % (sitecode_index, SITECODE_FIELD)

    src_ft = src_ly.GetNextFeature()
    while src_ft is not None:
        # retrieving sitecode
        sitecode = src_ft.GetField(sitecode_index)
        print sitecode

        # checking if area with given sitecode already exists in database
        if habitats.has_key(sitecode):
            habitat = habitats[sitecode]
            print "Habitat area '%s' (%s) already in database..." % (habitat.name, sitecode)
            # trying to another subhabitat by using the current feature's geometry
            habitat.geometry = habitat.geometry.union(loads(src_ft.GetGeometryRef().ExportToWkb()))
            src_ft = src_ly.GetNextFeature()
            continue

        # retrieving habitat data from characteristics at www.bfn.de
        # retrieving contents of html page
        ffh_url = ''.join((URL_PREFIX, sitecode))
        ffh_conn = urllib2.urlopen(ffh_url)
        ffh_doc = lxml.html.parse(ffh_conn).getroot()
        contents = ffh_doc.get_element_by_id('content')

        src_ft = src_ly.GetNextFeature()
