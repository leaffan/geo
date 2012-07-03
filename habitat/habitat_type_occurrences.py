#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/06/29 12:09:02

u"""
... Put description here ...
"""

from sqlalchemy import and_
from db.common import Session
from db.n2k import *

if __name__ == '__main__':

    tgt = r"D:\work\ms.monina\wp4\florkart_2012_occurrences_eunis_characteristic_species_n2k_areas_germany_all.txt"
    output = list()

    session = Session()
    
    # retrieving all habitat types
    habitat_types = session.query(HabitatType).all()
    
    for ht in habitat_types[:]:
        habitat_type = ht.type_id
    
        # retrieving all sites with the current habitat type
        sites_with_habitat_type = session.query(SitesHabitatTypes).filter(
            SitesHabitatTypes.type_id == habitat_type).all()
        
        # bailing out if no sites were found
        if not len(sites_with_habitat_type):
            continue

        print "Working on habitat type %s (%s)..." % (habitat_type, ht.shortname)
    
        # retrieving typical species for current habitat type
        typical_species = session.query(HabitatTypesSpecies).filter(
            HabitatTypesSpecies.type_id == habitat_type).all()
    
        if not len(typical_species):
            output.append("%s\t" % habitat_type)
            continue
    
        # reducing sites to site ids
        site_ids = [site.site_id for site in sites_with_habitat_type]
        # reducing species to species ids
        species_ids = [typical_sp.species_id for typical_sp in typical_species]
    
        # retrieving all map tiles that intersect with the previously retrieved sites
        map_intersects = session.query(SiteMapIntersect).filter(
            SiteMapIntersect.site_id.in_(site_ids)).all()
    
        # reducing map tiles to map ids
        map_ids = [map_intersect.map_id for map_intersect in map_intersects]
    
        # retrieving all Florkart occurrences with one of the specified map ids and
        # one of the specified species
        occurrences = session.query(SpeciesOccurrence).filter(
            and_(
                SpeciesOccurrence.map_id.in_(map_ids),
                SpeciesOccurrence.species_id.in_(species_ids)
            )
        ).all()
    
        # reducing occurrences to corresponding map ids
        occurrence_map_ids = [occ.map_id for occ in occurrences]
    
        print "# Habitat type %s (%s) present in the following sites:" % (habitat_type, ht.shortname)
        for site_id in site_ids:
            print "\t+ %s: %s" % (site_id, session.query(Site).filter(Site.site_id == site_id).one().name)
        print "# Typical species for habitat type %s:" % habitat_type
        for species_id in species_ids:
            print "\t+ %s (%d)" % (session.query(Species).filter(Species.species_id == species_id).one().name, species_id)
        print "Found %d occurrences of typical species in %d of a maximum of %d map tiles" % (len(occurrence_map_ids), len(set(occurrence_map_ids)), len(map_ids))
        
        output.append("\t".join((habitat_type, ", ".join(occurrence_map_ids))))
        
        print "================================================================"

    open(tgt, 'wb').write("\n".join(output))
    