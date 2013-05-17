#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2013/05/10 01:11:57

u"""
... Put description here ...
"""

from osgeo import ogr

src = r"d:\tmp\carto_test.shp"

ds = ogr.Open(src)


conn = ogr.Open("PG: host=localhost dbname=gis user=gis password=sql")
for layer in conn:
    print layer.GetName()
    
drv = ogr.GetDriverByName('PostgreSQL')



db_ds = drv.CopyDataSource(ds, "PG: host=localhost dbname=gis user=gis password=sql")
db_ds = None

