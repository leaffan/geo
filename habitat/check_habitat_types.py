#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/06/01 12:06:20

u"""
... Put description here ...
"""
import os
import pickle

from osgeo import ogr

from sqlalchemy import and_

from db.db_species import DbSpecies
from db.db_habitat_type import DbHabitatType, DbHabitatTypesSpecies, DbFkOccurrence
from db.common import Session

if __name__ == '__main__':

    pkl_src = r"data\_available_typical_species.pkl"
    shp_src = r"D:\work\ms.monina\wp4\work\natura2000_mtbq_intersect.shp"

    ds = ogr.Open(shp_src)
    ly = ds.GetLayer(0)
    
    session = Session()
    
    if os.path.isfile(pkl_src):
        available_typical_species = pickle.load(open(pkl_src))
    else:
        available_typical_species = dict()
        all_habitat_types = session.query(DbHabitatType).all()
        for ht in all_habitat_types[:]:
            print "-> Finding typical species for habitat type %s (%s)..." % (ht.type_id, ht.shortname)
            available_typical_species[ht.type_id] = list()
            typical_species = session.query(DbHabitatTypesSpecies).join(DbHabitatType).filter(
                    DbHabitatType.type_id == ht.type_id).all()
            for ts in typical_species:
                sp_name = session.query(DbSpecies).filter(DbSpecies.species_id == ts.species_id).one().name
                occurrence_cnt = len(session.query(DbFkOccurrence).filter(DbFkOccurrence.species_id == ts.species_id).all())
                if occurrence_cnt > 0:
                    available_typical_species[ht.type_id].append(ts)
                    print "\t+ %s" % sp_name
        else:
            pickle.dump(available_typical_species, open(pkl_src, 'wb'))
            
    #print [sp.get_species().name for sp in available_typical_species['8110']]

    for ft in ly[7400:7402]:
        quad_id = ft.GetFieldAsString('id')
        habitat_types = ft.GetFieldAsString('hab_types').split(', ')
        for ht in habitat_types:
            hab_type = session.query(DbHabitatType).filter(DbHabitatType.type_id == ht).one()
            typical_species = available_typical_species[ht]
            #print quad_id, ht, [sp.species_id for sp in typical_species]
            for sp in typical_species:
                
                occurring_species = list()
                fk_occurrences = session.query(DbFkOccurrence).filter(
                    and_(
                        DbFkOccurrence.species_id == sp.species_id,
                        DbFkOccurrence.map_id == quad_id)).all()
                if len(fk_occurrences) > 0:
                    occurring_species.append(sp)
                    #print quad_id, ht, sp.species_id, len(fk_occurrences)
            else:
                print "%s, %s (%s):" % (quad_id, hab_type.shortname, hab_type.type_id)
                print "\ttypical species: %d (%s)" % (len(typical_species), ", ".join([str(s.species_id) for s in typical_species]))
                print "\toccurring species: %d (%s)" % (len(occurring_species), ", ".join([str(s.species_id) for s in occurring_species]))
        
        
