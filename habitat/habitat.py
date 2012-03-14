#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: habitat.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2011/06/29 12:06:07

u"""
... Put description here ...
"""

from urlparse import urlparse

from osgeo import ogr
from shapely.geometry import Point, LineString, Polygon
from shapely.wkb import loads
from shapely.ops import linemerge

class Species():
    
    TAXA = ['Kingdom', 'Phylum', 'Class', 'Subclass', 'Order', 'Family', 'Genus']
    
    def __init__(self, name):
        self.set_name(name)
        self.is_synonym = ''
        self.synonyms = set()
        self.translations = dict()
        self.associated_habitat_types = list()
        self.urls = dict()
        self.taxonomic_information = dict()
        self.author = ''
    
    def set_name(self, name, synonym = False):
        if synonym:
            self.synonyms.add(synonym)
            return
        self.name = name
    
    def set_synonym(self, is_synonym):
        if is_synonym:
            self.is_synonym = True
        else:
            self.is_synonym = False
    
    def set_url(self, url):
        parsed_url = urlparse(url)
        self.urls[parsed_url.hostname] = url
    
    def add_translation(self, lang, name):
        self.translations[lang.lower()] = name
    
    def set_associated_habitat_type(self, habitat_type):
        self.associated_habitat_types.append(habitat_type)
    
    def set_taxonomic_information(self, tax_dict):
        for key in tax_dict:
            if key in self.TAXA:
                self.taxonomic_information[key] = tax_dict[key]

    def print_taxonomic_information(self):
        i = 2
        for t in self.TAXA:
            if self.taxonomic_information.has_key(t):
                print "%s%s: %s" % (i * ' ',t, self.taxonomic_information[t])
                i += 2

    def print_species_data(self):
        print "Species name: %s" % (self.name)
        print "  Author: %s" % (self.author.encode('utf-8'))
        self.print_taxonomic_information()
        print "  URL(s):"
        for host in self.urls:
            print "    [%s] : %s" % (host, self.urls[host])

    def is_plant(self):
        if not self.taxonomic_information:
            return None
        if not self.taxonomic_information.has_key('Kingdom'):
            return None
        if self.taxonomic_information['Kingdom'].lower() == "plantae":
            return True
        else:
            return False
    
    def is_animal(self):
        if not self.taxonomic_information:
            return None
        if not self.taxonomic_information.has_key('Kingdom'):
            return None
        if self.taxonomic_information['Kingdom'].lower() == "animalia":
            return True
        else:
            return False

    def set_author(self, author):
        self.author = author
    
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
    
    BIOGEOGRAPHICAL_REGIONS = {
        1 : "alpine",
        2 : "atlantic",
        3 : "continental",
        4 : "anatolian",
        5 : "arctic",
        6 : "black sea",
        7 : "boreal",
        8 : "mediterranean",
        9 : "pannonian",
        10 : "steppic",
    }
    
    def __init__(self, sitecode, name = ''):
        self.sitecode = sitecode
        self.set_name(name)
        self.description = None
        self.region = None
        self.nuts_code = None
        self.size = 0
        self.habitat_types = list()
        self.species = list()
        self.urls = dict()
        self.geometry = None

    def set_name(self, name):
        self.name = name

    def set_region(self, region):
        self.region = region
        
    def set_administrative_area(self, nuts_code):
        self.nuts_code = nuts_code

    def set_size(self, size):
        self.size = size

    def set_url(self, url):
        parsed_url = urlparse(url)
        self.urls[parsed_url.hostname] = url

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
        print "  Description: %s" % self.description
        print "  BGR: %s " % self.BIOGEOGRAPHICAL_REGIONS[self.region]
        print "  Size: %.2f ha" % self.size
        #print "  Subhabitate: %d" % len(self.sub_habitats)
        print "  Administrative unit (NUTS-Code): %s" % self.nuts_code
        print "  Available Habitat types:"
        for ht in self.habitat_types:
            print "    %s" % ht
        print "  Available (plant) species:"
        for sp in self.species:
            if not sp.is_plant():
                continue
            print "    %s" % sp
        print "  URL(s):"
        for host in self.urls:
            print "    [%s] : %s" % (host, self.urls[host])

    def __str__(self):
        return "%s: %s" % (self.sitecode, self.name)

def find_valid_name(synonym, verbose = False):
    import urllib2
    import lxml.html
    
    URL_PREFIX = r"http://eunis.eea.europa.eu/species-names-result.jsp?typeForm=0&showScientificName=true&searchVernacular=false&sort=3&ascendency=1&showValidName=true&relationOp=3&searchSynonyms=true&scientificName=Agropyron+repens"
    URL_SUFFIX = "&submit=Search"

    URL_PREFIX = r"http://eunis.eea.europa.eu/species-names-result.jsp?typeForm=0&showGroup=true&showFamily=true&showOrder=true&showScientificName=true&searchVernacular=false&sort=3&ascendency=1&showValidName=true&relationOp=3&searchSynonyms=True&submit=Search&scientificName="
    
    url_query_pt = "+".join(synonym.split())
    query_url = "".join((URL_PREFIX, url_query_pt))
    
    query_conn = urllib2.urlopen(query_url)
    query_doc = lxml.html.parse(query_conn).getroot().get_element_by_id('content')
    query_doc.make_links_absolute()

    search_results = query_doc.xpath("//table[@summary='Search results']/tbody/tr")

    found_species_name, added_text, tgt_url = retrieve_name_from_search_result_row(search_results[0])

    if found_species_name.lower() == synonym.lower():
        if not added_text:
            if verbose:
                print "'%s' is a valid species name: [%s]" % (synonym, tgt_url)
            valid_name = synonym
        elif added_text.lower() == '(synonym)':
            valid_name = retrieve_valid_name_for_synonym(synonym, tgt_url, verbose)
        else:
            if verbose:
                print "'%s' is a %s: [%s]" % (synonym, added_text, tgt_url)
            valid_name = synonym
    else:
        if verbose:
            print "Best match for '%s': '%s' %s [%s]" % (synonym, found_species_name, added_text, tgt_url)
        valid_name = find_valid_name(found_species_name)

    return valid_name

def retrieve_valid_name_for_synonym(synonym, url, verbose = False):
    import urllib2
    import lxml.html
    
    conn = urllib2.urlopen(url)
    doc = lxml.html.parse(conn).getroot().get_element_by_id('content')
    doc.make_links_absolute()

    heading = doc.xpath("//h1[@class='documentFirstHeading']")[0]
    potential_valid_name = heading.xpath("./span/a/strong")[0].text_content().strip()
    tgt_url = heading.xpath("./span/a")[0].attrib['href']

    if verbose:
        print "'%s' is a synonym of '%s': [%s]" % (synonym, potential_valid_name, tgt_url)
    
    valid_name = find_valid_name(potential_valid_name, verbose)
    return valid_name

    #print heading.text_content().encode('utf-8').strip()
    #print valid_name.text_content().strip()

def retrieve_name_from_search_result_row(row):
    species_element = row.xpath("./td")[3]
    name_element = species_element.xpath("./a")[0]
    tgt_url = species_element.xpath("./a")[0].attrib['href']
    found_species_name = name_element.text_content().strip()
    added_text = name_element.tail.strip()
    return found_species_name, added_text, tgt_url

def get_taxonomic_information(species_name, verbose = False):
    u"""
    Retrieve taxonomic information for the given species name using the EUNIS
    database. Returns a species object with a subset of information available
    from EUNIS, including author and taxonomic information.
    """
    
    import urllib2
    import lxml.html
    
    URL_PREFIX = r"http://eunis.eea.europa.eu/species-names-result.jsp?typeForm=0&showScientificName=true&searchVernacular=false&sort=3&ascendency=1&showValidName=true&relationOp=3&scientificName="
    URL_SUFFIX = r"&submit=Search"

    url_query_pt = "+".join(species_name.split())
    query_url = "".join((URL_PREFIX, url_query_pt, URL_SUFFIX))

    if verbose:
        print query_url

    search_conn = urllib2.urlopen(query_url)
    search_doc = lxml.html.parse(search_conn).getroot().get_element_by_id('content')
    search_doc.make_links_absolute()

    search_results = search_doc.xpath("//table[@summary='Search results']/tbody/tr")

    for row in search_results:
        species_element = row.xpath("./td/a")[0]
        species_url = species_element.attrib['href']
        found_species_name = species_element.text_content().strip()
        if 'check_green.gif' in row.xpath("./td/img")[0].attrib['src']:
            if verbose:
                print found_species_name, species_url
            #if found_species_name != species_name:
            #    print "!!!: %s <-> %s" % (species_name, found_species_name)
            species_conn = urllib2.urlopen(species_url)
            species_doc = lxml.html.parse(species_conn).getroot().get_element_by_id('content')
            species_doc.make_links_absolute()
            
            taxonomic_rank = species_doc.xpath("//table[@class='datatable fullwidth']/tr/td")[1].text.strip().lower()
            
            print taxonomic_rank
            if taxonomic_rank.lower() != "species":
                return None
            
            author_info = species_doc.xpath("//table[@class='datatable fullwidth']/tr/td")[2]
            if not author_info.text is None:
                author = author_info.text.strip()
            else:
                author = ''

            tax_info = species_doc.xpath("//table[@class='datatable fullwidth'][2]/tbody/tr")
            tax_dict = dict()
            
            for row in tax_info:
                level = row.xpath("./td")[0].text_content().strip()
                info = row.xpath("./td")[1].text_content().strip()
                tax_dict[level] = info

            species = Species(species_name)
            species.set_taxonomic_information(tax_dict)
            species.set_author(author)
            species.set_url(species_url)

            if verbose:
                species.print_species_data()

            return species

if __name__ == '__main__':
    
    pass
