#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/04/25 11:23:01

u"""
... Put description here ...
"""

import os
from collections import OrderedDict

from osgeo import ogr, osr

from _utils import ogr_utils

def read_coordinates(coord_src):
    coords = dict()
    
    for line in [l.strip() for l in open(coord_src).readlines()]:
        if line.startswith('p'):
            continue
        plot_id, x, y = [int(token) for token in line.split("\t")[:3]]
        coords[plot_id] = (x, y)
    else:
        return coords

if __name__ == '__main__':
    
    #plt_src = r"D:\work\ms.monina\wp5\wahner_heide\field\plot_ids_2011.txt"
    #coo_src_uh_2011 = r"D:\work\ms.monina\wp5\wahner_heide\field\koordinaten_ulli_2011.txt"
    #coo_src_df_2011 = r"D:\work\ms.monina\wp5\wahner_heide\field\koordinaten_dirk_2011.txt"

    veg_src_uh = r"D:\work\ms.monina\wp5\wahner_heide\field\wh_veg_final_uh_2011.txt"
    veg_src_df = r"D:\work\ms.monina\wp5\wahner_heide\field\wh_veg_final_df_2011.txt"
    
    tgt_dir = r"D:\tmp\veg"
    tgt_file = "wh_plots_2011.shp"
    tgt_path = os.path.join(tgt_dir, tgt_file)
    
    tgt_sr = osr.SpatialReference()
    tgt_sr.SetWellKnownGeogCS('WGS84')
    tgt_sr.SetUTM(32)

    record = OrderedDict()
    record['plot_id'] = 0
    record['editor'] = ""
    record['x'] = 0.0
    record['y'] = 0.0
    
    ds, ly = ogr_utils.create_shapefile(tgt_path, ogr.wkbPoint, tgt_sr)
    ogr_utils.create_feature_definition_from_record(record, ly)
    
    coords_1 = read_coordinates(veg_src_uh)
    coords_2 = read_coordinates(veg_src_df)

    for c in sorted(coords_1):
        x, y = coords_1[c]
        print "%d\t%d\t%d" % (c, coords_1[c][0], coords_1[c][1])
        pnt_gm = ogr.Geometry(ogr.wkbPoint)
        pnt_gm.SetPoint_2D(0, x, y)
        pnt_ft = ogr.Feature(ly.GetLayerDefn())
        pnt_ft.SetGeometry(pnt_gm)
        pnt_ft.SetField('plot_id', c)
        pnt_ft.SetField('editor', 'uh')
        pnt_ft.SetField('x', x)
        pnt_ft.SetField('y', y)
        ly.CreateFeature(pnt_ft)
    
    for c in sorted(coords_2):
        x, y = coords_2[c]
        print "%d\t%d\t%d" % (c, coords_2[c][0], coords_2[c][1])
        pnt_gm = ogr.Geometry(ogr.wkbPoint)
        pnt_gm.SetPoint_2D(0, x, y)
        pnt_ft = ogr.Feature(ly.GetLayerDefn())
        pnt_ft.SetGeometry(pnt_gm)
        pnt_ft.SetField('plot_id', c)
        pnt_ft.SetField('editor', 'df')
        pnt_ft.SetField('x', x)
        pnt_ft.SetField('y', y)
        ly.CreateFeature(pnt_ft)
    
    