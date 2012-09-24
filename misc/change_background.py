#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/09/21 11:35:35

u"""
... Put description here ...
"""
import sys
import os
import glob

from progressbar import *
from osgeo import gdal

def clear_background(src_img):
    ds = gdal.Open(src_img)
    r = ds.GetRasterBand(1).ReadAsArray()
    g = ds.GetRasterBand(2).ReadAsArray()
    b = ds.GetRasterBand(3).ReadAsArray()

    height = len(r)
    width = len(r[1])

    widgets = ['Percentage', ' ', Bar(), ' ', ETA()]

    pb = ProgressBar(widgets = widgets, maxval = height * width)

    maxval = height * width + width
    print maxval

    done = 0

    pb.start()
    for i in range(0, height):
        for j in range(0, width):
            rgb = (r[i, j], g[i, j], b[i, j])
            if min(rgb) >= 200 or rgb == (0,0,0):
                r[i, j] = g[i, j] = b[i, j] = 255
            done += 1
            pb.update(done)
            #if i % 500 == 0 and j % 500 == 0:
            #    print i, j
    pb.finish()
    
    return r, g, b

if __name__ == '__main__':
    
    src_dir = r"Z:\wh"
    tgt_dir = r"Z:\wh\clear"
    
    src_imagery = glob.glob(os.path.join(src_dir, '*.tif'))
    
    for src in src_imagery:
        print "Working on '%s'..." % src

        tgt = os.path.join(tgt_dir, "".join((os.path.splitext(os.path.basename(src))[0], '.img')))

        r, g, b = clear_background(src)
    
        drv = gdal.GetDriverByName('ENVI')
        drv.CreateCopy(tgt, gdal.Open(src))
        tgt_ds = gdal.Open(tgt, 1)
        tgt_bd = tgt_ds.GetRasterBand(1)
        tgt_bd.WriteArray(r, 0, 0)
        tgt_bd = tgt_ds.GetRasterBand(2)
        tgt_bd.WriteArray(g, 0, 0)
        tgt_bd = tgt_ds.GetRasterBand(3)
        tgt_bd.WriteArray(b, 0, 0)
