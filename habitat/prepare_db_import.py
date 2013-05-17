#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2013/04/03 01:04:58

u"""
... Put description here ...
"""

from osgeo import ogr


if __name__ == '__main__':
    
    shp_src = r"Z:\work\ms.monina\wp4\shp\blattschnitte\mtb_utm32_florkart_2012_coverage.shp"
    shp_src = r"Z:\work\ms.monina\wp4\shp\blattschnitte\quadranten_utm32.shp"
    
    ds = ogr.Open(shp_src)
    ly = ds.GetLayer(0)
    
    #print "\t".join(('mtb_id', 'name', 'lva', 'll_lat', 'll_lon', 'ur_lat', 'ur_lon'))
    print "\t".join(('quad_id', 'mtb_id'))
    
    for ft in ly:
        quad_id = ft.GetFieldAsString('QUADRANT')
        mtb_id = quad_id[:-1]
        #tile_id = ft.GetFieldAsString('id')
        #tile_name = ft.GetFieldAsString('name')
        #lva = ft.GetFieldAsString('lva')
        #ll_lat = ft.GetFieldAsDouble('ll_lat')
        #ll_lon = ft.GetFieldAsDouble('ll_lon')
        #ur_lat = ft.GetFieldAsDouble('ur_lat')
        #ur_lon = ft.GetFieldAsDouble('ur_lon')
        #print "\t".join((tile_id, tile_name, lva, str(ll_lat), str(ll_lon), str(ur_lat), str(ur_lon)))
        print "\t".join((quad_id, mtb_id))
