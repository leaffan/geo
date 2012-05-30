#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: collect_habitat_types.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2011/12/22 11:42:00

u"""
Parses a pre-defined csv-file holding information about Natura 2000 habitat
types and stores the retrieved habitat type objects in a dictionary and finally
a pickle file making it available for other scripts.
"""

import csv
import pickle
import hashlib
import os
import sys

from habitat import Species, HabitatType

# defining constants, these are the column headers in the csv-file used
# as source for habitat type data
CODE = 'N2000 code'
NAME = 'Name of the habitat type'
NAME_DE = 'Name des Habitattyps'
SHORTNAME = 'Shortname'
PRIORITY = 'Priority'
SPECIES = 'Characteristic plant species [EUNIS]'

def md5_for_file(f, block_size = 2**20):
    u"""
    Iteratively create an MD5-hash for a given file by re-calculating the hash
    blockwise.
    """
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.digest()

def check_for_changes(csv_src, pkl_tgt):
    u"""
    Check whether anything has changed in the given CSV source file by comparing
    its md5 hash with another one already stored in the given pickle file.
    """
    # calculating MD5-hash for input data file
    new_md5 = md5_for_file(open(csv_src))
    # trying to retrieve hash that is available in the pickle file
    if os.path.exists(pkl_tgt):
        old_md5 = pickle.load(open(pkl_tgt))[0]
    else:
        old_md5 = hashlib.md5()

    # comparing hashes
    if new_md5 == old_md5:
        print "Nothing changed..."
        return
    else:
        return new_md5

def read_habitat_type_data_from_csv(csv_src):
    u"""
    Fill a dictionary object with information about habitat types retrieved
    from the given csv file.
    """
    reader = csv.DictReader(open(csv_src, 'rb'), delimiter = ';')
    habitat_types = dict()
    for row in reader:
        # retrieving Natura 2000 code of habitat type to be created
        code = row[CODE]
        
        # creating new habitat type
        ht = HabitatType(code, row[NAME], row[SHORTNAME])
        # adding german translation
        ht.add_translation('de', row[NAME_DE])
        # setting priority
        if row[PRIORITY]:
            ht.set_priority()
        # retrieving and adding characteristic species for habitat type
        characteristic_species = row[SPECIES].split(",")
        [ht.add_characteristic_species(Species(species.strip())) for species in characteristic_species]

        # adding habitat type to dictionary of habitat types
        habitat_types[code] = ht
    else:
        return habitat_types

def retrieve_habitat_type_data(csv_src, pkl_tgt = ''):
    u"""
    Main function for habitat type data retrieval.
    """
    if not os.path.exists(csv_src):
        print "No source file found..."
        sys.exit()

    if not pkl_tgt:
        pkl_tgt = "".join((os.path.splitext(csv_src)[0], '.pkl'))

    new_md5 = check_for_changes(csv_src, pkl_tgt)

    if not new_md5:
        sys.exit()

    print "Reading habitat type data from %s..." % csv_src,
    habitat_types = read_habitat_type_data_from_csv(csv_src)
    print "Done"

    print "Dumping habitat type data to %s..." % pkl_tgt,
    pickle.dump((new_md5, habitat_types), open(pkl_tgt, 'wb'))
    print "Done"

if __name__ == '__main__':
    
    # input data source
    csv_src = r"data\_habitat_types.csv"
    # output data target
    pkl_tgt = r"data\habitat_types.pkl"

    retrieve_habitat_type_data(csv_src)
