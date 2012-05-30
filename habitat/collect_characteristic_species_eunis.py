#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2011/12/14 12:12:10

u"""
... Put description here ...
"""
import re
import urllib2
import time
import pickle

import lxml.html

from habitat import get_taxonomic_information

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
        match = re.search("".join(("\/", species_suffix, "\/")), tgt)
        if match is not None:
            sp_name = element.text
            print "<<<", len(species_data), ">>>"
            if species_data.has_key(sp_name):
                species = species_data[sp_name]
                print "Species '%s' already in database..." % sp_name
            else:
                species = get_taxonomic_information(sp_name)
                if not species is None:
                    species.print_species_data()
                    species_data[sp_name] = species

def is_plant_species(species_url):
    kingdom, genus = find_kingdom_and_genus(species_url)
    
    if kingdom == 'plantae' and genus == 'species':
        return True
    else:
        return False

def find_kingdom_and_genus(species_url):
    content = retrieve_document(species_url, 'content')
    
    kingdom = content.xpath("//table[@class='datatable fullwidth'][2]/tbody/tr/td")[1].text.strip().lower()
    genus = content.xpath("//table[@class='datatable fullwidth']/tr/td")[1].text.strip().lower()

    return kingdom, genus    

if __name__ == '__main__':
    
    base_url = "http://eunis.eea.europa.eu"
    url_main = "habitats-annex1-browser.jsp?expand=1,11,12,13,14,15,16,2,21,22,23,3,31,32,4,40,5,51,52,53,54,6,61,62,63,64,65,7,71,72,73,8,81,82,83,9,90,91,92,93,94,95"
    
    sps_pkl_src = r"data\_eunis_species.pkl"
    sps_pkl_tgt = r"data\_eunis_species_extended.pkl"
    
    
    sps_data = pickle.load(open(sps_pkl_src))
    
    
    species_suffix = "species"
    
    url = "/".join((base_url, url_main))
    conn = urllib2.urlopen(url)
    doc = lxml.html.parse(conn).getroot()
    content = doc.get_element_by_id('content')
    content.make_links_absolute()
    
    link_regex = "habitats\/\d+"
    
    for link in content.iterlinks():
        element, tag, tgt, pos = link
        #print link
        if element.tag == 'a':
            match = re.search(link_regex, tgt)
            if match is not None:
                print element.text
                find_species("/".join((tgt, species_suffix)), sps_data)
                time.sleep(0.05)
                
        pickle.dump(sps_data, open(sps_pkl_tgt, 'wb'))