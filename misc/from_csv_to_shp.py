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
    
    hnv_src = r"D:\work\veggeo\msave\2012_fieldsheet_update\data\NordOst_071211_HNV_fuer naechste Phase.csv"
    hnv_src = r"D:\work\ms.monina\wp5\wahner_heide\field\plot_ids_coordinates_2009_refined.csv"
    
    tgt_dir = r"z:\create"
    tgt_shp = r"2009.shp"
    
    sr = osr.SpatialReference()
    sr.SetWellKnownGeogCS("WGS84")
    sr.SetUTM(32)
    
    tgt_path = os.path.join(tgt_dir, tgt_shp)

    if os.path.isfile(tgt_path):
        drv = ogr.GetDriverByName('ESRI Shapefile')
        drv.DeleteDataSource(tgt_path)
    
    tgt_ds, tgt_ly = ogr_utils.create_shapefile(tgt_path, ogr.wkbPoint, sr)
    
    csv_reader = csv.DictReader(open(hnv_src, 'rb'), delimiter = ";")
    record = csv_reader.next()

    rec = OrderedDict()
    for fn in csv_reader.fieldnames[:]:
        new_fn = fn.replace(".", "_")
        if unicode(record[fn]).isnumeric():
            if "." in record[fn]:
                val = float(record[fn])
            else:
                val = int(record[fn])
        else:
            val = record[fn]
        rec[new_fn] = val
    
    csv_reader = csv.DictReader(open(hnv_src, 'rb'), delimiter = ";")
    
    ogr_utils.create_feature_definition_from_record(rec, tgt_ly)
    
    for row in csv_reader:
        x = float(row['x'])
        y = float(row['y'])
        
        ft = ogr.Feature(tgt_ly.GetLayerDefn())
        
        gm = ogr.Geometry(type = ogr.wkbPoint)
        gm.AddPoint_2D(float(x), float(y))
        
        ft.SetGeometry(gm)

        for i in range(0, len(csv_reader.fieldnames)):
            print ft.GetDefnRef().GetFieldDefn(i).GetName(), ft.GetDefnRef().GetFieldDefn(i).GetTypeName()
        #    print csv_reader.fieldnames[i], row[csv_reader.fieldnames[i]]
            ft.SetField(i, row[csv_reader.fieldnames[i]])
        tgt_ly.CreateFeature(ft)      
        
