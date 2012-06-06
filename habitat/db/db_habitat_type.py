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

from db_species import DbSpecies

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

class DbFkOccurrence(Base):
    __tablename__ = 'fk_occurrences'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

if __name__ == '__main__':
    
    from db_species import DbSpecies
    
    ht = DbHabitatType().find('2310')
    sp = DbSpecies().find('Calluna vulgaris')
    hs = DbHabitatTypesSpecies()
    
    print ht
    print sp

    session = Session()
    xxx = session.query(DbHabitatTypesSpecies).join(DbHabitatType).filter(DbHabitatType.type_id == '2310').all()
    
    for x in xxx:
        sp = session.query(DbSpecies).filter(DbSpecies.species_id == x.species_id).one()
        print sp.species_id, sp

    

