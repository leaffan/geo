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

if __name__ == '__main__':
    
    tk10_src_shp = r"d:\tmp\tk10_cov.shp"
    tk25_src_shp = r"d:\tmp\tk25_cov.shp"
    
    ds25 = ogr.Open(tk25_src_shp)
    ly25 = ds25.GetLayer()
    ds10 = ogr.Open(tk10_src_shp, 1)
    ly10 = ds10.GetLayer()
    
    print ly10.GetFeatureCount()
    
    
    ft25 = ly25.GetNextFeature()
    
    while ft25 is not None:
        gm25 = ft25.GetGeometryRef()
        id25 = ft25.GetFieldAsString('id')

        ul_lat = ft25.GetFieldAsDouble('ul_lat')
        ul_lon = ft25.GetFieldAsDouble('ul_lon')
        lr_lat = ft25.GetFieldAsDouble('lr_lat')
        lr_lon = ft25.GetFieldAsDouble('lr_lon')

        ly10.SetSpatialFilterRect(ul_lon, lr_lat, lr_lon, ul_lat)

        intersected_quadrants = list()
        
        ft10 = ly10.GetNextFeature()
        while ft10 is not None:
            gm10 = ft10.GetGeometryRef()
            if gm25.Intersects(gm10.Centroid()):
                intersected_quadrants.append(ft10.GetFID())
            ft10 = ly10.GetNextFeature()
        else:
            i = 1
            for ft_id in sorted(intersected_quadrants):
                ft10 = ly10.GetFeature(ft_id)
                new_id = "%s%d" % (id25, i)
                print "\t%d : %s" % (ft_id, new_id)
                i += 1
                ft10.SetField('id', new_id)
                ly10.SetFeature(ft10)
            else:
                print
        
        ly10 = ds10.GetLayer()
        ft25 = ly25.GetNextFeature()
        


