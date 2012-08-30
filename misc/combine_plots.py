#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/08/24 13:06:28

u"""
... Put description here ...
"""
from __future__ import division

from osgeo import ogr

from _utils import ogr_utils

if __name__ == '__main__':
    
    shp_src = r"D:\work\ms.monina\wp5\doeberitzer_heide\field\doeberitzer_heide_plots.shp"
    txt_src = r"D:\work\ms.monina\wp5\doeberitzer_heide\field\doeberitzer_heide_releve_plots.txt"
    
    link_field = "LINK_ID"
    
    tgt_shp = r"D:\work\ms.monina\wp5\doeberitzer_heide\field\releve_plots_xxx.shp"
    
    
    
    plt_ds = ogr.Open(shp_src)
    plt_ly = plt_ds.GetLayer(0)
    plt_name = plt_ly.GetName()

    tgt_ds, tgt_ly = ogr_utils.create_shapefile(tgt_shp, ogr.wkbPoint, plt_ly.GetSpatialRef())
    tgt_rec = dict()
    tgt_rec['plot_id'] = ''
    tgt_rec['src_cnt'] = 0
    tgt_rec['x'] = 0.
    tgt_rec['y'] = 0.
    ogr_utils.create_feature_definition_from_record(tgt_rec, tgt_ly)

    releve_plot_ids = [l.strip() for l in open(txt_src).readlines()]
    
    i = 0
    
    for r_plot_id in releve_plot_ids:
        sel_ly = plt_ds.ExecuteSQL("SELECT * FROM %s WHERE %s LIKE '%s'" % (plt_name, link_field, r_plot_id))
        if sel_ly is None:
            continue
        ft_found = sel_ly.GetFeatureCount()
        if not ft_found:
            print r_plot_id
            continue
        i += 1
        if ft_found == 1:
            ft = sel_ly.GetNextFeature()
            gm = ft.GetGeometryRef()
            #print i, r_plot_id, ft_found, gm
            print "%s\t%f\t%f" % (r_plot_id, gm.GetX(), gm.GetY())
        elif ft_found > 1:
            x = list()
            y = list()
            for ft in sel_ly:
                gm = ft.GetGeometryRef()
                x.append(gm.GetX())
                y.append(gm.GetY())
            else:
                gm = ogr.Geometry(ogr.wkbPoint)
                gm.SetPoint_2D(0, sum(x) / len(x), sum(y) / len(y))
                #print i, r_plot_id, ft_found, gm
                print "%s\t%f\t%f" % (r_plot_id, gm.GetX(), gm.GetY())

        new_ft = ogr.Feature(tgt_ly.GetLayerDefn())
        new_ft.SetGeometry(gm)
        new_ft.SetField('plot_id', r_plot_id)
        new_ft.SetField('src_cnt', ft_found)
        new_ft.SetField('x', gm.GetX())
        new_ft.SetField('y', gm.GetY())
        tgt_ly.CreateFeature(new_ft)
