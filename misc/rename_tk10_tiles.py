#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/03/27 11:58:07

u"""
... Put description here ...
"""

from osgeo import ogr

def quad_generator(count, width):
    row = 0
    for i in range(0, count):
        if i % width == 0:
           row += 1 
        id_1 = i * 2 + (row - 1) * width * 2
        id_2 = id_1 + 1
        id_3 = id_1 + width * 2
        id_4 = id_3 + 1
        yield (id_1, id_2, id_3, id_4)

if __name__ == '__main__':
    
    tk10_src_shp = r"d:\tmp\tk10_cov_final.shp"
    tk25_src_shp = r"d:\tmp\tk25_cov_final.shp"
    
    ds25 = ogr.Open(tk25_src_shp)
    ly25 = ds25.GetLayer()
    ds10 = ogr.Open(tk10_src_shp, 1)
    ly10 = ds10.GetLayer()

    ft25_id = 0

    for ft10_ids in quad_generator(ly25.GetFeatureCount(), 61):
        ft25 = ly25.GetFeature(ft25_id)
        id25 = ft25.GetFieldAsString('id')
        print "Working on id '%s'..." % id25
        k = 1
        for ft10_id in ft10_ids:
            new_id = "%s%d" % (id25, k)
            k += 1
            print new_id
            ft10 = ly10.GetFeature(ft10_id)
            ft10.SetField('id', new_id)
            ly10.SetFeature(ft10)
        ft25_id += 1

