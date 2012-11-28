#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/10/19 11:14:03

u"""
... Put description here ...
"""
import os
import glob

from osgeo import gdal

if __name__ == '__main__':
    
    src_dir = r"D:\work\ms.monina\wp4\maxent\_projection_data"
    tgt_dir = r"D:\work\ms.monina\wp4\maxent\_projection_data_no_data"
    src_dir = r"z:\prj_test"
    tgt_dir = r"z:\prj_test_no_data"
    
    data = glob.glob(os.path.join(src_dir, "*.bil"))

    empty_data = list()

    for f in data:
        print f
        ds = gdal.Open(f)
        bd = ds.GetRasterBand(1)
        mn, mx, mean, std_dev = bd.GetStatistics(0, 1)
        if mn == mx:
            empty_data.append(f)
            print f
        ds = None
    else:
        print len(data)
        print len(empty_data)

    for f in empty_data:
        tgt_path = os.path.join(tgt_dir, os.path.basename(f))
        ds = gdal.Open(f)
        drv = ds.GetDriver()
        ds = None
        drv.CopyFiles(tgt_path, f)
        drv.Delete(f)
