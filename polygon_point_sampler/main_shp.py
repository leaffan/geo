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

from sampler import SkeletonLineSampler, RegularGridSampler, UniformRandomSampler
from _utils import ogr_utils

if __name__ == '__main__':
    
    shp_src = r"D:\tmp\ahs1_coverage_b.shp"
    shp_src = r"d:\tmp\skel_test.shp"
    shp_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\coverage\shp\ahs_1_coverage_reduced.shp"
    shp_src = r"Z:\fabi\shp\_wet_orig.shp"
    
    tgt_file = r"Z:\fabi\shp\_nf_orig_pnt.shp"
    
    tgt_type = 'nf'
    
    ds = ogr.Open(shp_src)
    ly = ds.GetLayer(0)
    sr = ly.GetSpatialRef()
    
    tgt_ds, tgt_ly = ogr_utils.create_shapefile(tgt_file, ogr.wkbPoint, sr)
    ogr_utils.create_feature_definition_from_template(ly, tgt_ly)

    new_field = ogr.FieldDefn('x', ogr.OFTReal)
    tgt_ly.CreateField(new_field)
    new_field = ogr.FieldDefn('y', ogr.OFTReal)
    tgt_ly.CreateField(new_field)
    
    i = 0

    for ft in ly:
        t = ft.GetFieldAsString('type')
        if t != tgt_type:
            continue
        
        gm = ft.GetGeometryRef()
        py = loads(gm.ExportToWkb())
        
        #sls = SkeletonLineSampler(py)
        #sls.perform_sampling()

        rgs = RegularGridSampler(py, 20, 20)
        rgs.perform_sampling()
        
        for s in rgs.samples:
            i += 1
            print "\t", s
            tgt_gm = ogr.Geometry(ogr.wkbPoint)
            tgt_gm.SetPoint_2D(0, s.x, s.y)
            tgt_ft = ogr.Feature(tgt_ly.GetLayerDefn())
            tgt_ft.SetGeometry(tgt_gm)
            tgt_ft.SetField('type', tgt_type)
            tgt_ft.SetField('id', i)
            tgt_ft.SetField('x', s.x)
            tgt_ft.SetField('y', s.y)
            tgt_ly.CreateFeature(tgt_ft)
