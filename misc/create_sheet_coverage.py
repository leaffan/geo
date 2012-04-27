#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: create_tk25_coverage.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/03/26 11:31:39

u"""
This script creates a sheet coverage dataset for the German topographical maps
of the scale 1:25000, i.e. Messtischblätter (TK25) or 1:10000 (TK10).
Each sheet of TK25 is 6' high and 10' wide, each sheet of TK10 is 3' high and
5' wide.
Starting from a point at 56° N and 5°50' E, each TK25 sheet is given a row
and a column number resulting in a unique identifier.
TK10 sheets are given the identifier of the containing TK25 sheet added by a
quadrant identifier running from 1 to 4. Renaming of TK10 sheets is implemented
in rename_tk10_tiles.py.
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

    # setting up target shape file
    tgt_shp = r"d:\tmp\tk10_cov_final.shp"
    # setting up target spatial reference
    sr = osr.SpatialReference()
    sr.SetWellKnownGeogCS('WGS84')

    # preparing attributes to be stored for each sheet tile
    record = OrderedDict()
    record['id'] = ''
    record['name'] = ''
    record['lva'] = ''
    record['ll_lat'] = 0.0
    record['ll_lon'] = 0.0
    record['ur_lat'] = 0.0
    record['ur_lon'] = 0.0
    
    # creating shape file
    ds, ly = ogr_utils.create_shapefile(tgt_shp, ogr.wkbPolygon, sr)
    ogr_utils.create_feature_definition_from_record(record, ly)
    
    # setting up initial corner
    initial_corner = GeographicCoordinates(DMSCoordinate(56, 0, 0, 'N'), DMSCoordinate(5, 50, 0, 'E'))
    initial_lat = initial_corner.latitude
    initial_lon = initial_corner.longitude
    
    # setting up sheet dimensions
    # TK25
    delta_lat = DMSCoordinate(0, 6)
    delta_lon = DMSCoordinate(0, 10)
    # TK10
    delta_lat = DMSCoordinate(0, 3)
    delta_lon = DMSCoordinate(0, 5)

    curr_lat = initial_lat
    curr_lon = initial_lon

    lat = initial_lat.convert_to_decimal()
    lon = initial_lon.convert_to_decimal()
    
    # setting up initial row and column identifiers
    r = 0
    c = 1
    
    while lat > 47.:
        while lon < 16.:
            # setting up upper left corner of the current sheet
            ul = GeographicCoordinates(curr_lat, curr_lon)
            # finding all corners of the current sheet
            ll, ul, lr, ur = find_corners(ul, delta_lat, delta_lon)
            # creating bounding box polygon
            py = box(ll.longitude.convert_to_decimal(), ll.latitude.convert_to_decimal(),
                     ur.longitude.convert_to_decimal(), ur.latitude.convert_to_decimal())
            # preparing polygon geometry for vector dataset
            ring = ogr.Geometry(type = ogr.wkbLinearRing)
            # creating polygon geometry
            for cp in py.exterior.coords:
                ring.AddPoint_2D(cp[0], cp[1])
            else:
                gm = ogr.Geometry(type = ogr.wkbPolygon)
                gm.AddGeometry(ring)
                gm.CloseRings()
            # creating feature for vector dataset
            ft = ogr.Feature(ly.GetLayerDefn())
            # setting feature attributes
            ft.SetField('id', "%02d%02d" % (r, c))
            ft.SetField('ll_lat', float(ll.latitude.convert_to_decimal()))
            ft.SetField('ll_lon', float(ll.longitude.convert_to_decimal()))
            ft.SetField('ur_lat', float(ur.latitude.convert_to_decimal()))
            ft.SetField('ur_lon', float(ur.longitude.convert_to_decimal()))
            # linking feature with created polygon geometry
            ft.SetGeometry(gm)
            # adding feature to target layer
            ly.CreateFeature(ft)
            
            print "%02d%02d %s %s" % (r, c, ul, lr)

            # updating current longitude and column number
            curr_lon += delta_lon
            lon = curr_lon.convert_to_decimal()
            c += 1
        else:
            # resetting longitude and column number at the end of the current row
            curr_lon = initial_lon
            lon = curr_lon.convert_to_decimal()
            c = 1
        # updating current latitude and row number
        curr_lat -= delta_lat
        lat = curr_lat.convert_to_decimal()
        r += 1
