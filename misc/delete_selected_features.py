#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/12/18 15:19:03

u"""
... Put description here ...
"""

import numpy as np
from osgeo import ogr

from _utils import ogr_utils

if __name__ == '__main__':
    
    del_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\field\kh_forest_plots.txt"
    geo_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\field\kalmthoutse_heide_releve_plots.shp"
    
    geo_tgt = r"D:\work\ms.monina\wp5\kalmthoutse_heide\field\kalmthoutse_heide_releve_plots_wo_forest.shp"
    
    src_ds = ogr.Open(geo_src)
    src_ly = src_ds.GetLayer(0)
    src_sr = src_ly.GetSpatialRef()
    
    tgt_ds, tgt_ly = ogr_utils.create_shapefile(geo_tgt, ogr.wkbPoint, src_sr)
    ogr_utils.create_feature_definition_from_template(src_ly, tgt_ly)
    
    del_ft = [int(n) for n in np.loadtxt(del_src)]

    plot_idx = src_ly.GetLayerDefn().GetFieldIndex('plot_id')

    for ft in src_ly:
        src_id = ft.GetField(plot_idx)
        if src_id in del_ft:
            continue
        tgt_ly.CreateFeature(ft)
