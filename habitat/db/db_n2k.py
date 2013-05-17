#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/05/31 15:28:53

u"""
... Put description here ...
"""

from common import Base
from common import Engine
from common import Session

from sqlalchemy import and_
from sqlalchemy.sql.expression import *

class DbSpecies(Base):
    __tablename__ = 'species'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}
    
    def __init__(self):
        pass
    
    @classmethod
    def find(self, species_name):
        session = Session()
        try:
            species = session.query(DbSpecies).filter(
                DbSpecies.name == species_name
                ).one()
        except:
            species = None
        finally:
            session.close()
        return species

    def __str__(self):
        return "%s" % self.name

class DbHabitatType(Base):
    __tablename__ = 'habitat_types'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

    @classmethod
    def find(self, type_id):
        session = Session()
        try:
            habitat_type = session.query(DbHabitatType).filter(
                DbHabitatType.type_id == type_id
                ).one()
        except:
            habitat_type = None
        finally:
            session.close()
        return habitat_type

    def __str__(self):
        return "[%s] %s" % (self.type_id, self.shortname)

class DbHabitatTypesSpecies(Base):
    __tablename__ = 'habitat_types_species'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass
    
    def get_species(self):
        session = Session()
        try:
            species = session.query(DbSpecies).filter(
                DbSpecies.species_id == self.species_id
                ).one()
        except:
            species = None
        finally:
            session.close()
        return species

class DbSitesHabitatTypes(Base):
    __tablename__ = 'sites_habitat_types'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

class DbQuadSpeciesOccurrence(Base):
    __tablename__ = 'quad_species_occurrences'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

class DbMtbSpeciesOccurrence(Base):
    __tablename__ = 'mtb_species_occurrences'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

class DbSite(Base):
    __tablename__ = 'sites'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

class DbSiteOnMtbTile(Base):
    __tablename__ = 'sites_on_mtb_tiles'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

class DbSiteOnQuadTile(Base):
    __tablename__ = 'sites_on_quad_tiles'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass
    
if __name__ == '__main__':
    
    from operator import attrgetter
    
    habitat_type = '9120'

    session = Session()
    
    # retrieving all sites with the current habitat type
    sites_with_habitat_type = session.query(DbSitesHabitatTypes).filter(
        DbSitesHabitatTypes.type_id == habitat_type).all()
    # retrieving typical species for current habitat type
    typical_species = session.query(DbHabitatTypesSpecies).filter(
        DbHabitatTypesSpecies.type_id == habitat_type).all()

    # reducing sites to site ids
    f = attrgetter('site_id')
    site_ids = [f(site) for site in sites_with_habitat_type]
    # reducing species to species ids
    f = attrgetter('species_id')
    species_ids = [f(typical_sp) for typical_sp in typical_species]

    # retrieving all map tiles that intersect with the previously retrieved sites
    map_ids = session.query(DbSiteOnQuadTile).filter(
        DbSiteOnQuadTile.site_id.in_(site_ids)).all()

    # reducing map tiles to map ids
    f = attrgetter('map_id')
    map_ids = [f(map_id) for map_id in map_ids]

    import sys
    sys.exit()

    # retrieving all Florkart occurrences with one of the specified map ids and
    # one of the specified species
    occurrences = session.query(DbFkOccurrence).filter(
        and_(
            DbFkOccurrence.map_id.in_(map_ids),
            DbFkOccurrence.species_id.in_(species_ids)
        )
    ).all()

    # reducing occurrences to corresponding map ids
    f = attrgetter('map_id')
    occurrence_map_ids = [f(occ) for occ in occurrences]

    print site_ids
    print species_ids
    print len(map_ids)


    print len(set(occurrence_map_ids))

   
    
    


