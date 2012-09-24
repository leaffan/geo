#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/09/04 14:39:47

u"""
... Put description here ...
"""

from osgeo import gdal

def own_progress(a, b, c):
    if a >= 1.:
        print "'%f' - '%s' - '%s'" % (a, b, c)


if __name__ == '__main__':
    
    src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\ms\2011-09-14_apex_wahner_heide_3_ms.img"
    
    ds = gdal.Open(src)
    
    ds.BuildOverviews(overviewlist = [2, 4, 6, 8, 10], callback = own_progress, callback_data = "bla")
    
    
    