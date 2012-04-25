#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/04/10 14:19:45

u"""
... Put description here ...
"""

from osgeo import ogr

if __name__ == '__main__':

    src_shp = r"D:\work\ms.monina\wp4\shp\blattschnitte\mtb_utm32.shp"
    ref_shp = r"D:\work\ms.monina\wp4\shp\blattschnitte\tk25_utm32.shp"

    src_ds = ogr.Open(src_shp, 1)
    src_ly = src_ds.GetLayer(0)
    
    ref_ds = ogr.Open(ref_shp)
    ref_ly = ref_ds.GetLayer(0)
    
    for src_ft in src_ly[:]:
        if src_ft.GetFID() % 1000 == 0:
            print "Working on feature %d..." % src_ft.GetFID()
        c = src_ft.GetGeometryRef().Centroid()
        ref_ly.SetSpatialFilter(c)
        if not ref_ly.GetFeatureCount():
            continue
        ref_ft = ref_ly.GetNextFeature()
        #print ref_ft.GetFieldAsString('name')
        src_ft.SetField('name', ref_ft.GetFieldAsString('name'))
        src_ft.SetField('lva', ref_ft.GetFieldAsString('lva'))
        src_ly.SetFeature(src_ft)
