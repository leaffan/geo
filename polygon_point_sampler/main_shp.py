#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/06/25 13:10:18

u"""
... Put description here ...
"""

from osgeo import ogr
from shapely.geometry import Polygon
from shapely.wkb import loads

from sampler import SkeletonLineSampler

if __name__ == '__main__':
    
    shp_src = r"D:\tmp\ahs1_coverage_b.shp"
    shp_src = r"d:\tmp\skel_test.shp"
    shp_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\coverage\shp\ahs_1_coverage_reduced.shp"
    
    ds = ogr.Open(shp_src)
    ly = ds.GetLayer(0)
    
    for ft in ly:
        gm = ft.GetGeometryRef()
        py = loads(gm.ExportToWkb())
        
        sls = SkeletonLineSampler(py)
        sls.perform_sampling()
        #for s in sls.samples:
            #print "\t", s
        print sls.skel
