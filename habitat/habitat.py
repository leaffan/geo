#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: habitat.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2011/06/29 12:06:07

u"""
... Put description here ...
"""

import urllib2
import lxml.html
import Levenshtein

from urlparse import urlparse

from osgeo import ogr
from shapely.geometry import Point, LineString, Polygon
from shapely.wkb import loads
from shapely.ops import linemerge

class Species():
    
    TAXA = ['Kingdom', 'Division', 'Class', 'Subclass', 'Order', 'Family', 'Genus']
    
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

class SpeciesFinder():
    URL_PREFIX = r"http://eunis.eea.europa.eu/species-names-result.jsp?typeForm=0&pageSize=300&showGroup=true&showFamily=true&showOrder=true&showScientificName=true&searchVernacular=false&sort=3&ascendency=1&showValidName=true&relationOp=2&searchSynonyms=True&submit=Search&scientificName="

    def __init__(self, search_name = ''):
        self.search_name = search_name
    
    def set_search_name(self, search_name):
        self.search_name = search_name
    
    def search_on_eunis(self):
        if not self.search_name:
            return list()
        
        query_str = "+".join(self.search_name.split())
        query_url = "".join((self.URL_PREFIX, query_str))
        query_conn = urllib2.urlopen(query_url)

        self.query_doc = lxml.html.parse(query_conn).getroot().get_element_by_id('content')
        self.query_doc.make_links_absolute()

        search_results = self.query_doc.xpath("//table[@summary='Search results']/tbody/tr")
        
        return search_results
    
    def find_species(self, verbose = False):
        search_results = self.search_on_eunis()
        
        if not search_results:
            return None
        
        if len(search_results) > 1:
            (sp_name, sp_type, sp_url), similarity = self.find_best_match(search_results)
            if verbose:
                print "Best match for '%s': '%s' %s [%s]" % (self.search_name, sp_name, sp_type, sp_url)
        else:
            (sp_name, sp_type, sp_url) = self.get_species_info_from_row(search_results[0])

        if sp_type.lower() == "(synonym)":
            sp_name, sp_url = self.find_valid_name_for_synonym(sp_name, sp_url, verbose)

        self.species = Species(sp_name)
        self.species.set_url(sp_url)
        self.get_species_data()
        return self.species
    
    def find_valid_name_for_synonym(self, synonym, synonym_url, verbose = False):
        species_conn = urllib2.urlopen(synonym_url)
        self.species_doc = lxml.html.parse(species_conn).getroot().get_element_by_id('content')
        self.species_doc.make_links_absolute()

        heading = self.species_doc.xpath("//h1[@class='documentFirstHeading']")[0]
        valid_name = heading.xpath("./span/a/strong")[0].text_content().strip()
        tgt_url = heading.xpath("./span/a")[0].attrib['href']

        author_info = self.species_doc.xpath("//table[@class='datatable fullwidth']/tr/td")[2]
        if not author_info.text is None:
            author = author_info.text.strip()
        else:
            author = ''

        if verbose:
            print "'%s' (%s) is a synonym of '%s': [%s]" % (synonym, author, valid_name, tgt_url)
        
        return valid_name, tgt_url
    
    def find_species_column(self):
        table_header = self.query_doc.xpath("//table[@summary='Search results']/thead/tr/th")
        i = 0
        for th in table_header:
            if th.text_content().strip() == 'Scientific name':
                idx = i
                break
            i += 1
        return idx
    
    def get_species_data(self):
        u"""
        Retrieve taxonomic information for the given species name using the EUNIS
        database. Sets species object to with a subset of information available
        from EUNIS, including author and taxonomic information.
        """
        species_conn = urllib2.urlopen(self.species.urls['eunis.eea.europa.eu'])
        self.species_doc = lxml.html.parse(species_conn).getroot().get_element_by_id('content')
        self.species_doc.make_links_absolute()

        taxonomic_rank = self.species_doc.xpath("//table[@class='datatable fullwidth']/tr/td")[1].text.strip().lower()
            
        author_info = self.species_doc.xpath("//table[@class='datatable fullwidth']/tr/td")[2]
        if not author_info.text is None:
            author = author_info.text.strip()
        else:
            author = ''

        tax_info = self.species_doc.xpath("//table[@class='datatable fullwidth'][2]/tbody/tr")
        tax_dict = dict()
            
        for row in tax_info:
            level = row.xpath("./td")[0].text_content().strip()
            info = row.xpath("./td")[1].text_content().strip()
            tax_dict[level] = info        

        self.species.set_taxonomic_information(tax_dict)
        self.species.set_author(author)
        #self.species.print_species_data()
    
    def get_species_info_from_row(self, row):
        idx = self.find_species_column()
        species_element = row.xpath("./td")[idx]
        species_link_element = species_element.xpath("./a")[0]
        
        sp_url = species_element.xpath("./a")[0].attrib['href']
        sp_name = species_link_element.text_content().strip()
        sp_type = species_link_element.tail.strip()
        
        return sp_name, sp_type, sp_url
    
    def find_best_match(self, search_results):
        best_match = ((), -1.0)        
        idx = self.find_species_column()
        for row in search_results:
            sp_name, sp_type, sp_url = self.get_species_info_from_row(row)
            ratio = Levenshtein.ratio(self.search_name, sp_name)
            if ratio > best_match[-1]:
                best_match = ((sp_name, sp_type, sp_url), ratio)
            elif ratio == best_match[-1]:
                if not sp_type:
                    best_match = ((sp_name, sp_type, sp_url), ratio)
        else:
            return best_match

if __name__ == '__main__':
    
    import pickle
    src = r"data\_natura_2000_de.pkl"
    n2k_de = pickle.load(open(src))
    i = 0

    output = list()

    for sitecode in sorted(n2k_de):
        site = n2k_de[sitecode]
        #output.append("\t".join((sitecode, site.name, site.description, str(site.region), str(site.nuts_code), str(site.size), site.urls['www.bfn.de'])))
        for ht in site.habitat_types:
            output.append("\t".join((str(i), sitecode, ht.code)))
            i += 1
        #i += 1
        #if i > 5:
        #    break

    print "\n".join(output)
