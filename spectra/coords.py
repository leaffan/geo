#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/10/01 11:52:59

u"""
... Put description here ...
"""

import re


from types import TupleType, ListType
from osgeo import ogr

def collect_coordinates(shp_src, id_field):
    ds = ogr.Open(shp_src)
    ly = ds.GetLayer(0)
    
    coordinates = dict()
    
    for ft in ly:
        plot_id_as_str = ft.GetFieldAsString(id_field)
        gm = ft.GetGeometryRef()
        
        try:
            plot_id = int(plot_id_as_str)
        except:
            plot_id = None
        
        if plot_id is None:
            try:
                plot_id = int(re.search("\d+", plot_id_as_str).group(0))
            except:
                print "Couldn't convert plot id to a numeric value"
        
        coordinates[plot_id] = (plot_id_as_str, gm.GetX(), gm.GetY())

    return coordinates


if __name__ == '__main__':
    
    src_1 = r"D:\work\ms.monina\wp5\wahner_heide\field\shp\wh_102plots_df_2011.shp"
    id_field_1 = "punkt"
    t_1 = "df_2011"

    src_2 = r"D:\work\ms.monina\wp5\wahner_heide\field\shp\wh_195plots_doku_2009.shp"
    id_field_2 = "plot"
    t_2 = "doku_2009"

    src_3 = r"D:\work\ms.monina\wp5\wahner_heide\shp\wh_plots_2009.shp"
    id_field_3 = "plot_id"
    t_3 = "all_2009"
    
    src_4 = r"D:\work\ms.monina\wp5\wahner_heide\shp\wh_plots_2011.shp"
    id_field_4 = "plot_id"
    t_4 = "all_2011"

    plot_coordinates_1 = collect_coordinates(src_1, id_field_1)
    plot_coordinates_2 = collect_coordinates(src_2, id_field_2)
    plot_coordinates_3 = collect_coordinates(src_3, id_field_3)
    plot_coordinates_4 = collect_coordinates(src_4, id_field_4)

    all_plots = list(set(plot_coordinates_4.keys() + plot_coordinates_2.keys() + plot_coordinates_1.keys() + plot_coordinates_3.keys()))

    for plot in sorted(all_plots):
        print "%d\t" % plot,
        if plot_coordinates_1.has_key(plot):
            x, y = plot_coordinates_1[plot][1:]
            print "%.4f\t%.4f\t" % (x, y),
        else:
            print "0\t0\t",
        if plot_coordinates_2.has_key(plot):
            x, y = plot_coordinates_2[plot][1:]
            print "%.4f\t%.4f\t" % (x, y),
        else:
            print "0\t0\t",
        if plot_coordinates_3.has_key(plot):
            x, y = plot_coordinates_3[plot][1:]
            print "%.4f\t%.4f\t" % (x, y),
        else:
            print "0\t0\t",
        if plot_coordinates_4.has_key(plot):
            x, y = plot_coordinates_4[plot][1:]
            print "%.4f\t%.4f\t" % (x, y),
        else:
            print "0\t0\t",
        print

    #for plot in sorted(plot_coordinates):
    #    print "%d\t" % plot,
    #    for v in plot_coordinates[plot]:
    #        print "%.4f\t%.4f\t" % (v[1], v[2]),
    #    print
    
    #ds = ogr.Open(src)
    #ly = ds.GetLayer(0)
    #
    #plot_coordinates = dict()
    #
    #for ft in ly:
    #    plot_id_as_str = ft.GetFieldAsString(id_field)
    #    gm = ft.GetGeometryRef()
    #    
    #    try:
    #        plot_id = int(plot_id_as_str)
    #    except:
    #        plot_id = None
    #    
    #    if plot_id is None:
    #        try:
    #            plot_id = int(re.search("\d+", plot_id_as_str).group(0))
    #        except:
    #            print "Couldn't convert plot id to a numeric value"
    #    
    #    if plot_coordinates.has_key(plot_id):
    #        if type(plot_coordinates[plot_id]) is TupleType:
    #            new_value = list()
    #            new_value.append(plot_coordinates[plot_id])
    #            plot_coordinates[plot_id] = new_value
    #        plot_coordinates[plot_id].append(((plot_id_as_str, gm.GetX(), gm.GetY())))
    #    else:
    #        plot_coordinates[plot_id] = (plot_id_as_str, gm.GetX(), gm.GetY())
    #
    #for plot in sorted(plot_coordinates):
    #    print plot, plot_coordinates[plot]
    #