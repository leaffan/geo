#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: florkart_occurrences.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/04/11 11:14:26

u"""
This script takes a list of plant species names and retrieves all corresponding
occurences from a previously prepared copy of the FLORKART database.
"""

from _utils import access_db

if __name__ == '__main__':
    
    flk_src = r"Y:\work\ms.monina\wp4\florkart\florkart_update_2012_working_copy.mdb"
    #spc_src = r"D:\tmp\hd_annex_species_germany.txt"
    spc_src = r"Y:\work\ms.monina\wp4\eunis_ht_characteristic_species_germany.txt"

    sql_query = "SELECT DISTINCT Q.QUAD, Q.SIPNR, Q.SYM, t.TAXNR, t.SP_NUM, t.SP_NAM, t.SP_SHORT \
                 FROM FLORKART_ATLQUADINT AS Q INNER JOIN taxa AS t ON Q.SIPNR = t.taxnr \
                 WHERE (((Q.SYM)='O' Or (Q.SYM)='Q' Or (Q.SYM)='X' Or (Q.SYM)='Z') \
                 AND ((t.SP_NAM)='<replace_string>'))"

    db = access_db.AccessDataBase(flk_src)
    
    lines = open(spc_src).readlines()

    for line in lines[:2]:
        if line.strip().startswith('#'):
            continue
        tokens = line.strip().split("\t")
        species = tokens[0]
        query = sql_query.replace('<replace_string>', species)
        res = db.fetch_all(query)
        for r in res:
            if len(tokens) == 1:
                print ";".join((r['SP_NAM'], r['QUAD'], r['SYM']))
            else:
                print ";".join((r['SP_NAM'], r['QUAD'], r['SYM'], ";".join(tokens[1:])))
            
