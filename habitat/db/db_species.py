#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/05/15 12:56:32

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

if __name__ == '__main__':
    
    src = r"D:\work\ms.monina\wp4\florkart_2012_occurrences_eunis_characteristic_species_germany.txt"
    
    lines = open(src).readlines()
    
    sp = DbSpecies().find('Betula pendula')
    
    i = 0
    
    for line in lines[:]:
        tokens = line.strip().split(";")
        sp_name, map_id, symbol = tokens[0:3]
        if sp_name != sp.name:
            sp = DbSpecies().find(sp_name)
        
        if int(map_id[-1]):
            is_quadrant = True
        else:
            is_quadrant = False
        
        print "%d\t%s\t%d\t%s\t%s" % (i, map_id, sp.species_id, is_quadrant, symbol)
        
        i += 1
        

    