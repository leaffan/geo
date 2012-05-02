#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/05/02 14:09:58

u"""
... Put description here ...
"""

import os
import csv

from collections import OrderedDict
from osgeo import ogr, osr

from _utils import ogr_utils

if __name__ == '__main__':
    
    hnv_src = r"D:\tmp\veg\NordOst_071211_HNV_fuer naechste Phase.csv"
    
    tgt_dir = r"d:\tmp\veg"
    tgt_shp = r"hnv.shp"
    
    sr = osr.SpatialReference()
    sr.SetWellKnownGeogCS("WGS84")
    sr.SetUTM(33)
    
    tgt_path = os.path.join(tgt_dir, tgt_shp)
    
    tgt_ds, tgt_ly = ogr_utils.create_shapefile(tgt_path, ogr.wkbPoint, sr)
    
    
    
    csv_reader = csv.DictReader(open(hnv_src, 'rb'), delimiter = ";")
    
    
    
    
    record = csv_reader.next()

    rec = OrderedDict()
    for fn in csv_reader.fieldnames:
        rec[fn] = record[fn]
    
    ogr_utils.create_feature_definition_from_record(rec, tgt_ly)
    
    for row in csv_reader:
        
        x = int(row['X_UTM33'])
        y = int(row['Y_UTM33'])
        
        ft = ogr.Feature(tgt_ly.GetLayerDefn())
        
        gm = ogr.Geometry(type = ogr.wkbPoint)
        gm.AddPoint_2D(float(x), float(y))
        
        ft.SetGeometry(gm)

        for i in range(0, len(csv_reader.fieldnames)):
            print ft.GetDefnRef().GetFieldDefn(i).GetName(), 
            print csv_reader.fieldnames[i], row[csv_reader.fieldnames[i]]
            #ft.SetField(i, row[csv_reader.fieldnames[i]])


        tgt_ly.CreateFeature(ft)      
        
        
        