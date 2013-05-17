#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: collect_characteristic_species_eunis.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2011/12/14 12:12:10

u"""
Browses the European nature information system website (EUNIS) to retrieve
characteristic plant species for a complete list of Natura 2000 habitat types
found on the same website. Finally dumps all retrieved information to a pickle
file.
"""
import re
import urllib2
import time
import pickle

import lxml.html

from habitat import SpeciesFinder

species_suffix = "species"

def retrieve_document(url, id = ''):
    conn = urllib2.urlopen(url)
    doc = lxml.html.parse(conn).getroot()
    if id:
        doc = doc.get_element_by_id(id)
    doc.make_links_absolute()
    return doc

def find_species(url, species_data):
    content = retrieve_document(url, 'content')
    
    for link in content.iterlinks():
        element, attribute, tgt = link[:-1]
        # looking for links containing the word *species* in their target url
        match = re.search("".join(("\/", species_suffix, "\/")), tgt)
        if match is not None:
            # retrieving species name
            sp_name = element.text
            #print "<<<", len(species_data), ">>>"
            if species_data.has_key(sp_name):
                species = species_data[sp_name]
                print "\tSpecies '%s' already in database..." % sp_name
            else:
                spf = SpeciesFinder(sp_name)
                species = spf.find_species()
                if not species is None and species.is_plant():
                    species.print_species_data()
                    species_data[sp_name] = species

if __name__ == '__main__':
    
    # setting source urls
    base_url = "http://eunis.eea.europa.eu"
    url_main = "habitats-annex1-browser.jsp?expand=1,11,12,13,14,15,16,2,21,22,23,3,31,32,4,40,5,51,52,53,54,6,61,62,63,64,65,7,71,72,73,8,81,82,83,9,90,91,92,93,94,95"
    
    # setting source species dictionary
    sps_pkl_src = r"data\_eunis_species.pkl"
    # setting target species dictionary
    sps_pkl_tgt = r"data\_eunis_species_extended.pkl"
    
    # loading existing species data
    sps_data = pickle.load(open(sps_pkl_src))
    
    species_suffix = "species"
    
    # accessing website overviewing habitat types
    url = "/".join((base_url, url_main))
    conn = urllib2.urlopen(url)
    doc = lxml.html.parse(conn).getroot()
    content = doc.get_element_by_id('content')
    content.make_links_absolute()
    
    link_regex = "habitats\/\d+"
    
    # iterating over all links on overview page
    for link in content.iterlinks():
        element, tag, tgt, pos = link
        # looking for links pointing to habitat types
        if element.tag == 'a':
            match = re.search(link_regex, tgt)
            if match is not None:
                print element.text
                # finding all species for current habitat type
                find_species("/".join((tgt, species_suffix)), sps_data)
                time.sleep(0.05)
                
        pickle.dump(sps_data, open(sps_pkl_tgt, 'wb'))