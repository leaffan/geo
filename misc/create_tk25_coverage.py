#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/03/26 11:31:39

u"""
... Put description here ...
"""
from osgeo import ogr
from custom_coordinates import GeographicCoordinates, DMSCoordinate

def find_corners(ul, delta_lat, delta_lon):
    ur = GeographicCoordinates(ul.latitude, ul.longitude + delta_lon)
    ll = GeographicCoordinates(ul.latitude - delta_lat, ul.longitude)
    lr = GeographicCoordinates(ul.latitude - delta_lat, ul.longitude + delta_lon)
    
    return (ll, ul, lr, ur)

if __name__ == '__main__':

    from collections import OrderedDict
    from shapely.geometry import Point, Polygon, box
    from osgeo import ogr, osr
    from _utils import ogr_utils

    tgt_shp = r"d:\tmp\tk25_cov_final.shp"

    sr = osr.SpatialReference()
    sr.SetWellKnownGeogCS('WGS84')

    record = OrderedDict()
    record['id'] = ''
    record['name'] = ''
    record['lva'] = ''
    record['ll_lat'] = 0.0
    record['ll_lon'] = 0.0
    record['ur_lat'] = 0.0
    record['ur_lon'] = 0.0
    
    ds, ly = ogr_utils.create_shapefile(tgt_shp, ogr.wkbPolygon, sr)
    ogr_utils.create_feature_definition_from_record(record, ly)
    
    initial_corner = GeographicCoordinates(DMSCoordinate(56, 0, 0, 'N'), DMSCoordinate(5, 50, 0, 'E'))
    initial_lat = initial_corner.latitude
    initial_lon = initial_corner.longitude
    
    delta_lat = DMSCoordinate(0, 6)
    delta_lon = DMSCoordinate(0, 10)

    import sys
    #sys.exit()
    
    curr_lat = initial_lat
    curr_lon = initial_lon

    lat = initial_lat.convert_to_decimal()
    lon = initial_lon.convert_to_decimal()
    
    r = 0
    c = 1
    
    while lat > 47.:
        while lon < 16.:
            ul = GeographicCoordinates(curr_lat, curr_lon)
            #lr = (curr_lat, curr_lon)
            ll, ul, lr, ur = find_corners(ul, delta_lat, delta_lon)
            py = box(ll.longitude.convert_to_decimal(), ll.latitude.convert_to_decimal(),
                     ur.longitude.convert_to_decimal(), ur.latitude.convert_to_decimal())
            ring = ogr.Geometry(type = ogr.wkbLinearRing)
            for cp in py.exterior.coords:
                ring.AddPoint_2D(cp[0], cp[1])
            else:
                gm = ogr.Geometry(type = ogr.wkbPolygon)
                gm.AddGeometry(ring)
                gm.CloseRings()
            ft = ogr.Feature(ly.GetLayerDefn())
            ft.SetField('id', "%02d%02d" % (r, c))
            ft.SetField('ll_lat', float(ll.latitude.convert_to_decimal()))
            ft.SetField('ll_lon', float(ll.longitude.convert_to_decimal()))
            ft.SetField('ur_lat', float(ur.latitude.convert_to_decimal()))
            ft.SetField('ur_lon', float(ur.longitude.convert_to_decimal()))
            ft.SetGeometry(gm)
            ly.CreateFeature(ft)
            
            print "%02d%02d %s %s" % (r, c, ul, lr)

            curr_lon += delta_lon
            lon = curr_lon.convert_to_decimal()
            c += 1
        else:
            curr_lon = initial_lon
            lon = curr_lon.convert_to_decimal()
            c = 1
        curr_lat -= delta_lat
        lat = curr_lat.convert_to_decimal()
        r += 1
