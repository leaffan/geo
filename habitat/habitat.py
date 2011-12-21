#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: habitat.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2011/06/29 12:06:07

u"""
... Put description here ...
"""

from osgeo import ogr
from shapely.geometry import Point, LineString, Polygon
from shapely.wkb import loads
from shapely.ops import linemerge

class Species():
    def __init__(self, name):
        self.set_name(name)
        self.synonyms = set()
        self.translations = dict()
        self.associated_habitat_types = list()
        self.url = ''
    
    def set_name(self, name, synonym = False):
        if synonym:
            self.synonyms.add(synonym)
            return
        self.name = name
    
    def set_url(self, url):
        self.url = url
    
    def add_translation(self, lang, name):
        self.translations[lang.lower()] = name
    
    def set_associated_habitat_type(self, habitat_type):
        self.associated_habitat_types.append(habitat_type)
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return self.name == other.name
    
    def __ne__(self, other):
        return self.name != other.name

    def __cmp__(self, other):
        pass

    def __hash__(self):
        import hashlib
        return hash(self.name)

class HabitatType():
    def __init__(self, code, name = '', shortname = ''):
        self.code = code
        self.set_name(name, shortname)
        self.translations = dict()
        self.is_priority = False
        self.is_habitat_type = False
        self.is_major_group = False
        self.is_subgroup = False
        if len(code) == 4:
            self.is_habitat_type = True
        if len(code) == 2:
            self.is_subgroup = True
        if len(code) == 1:
            self.is_major_group = True
        self.characteristic_species = set()

    def set_name(self, name, shortname = ''):
        self.name = name
        if shortname:
            self.shortname = shortname
        else:
            self.shortname = ''

    def set_priority(self, priority = True):
        if priority and priority is True:
            self.is_priority = True
        else:
            self.is_priority = False
    
    def add_translation(self, lang, name):
        self.translations[lang.lower()] = name
    
    def add_characteristic_species(self, species):
        if not hasattr(self, 'characteristic_species'):
            self.characteristic_species = set()
        self.characteristic_species.add(species)
    
    def __str__(self):
        result = "%s: %s" % (self.code, self.name)
        if self.is_priority:
            result = "".join((result, '*'))
        if self.is_major_group:
            result = " ".join((result, '[major group]'))
        if self.is_subgroup:
            result = " ".join((result, '[sub group]'))
        return result

class Habitat():
    def __init__(self, sitecode, name = ''):
        self.sitecode = sitecode
        self.set_name(name)
        self.description = None
        self.region = None
        self.fed_state = None
        self.size = 0
        self.habitat_types = list()
        self.species = list()
        self.url = ''
        self.geometry = None

    def set_name(self, name):
        self.name = name

    def set_region(self, region):
        self.region = region
        
    def set_fed_state(self, fed_state):
        self.fed_state = fed_state

    def set_size(self, size):
        self.size = size

    def set_url(self, url):
        self.url = url

    def set_description(self, description):
        self.description = description

    def set_geometry(self, geometry_src):
        try:
            geometry_src = geometry_src.GetGeometryRef()
        except TypeError:
            "geometry source is no feature"
            pass
        try:
            self.geometry = loads(geometry_src.ExportToWkb())
            self.geometry_set = True
        except TypeError:
            "geometry source is no geometry"

    def print_habitat_data(self):
        print self
        print "  Beschreibung: %s" % self.description
        print "  BGR: %s " % self.region
        print "  Größe: %.2f ha" % self.size
        #print "  Subhabitate: %d" % len(self.sub_habitats)
        print "  Bundesland: %s" % self.fed_state
        print "  Habitattypen:"
        for ht in self.habitat_types:
            print "    %s" % ht
        print "  Arten:"
        for sp in self.species:
            print "    %s" % sp
        print "  URL: %s" % self.url

    def __str__(self):
        return "%s: %s" % (self.sitecode, self.name)
    
if __name__ == '__main__':
    
    import csv
    import pickle
    
    csv_src = r"D:\dev\python\geo\habitat\data\_ffh_types.csv"
    pkl_src = r"ffh_types.pkl"

    # defining constants, these are the column headers in the csv-file used
    # as source for habitat type data
    N2000_KEY = 'N2000 code'
    N2000_NAME = 'Name of the habitat type'
    N2000_NAME_DE = 'Name des Habitattyps'
    N2000_PRIORITY = 'Priority'
    N2000_SHORTNAME = 'Shortname'
    N2000_SPECIES = 'Characteristic plant species [EUNIS]'
    
    reader = csv.DictReader(open(csv_src, 'rb'), delimiter = ';')

    # defining dictionary to hold habitat type data
    ffh_types = dict()
    for row in reader:
        # retrieving N2000 code
        n2000_code = row[N2000_KEY]
        
        # creating new habitat type
        ht = HabitatType(n2000_code, row[N2000_NAME], row[N2000_SHORTNAME])
        # adding german translation
        ht.add_translation('de', row[N2000_NAME_DE])
        
        species = row[N2000_SPECIES].split(", ")
        [ht.add_characteristic_species(Species(sp)) for sp in species]
        
        #ht.add_characteristic_species()
        # setting priority
        if row[N2000_PRIORITY]:
            ht.set_priority()
        # adding habitat type to dictionary of habitat types
        ffh_types[n2000_code] = ht
    else:
        ht = ffh_types['6520']
        print ht
        print [cs.name for cs in ht.characteristic_species]
        print "Done"

    # dumping dictionary of habitat type data to external file
    print "Dumping habitat type data to %s..." % pkl_src,
    pickle.dump(ffh_types, open(pkl_src, 'wb'))
    print "Done"

