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
    
    sp = DbSpecies().find('Betula pendula')
    
    print sp
    
        
    
    