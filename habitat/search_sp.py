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
    sp_src = r"Z:\tmp\dh_species.txt"
    
    sp_names = [line.strip() for line in open(sp_src).readlines()]

    spf = SpeciesFinder()
    
    for spn in sp_names[:]:
        print "Searching '%s'..." % spn
        spf.set_search_name(spn)
        sp_name, sp_url, sp_info = spf.find_species(True)        
        
        if sp_name is not None:
            print spf.get_vernacular_name(sp_url)

        
        #if sp is None:
        #    print "Couldn't find species name '%s'..." % sp_name
        #else:
        #    pass
            #print "'%s' -> '%s'" % (sp_name, sp)
        #print "========================="