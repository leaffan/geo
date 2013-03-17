#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2013/01/16 11:34:27

u"""
... Put description here ...
"""

from osgeo import ogr

import numpy as np

src_shp = r"D:\work\ms.monina\wp5\kalmthoutse_heide\field\kalmthoutse_heide_releve_plots_wo_forest_hab_types.shp"
src_dat = r"D:\dev\r\monina\kalmthoutse_heide\data\kh_vegetation_orig.txt"

data = np.genfromtxt(src_dat, usecols = (0,1), dtype = '|S4,|S4', delimiter = "\t", names = True)
data_dict = dict()

for d in data:
    data_dict[int(d[0])] = d[1]

ds = ogr.Open(src_shp, True)
ly = ds.GetLayer(0)

idx = ly.GetLayerDefn().GetFieldIndex('plot_id')

for ft in ly:
    plot_id = ft.GetField(idx)
    print plot_id, data_dict[plot_id]
    ft.SetField("hab_type", data_dict[plot_id])
    ly.SetFeature(ft)
