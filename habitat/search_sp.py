#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/03/15 13:11:50

u"""
... Put description here ...
"""

from db.species_finder import SpeciesFinder

if __name__ == '__main__':
    
    sp_names = ['Agropyron repens', 'Barbarea vulgaris', 'Calamagrosis canescens', 'Oxalis stricta']
    sp_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\field\kh_all_species_orig.txt"
    sp_src = r"D:\work\ms.monina\wp5\doeberitzer_heide\field\dh_all_species_orig.txt"
    #sp_names = ['Abies alba', 'Salix aurita', 'Abies sp.', 'Hieracium pilosela']
    
    sp_names = [line.strip() for line in open(sp_src).readlines()]

    spf = SpeciesFinder()
    
    for spn in sp_names[:]:
        #print "Searching '%s'..." % spn
        spf.set_search_name(spn)
        sp_name, sp_url, sp_info = spf.find_species(True)        
        #print sp_name, sp_url, sp_info
        #if sp_name is not None:
        #    print spf.get_vernacular_name(sp_url)
