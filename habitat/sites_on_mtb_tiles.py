#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2013/05/06 00:44:04

u"""
... Put description here ...
"""

from osgeo import ogr

src_shp = r"z:\work\ms.monina\wp4\work\natura2000_mtb_intersect.shp"
#src_shp = r"z:\work\ms.monina\wp4\work\natura2000_mtbq_intersect.shp"

ds = ogr.Open(src_shp)
ly = ds.GetLayer(0)

i = 0

print "\t".join(('site_map_id', 'site_id', 'mtb_id'))

for ft in ly:
    site_id = ft.GetFieldAsString('sitecode')
    mtb_id = ft.GetFieldAsString('id')
    print "%d\t%s\t%s" % (i, site_id, mtb_id)
    i += 1


