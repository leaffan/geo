#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/05/15 12:47:31

u"""
... Put description here ...
"""

from habitat import Species, SpeciesFinder

if __name__ == '__main__':
    
    from db.db_species import DbSpecies
    
    sp_src = r"D:\work\ms.monina\wp4\eunis_ht_characteristic_species_germany.txt"
    lines = open(sp_src).readlines()
    
    i = 0
    
    output = list()
    
    for line in lines[:]:
        species_name, habitat_types = line.strip().split("\t")
        habitat_types = habitat_types.split("/")
        #print species, habitat_types
        species = DbSpecies().find(species_name)
        
        for ht in habitat_types:
            output.append("\t".join((str(i), ht, str(species.species_id))))
            i += 1
    
    print "\n".join(output)
        
        #print species.species_id, species.name, habitat_types
    
    


    import sys
    sys.exit()

    
    
    spf = SpeciesFinder()
    output = list()
    
    for line in lines[:]:
        species, habitat_types = line.strip().split("\t")
        habitat_types = habitat_types.split("/")
        print species, habitat_types
        
        spf.set_search_name(species)
        spf.find_species()
        spf.get_species_data()
        
        url = spf.species.urls['eunis.eea.europa.eu']
        sp_id = int(url.split("/")[-1])
        basic_info = "\t".join((str(sp_id), spf.species.name, url, spf.species.author))
        taxonomic_info = list()
        for t in spf.species.TAXA:
            if spf.species.taxonomic_information.has_key(t):
                taxonomic_info.append(spf.species.taxonomic_information[t])
            else:
                taxonomic_info.append("")
        output.append("\t".join((basic_info, "\t".join(taxonomic_info))))

    print "\n".join(output)