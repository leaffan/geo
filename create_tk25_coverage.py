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

import decimaldegrees as dd

def add_dms(orig, addendum):
    odd, omm, oss = orig
    add, amm, ass = addendum
    
    rss = oss + ass
    minute_add = 0
    while rss >= 60:
        rss = rss - 60
        minute_add += 1
    
    rmm = omm + amm + minute_add
    degree_add = 0
    while rmm >= 60:
        rmm = rmm - 60
        degree_add += 1
    
    rdd = odd + add + degree_add
    
    #print "%d° %d' %d'' + %d° %d' %d'' = %d° %d' %d''" % (odd, omm, oss, add, amm, ass, rdd, rmm, rss)

    return rdd, rmm, rss


def subtract_dms(orig, subtrahend):
    odd, omm, oss = orig
    sdd, smm, sss = subtrahend
    
    rss = oss - sss
    minute_substract = 0
    while rss < 0:
        rss = rss + 60
        minute_substract += 1
    
    rmm = omm - smm - minute_substract
    degree_subtract = 0
    while rmm < 0:
        rmm = rmm + 60
        degree_subtract += 1
    
    rdd = odd - sdd - degree_subtract
    
    #print "%d°%d'%d'' - %d°%d'%d'' = %d°%d'%d''" % (odd, omm, oss, sdd, smm, sss, rdd, rmm, rss)

    return rdd, rmm, rss

def find_corners(ll, delta_lat, delta_lon):
    
    ll_lat, ll_lon =  ll
    lr = (ll_lat, add_dms(ll_lon, delta_lon))
    ul = (add_dms(ll_lat, delta_lat), ll_lon)
    ur = (add_dms(ll_lat, delta_lat), add_dms(ll_lon, delta_lon))
    
    return ul, ll, ur, lr

if __name__ == '__main__':

    from shapely.geometry import Point, Polygon, box
    from osgeo import ogr, osr
    from _utils import ogr_utils

    tgt_shp = r"d:\tmp\tk25_cov.shp"

    sr = osr.SpatialReference()
    sr.SetWellKnownGeogCS('WGS84')

    record = dict()
    record['ul_lat'] = 0.0
    record['ul_lon'] = 0.0
    record['lr_lat'] = 0.0
    record['lr_lon'] = 0.0
    record['id'] = ""
    
    ds, ly = ogr_utils.create_shapefile(tgt_shp, ogr.wkbPolygon, sr)
    ogr_utils.create_feature_definition_from_record(record, ly)
    
    initial_corner = ((56, 0, 0), (5, 50, 0))
    initial_lat = initial_corner[0]
    initial_lon = initial_corner[1]
    
    delta_lon = (0, 10, 0)
    delta_lat = (0, 6, 0)
    

    #add_dms((56, 58, 57), (0, 66, 3))
    #subtract_dms((56, 0, 0), (13, 1, 0))
    
    print add_dms((5, 50, 0), delta_lon)
    
    import sys
    #sys.exit()
    
    curr_lat = initial_lat
    curr_lon = initial_lon
    
    lat = dd.dm2decimal(initial_lat[0], initial_lat[1])
    lon = dd.dm2decimal(initial_lon[0], initial_lon[1])
    r = -1
    c = 1
    print lat
    print lon
    
    while lat > 47.:
        while lon < 22.:
            ll = (curr_lat, curr_lon)
            #lr = (curr_lat, curr_lon)
            ul, ll, ur, lr = find_corners(ll, delta_lat, delta_lon)
            py = box(dd.dm2decimal(ll[1][0], ll[1][1]), dd.dm2decimal(ll[0][0], ll[0][1]), dd.dm2decimal(ur[1][0], ur[1][1]), dd.dm2decimal(ur[0][0], ur[0][1]))
            ring = ogr.Geometry(type = ogr.wkbLinearRing)
            for cp in py.exterior.coords:
                ring.AddPoint_2D(cp[0], cp[1])
            else:
                gm = ogr.Geometry(type = ogr.wkbPolygon)
                gm.AddGeometry(ring)
                gm.CloseRings()
            ft = ogr.Feature(ly.GetLayerDefn())
            ft.SetField('id', "%02d%02d" % (r, c))
            ft.SetField('ul_lat', float(dd.dm2decimal(ul[1][0], ul[1][1])))
            ft.SetField('ul_lon', float(dd.dm2decimal(ul[0][0], ul[0][1])))
            ft.SetField('lr_lat', float(dd.dm2decimal(lr[1][0], lr[1][1])))
            ft.SetField('lr_lon', float(dd.dm2decimal(lr[0][0], lr[0][1])))
            ft.SetGeometry(gm)
            ly.CreateFeature(ft)
            
            print "%02d%02d [%02d°%02d'/ %02d°%02d'] [%02d°%02d'/ %02d°%02d']" % (r, c, curr_lat[0], curr_lat[1], curr_lon[0], curr_lon[1], lr[0][0], lr[0][1], lr[1][0], lr[1][1])

            curr_lon = add_dms(curr_lon, delta_lon)
            lon = dd.dm2decimal(curr_lon[0], curr_lon[1])
            c += 1
        else:
            curr_lon = initial_lon
            lon = dd.dm2decimal(initial_lon[0], initial_lon[1])
            c = 1
        curr_lat = subtract_dms(curr_lat, delta_lat)
        lat = dd.dm2decimal(curr_lat[0], curr_lat[1])
        r += 1


        #curr_lat = subtract_dms(curr_lat, delta_lat)
        #lat = dd.dm2decimal(curr_lat[0], curr_lat[1])
        #r += 1
        #while lon < 15.:
        #    curr_lon = add_dms(curr_lon, delta_lon)
        #    lon = dd.dm2decimal(curr_lon[0], curr_lon[1])
        #    #print lon
        #    c += 1
        #    
        #    ul = (curr_lat, curr_lon)
        #    
        #    ul, ll, ur, lr = find_corners(ul, delta_lat, delta_lon)
        #    
        #    #print ul
        #    #print ll, dd.dm2decimal(ll[1][0], ll[1][1])
        #    #print ur, dd.dm2decimal(ur[1][0], ur[1][1])
        #    #print lr
        #    
        #    py = box(dd.dm2decimal(ll[1][0], ll[1][1]), dd.dm2decimal(ll[0][0], ll[0][1]), dd.dm2decimal(ur[1][0], ur[1][1]), dd.dm2decimal(ur[0][0], ur[0][1]))
        #    
        #    ring = ogr.Geometry(type = ogr.wkbLinearRing)
        #    
        #    for cp in py.exterior.coords:
        #        ring.AddPoint_2D(cp[0], cp[1])
        #    else:
        #        gm = ogr.Geometry(type = ogr.wkbPolygon)
        #        gm.AddGeometry(ring)
        #        gm.CloseRings()
        #    
        #    ft = ogr.Feature(ly.GetLayerDefn())
        #    ft.SetField('id', "%02d%02d" % (r, c))
        #    #print dd.dm2decimal(ul[1][0], ul[1][1])
        #    ft.SetField('ul_lat', float(dd.dm2decimal(ul[1][0], ul[1][1])))
        #    ft.SetField('ul_lon', float(dd.dm2decimal(ul[0][0], ul[0][1])))
        #    ft.SetField('lr_lat', float(dd.dm2decimal(lr[1][0], lr[1][1])))
        #    ft.SetField('lr_lon', float(dd.dm2decimal(lr[0][0], lr[0][1])))
        #    ft.SetGeometry(gm)
        #    ly.CreateFeature(ft)
        #    
        #    print "%02d%02d [%02d°%02d'/ %02d°%02d'] [%02d°%02d'/ %02d°%02d']" % (r, c, curr_lat[0], curr_lat[1], curr_lon[0], curr_lon[1], lr[0][0], lr[0][1], lr[1][0], lr[1][1])
        #else:
        #    curr_lon = initial_lon
        #    lon = dd.dm2decimal(initial_lon[0], initial_lon[1])
        #    c = 1
        #