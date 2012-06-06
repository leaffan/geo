#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/05/03 15:32:47

u"""
... Put description here ...
"""

import pickle

from osgeo import ogr

def add_habitat_type(shp_src, n2k_src):
    ds = ogr.Open(shp_src, 1)
    ly = ds.GetLayer(0)
    n2k = pickle.load(open(n2k_src))

    for ft in ly:
        sitecode = ft.GetFieldAsString('sitecode')
        print "Working on Natura 2000 area %s..." % sitecode
        n2k_area = n2k[sitecode]
        area_hab_types = ", ".join([ht.code for ht in n2k_area.habitat_types])
        ft.SetField('hab_types', area_hab_types)
        ly.SetFeature(ft)
    

if __name__ == '__main__':
    
    shp_src = r"D:\work\ms.monina\wp4\work\natura2000_mtb_intersect.shp"
    #shp_src = r"D:\work\ms.monina\wp4\work\natura2000_mtbq_intersect.shp"
    
    n2k_src = r"data\_natura_2000_de.pkl"
    hab_src = r"data\_habitat_types.pkl"

    add_habitat_type(shp_src, n2k_src)

