#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: collect_species_eunis.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/01/11 10:31:20

u"""
This script allows to collect taxonomic and author information for a given
species from the EUNIS database.
Collected data can be stored using a pickle file.
"""

import os
import pickle

from habitat import Species
from habitat import get_taxonomic_information

def collect_species_data(species_name, pkl_tgt = '', verbose = False):
    
    if pkl_tgt and os.path.isfile(pkl_tgt):
        if verbose:
            print "Restoring species data from %s..." % (pkl_tgt),
        species_data = pickle.load(open(pkl_tgt))
        if verbose:
            print "Done"
    else:
        species_data = dict()

    if species_data.has_key(species_name):
        species = species_data[species_name]
        if species.taxonomic_information:
            if verbose:
                print "Taxonomic information for '%s' already available..." % species_name
                return

    species = get_taxonomic_information(species_name)
    
    if verbose:
        species.print_species_data()
    
    species_data[species.name] = species
    # TODO:
    #if species_name != species.name:
    #    species_data[species_name] = species.name

    if pkl_tgt:
        if verbose:
            print "Dumping species data to %s..." % (pkl_tgt),
        pickle.dump(species_data, open(pkl_tgt, 'wb'))
        if verbose:
            print "Done"

    return species

if __name__ == '__main__':
    
    # output data target
    sps_pkl_tgt = r"data\_eunis_species.pkl"

    sps_src = r"D:\tmp\sps.txt"
    lines = open(sps_src).readlines()
    for line in lines:
        #collect_species_data(line.strip(), pkl_tgt = sps_pkl_tgt, verbose = True)
        sp = collect_species_data(line.strip())
