#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/11/08 14:25:56

u"""
... Put description here ...
"""
import re
import math

import numpy as np

def import_species_data(sp_src, cols):
    pass

def log_mccune(array, digits = 10):
    array = np.round(array, digits)
    c = round(math.log(np.min(np.where(array == 0, 1, array)), 10))
    d = 10 ** c
    return np.log10(array + d) - c

if __name__ == '__main__':
    src = r"D:\dev\r\monina\kalmthoutse_heide\kh_vegetation_orig.txt"
    
    species = np.genfromtxt(src, delimiter = "\t", names = True)
    # retrieving column and row names
    colnames = list(species.dtype.names)
    rownames = [str(row['plot_id']) for row in species]
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

    #print sp.shape, len(rownames)
    #print sp.shape, len(colnames)

    print "Normalizing species coverage data with McCune logarithm..."
    sp = log_mccune(sp)

    from cogent.cluster.nmds import NMDS, metaNMDS
    from cogent.maths.distance_transform import dist_bray_curtis
    
    print "Calculating distance matrix..."
    distmtx = dist_bray_curtis(sp)
    
    nmds = NMDS(distmtx, dimension = 3)
    print nmds.getPoints()
    print nmds.getStress()

    #nmds = NMDS()