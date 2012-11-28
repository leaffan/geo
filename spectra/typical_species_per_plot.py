#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/11/13 14:27:00

u"""
... Put description here ...
"""

import re

import numpy as np


if __name__ == '__main__':
    
    src = r"D:\dev\r\monina\kalmthoutse_heide\kh_vegetation_orig.txt"
    ht_sp_src = r"D:\dev\r\monina\kalmthoutse_heide\kh_habtypes_typical_species_b.txt"

    species = np.genfromtxt(src, delimiter = "\t", names = True)
    # retrieving column and row names
    colnames = list(species.dtype.names)
    rownames = [int(row['plot_id']) for row in species]
    # converting structured array to real numpy array
    sp = species[list(colnames)].view((float, len(colnames)))
    # converting indefinite numbers to zero
    sp = np.nan_to_num(sp)

    print "Removing irrelevant columns..."
    pattern = "plot_id|standing_water|soil|litter|_sp|_indet"
    to_remove = [colnames.index(name) for name in colnames if re.search(pattern, name)]
    sp = np.delete(sp, to_remove, 1)
    colnames = np.delete(colnames, to_remove)

    print "Removing species with less than two occurrences..."
    sp_io = np.where(~(sp > 0), sp, 1)
    column_sums = np.sum(sp_io, 0)
    to_remove = np.where(column_sums < 2)
    sp = np.delete(sp, to_remove, 1)
    colnames = np.delete(colnames, to_remove)
    
    print "Removing plots with less than two species..."
    pl_io = np.where(~(sp > 0), sp, 1)
    row_sums = np.sum(pl_io, 1)
    to_remove = np.where(row_sums < 2)
    sp = np.delete(sp, to_remove, 0)
    rownames = np.delete(rownames, to_remove)

    ht_species = np.genfromtxt(ht_sp_src, delimiter = "\t", dtype = np.str)

    hab_types = ['2310', '2330', '3110', '3130', '4010', '4030', '7150',]

    sp = np.where(~(sp > 0), 0, 1)

    result = dict()

    for ht in hab_types:
        # retrieving typical species per habitat type
        typ_species = np.unique(ht_species[[ht_species[:,0] == ht]][:,1])
        # retrieving index of according columns
        typ_cols = [list(colnames).index(name) for name in colnames if name.replace("_", " ") in typ_species]
        print ht, len(typ_cols), ", ".join(colnames[typ_cols])
        single_result = list()
        for rowname, row in zip(rownames, sp):
            #print rowname, row[typ_cols].sum()
            single_result.append(row[typ_cols].sum())
        result[ht] = single_result
        
    output = list()

    output.append("\t".join(['plot_id'] + sorted(result.keys())))

    for i in range(0, len(rownames)):
        single_line = list()
        single_line.append(str(rownames[i]))
        for key in sorted(result.keys()):
            single_line.append(str(result[key][i]))
        output.append("\t".join(single_line))

    open(r"z:\kh_typical_species_per_habitat_type.txt", "wb").write("\n".join(output))