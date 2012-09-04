#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/06/29 13:53:25

u"""
... Put description here ...
"""

from osgeo import ogr

if __name__ == '__main__':
    
    src = r"D:\work\ms.monina\wp4\work\natura2000_mtb_intersect.shp"
    
    ds = ogr.Open(src)
    ly = ds.GetLayer(0)
    
    i = 16378
    output = list()
    
    for ft in ly:
        output.append("\t".join((str(i), ft.GetFieldAsString('sitecode'), ft.GetFieldAsString('id') + '0')))
        i += 1
    
    open(r"d:\map.txt", 'wb').write("\n".join(output))