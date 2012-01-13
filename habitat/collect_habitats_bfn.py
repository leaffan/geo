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
import urllib2

import lxml.html

from osgeo import ogr
from shapely.wkb import loads

from habitat import Habitat, HabitatType, Species
from habitat import retrieve_taxonomic_information

DEBUG = False

# defining constants
# prefix to site urls at www.bfn.de
URL_PREFIX = "http://www.bfn.de/4624.html?tx_n2gebiete_pi1[detail]=ffh&tx_n2gebiete_pi1[sitecode]="
# regular expression to retrieve sitecode and name from area webpage
NAME_REGEX = "\d{4}-\d{3}\s(.+)\s\(FFH-Gebiet(.+)?\)"
# regular expression to retrieve region type and size of a habitat
REGION_SIZE_REGEX = "(.+)\sRegion(.+)\sha"

SITECODE_FIELD = 'SITECODE'

NUTS_CODES = {
    "Baden-Württemberg":"DE1",
    "Bayern":"DE2",
    "Berlin":"DE3",
    "Brandenburg":"DE4",
    "Bremen":"DE5",
    "Hamburg":"DE6",
    "Hessen":"DE7",
    "Mecklenburg-Vorpommern":"DE8",
    "Niedersachsen":"DE9",
    "Nordrhein-Westfalen":"DEA",
    "Rheinland-Pfalz":"DEB",
    "Saarland":"DEC",
    "Sachsen":"DED",
    "Sachsen-Anhalt":"DEE",
    "Schleswig-Holstein":"DEF",
    "Thüringen":"DEG",
    "Ausschließliche Wirtschaftszone":"DEZ",
}

BIOGREOGRAPHICAL_REGIONS = {
    "alpine" : 1,
    "atlantische" : 2,
    "kontinentale" : 3,
}

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

    ii = 0

    src_ft = src_ly.GetNextFeature()
    #src_ft = src_ly.GetFeature(100)
    while src_ft is not None:
        # retrieving sitecode
        sitecode = src_ft.GetField(sitecode_index)

        # checking if area with given sitecode already exists in database
        if habitats.has_key(sitecode):
            habitat = habitats[sitecode]
            print "Habitat area '%s' (%s) already in database..." % (habitat.name, sitecode)
            # unifying habitat geometry with the current feature's geometry
            habitat.geometry = habitat.geometry.union(loads(src_ft.GetGeometryRef().ExportToWkb()))
            src_ft = src_ly.GetNextFeature()
            continue

        # retrieving habitat data from characteristics at www.bfn.de
        # retrieving contents of html page
        hab_url = ''.join((URL_PREFIX, sitecode))
        hab_conn = urllib2.urlopen(hab_url)
        hab_doc = lxml.html.parse(hab_conn).getroot()
        contents = hab_doc.get_element_by_id('content')

        # finding name data (incl. sitecode, name, ...)
        hab_name_data = contents.find('*/h2').text_content().encode('utf-8')
        match = re.search(NAME_REGEX, hab_name_data)

        if match is not None:
            hab_name = match.group(1)

            # creating new habitat
            hab = Habitat(sitecode, hab_name)
            # find further habitat data
            other_data = contents.findall('div/p')

            # containing administrative area
            fed_state = other_data[0].text_content().encode('utf-8')
            try:
                nuts_code = NUTS_CODES[fed_state]
            except:
                nuts_code = ''

            # biogreophical region and size
            region = other_data[1].text_content().encode('utf-8')
            # separating region and size
            region_size_match = re.search(REGION_SIZE_REGEX, region)
            if region_size_match is not None:
                try:
                    region = BIOGREOGRAPHICAL_REGIONS[region_size_match.group(1)]
                except:
                    region = ''
                size = float(region_size_match.group(2).replace(".", "").replace(',', '.'))

            # description of habitat
            description = other_data[-2].text_content().encode('utf-8')

            # adding found information to habitat object
            hab.set_description(description)
            hab.set_administrative_area(nuts_code)
            hab.set_region(region)
            hab.set_size(size)
            hab.set_url(hab_url)
            
            hab.set_geometry(src_ft)
            
            # retrieving available habitat types and species
            for link in contents.iterlinks():
                if link[0].find_class('linkint'):
                    key = link[0].text_content().encode('utf-8')
                    if not len(key) == 4:
                        sp = Species(key)
                        retrieve_taxonomic_information(sp)  
                        hab.species.append(sp)
                    else:
                        hab.habitat_types.append(habitat_types[key])

            # adding found habitat types to habitat object
            habitats[sitecode] = hab
            pickle.dump(habitats, open(hab_area_pkl_tgt, 'wb'))


        print ii
        hab.print_habitat_data()
        print "==============================================================="

        ii += 1

        #import sys
        if ii > 10 and DEBUG:
            src_ft = None
        else:
           src_ft = src_ly.GetNextFeature()

    # saving found habitat data in pickle file
    print "Dumping habitat area data to %s..." % hab_area_pkl_tgt,
    pickle.dump(habitats, open(hab_area_pkl_tgt, 'wb'))
    print "Done"
