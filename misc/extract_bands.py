#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/10/13 11:06:29

u"""
... Put description here ...
"""

import os
import numpy as np
from osgeo import gdal

from _utils import gdal_utils

from metadata_builder import MetadataBuilder


if __name__ == '__main__':
    
    img_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\mos\2007-07-02_ahs_kalmthoutse_heide_mosaic.img"
    img_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\mos\2011-09-14_apex_wahner_heide_mosaic.img"
    bad_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\_info\2007-07-02_ahs_bad_bands.txt"
    bad_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_info\2011-09-14_apex_bad_bands.txt"
    
    tgt_path, ext = os.path.splitext(img_src)
    
    if ext == '.dat':
        ext = '.img'
    
    tgt_path = tgt_path + "_good_bands_only" + ext
    
    ds = gdal.Open(img_src)
    height = ds.RasterYSize
    width = ds.RasterXSize
    tgt_type = ds.GetRasterBand(1).DataType
    src_gtf = ds.GetGeoTransform()
    src_prj = ds.GetProjection()
    
    band_count = gdal_utils.get_band_count(img_src)
    bad_bands = [int(b) for b in open(bad_src).readlines()[1].split("\t")]
    bad_bands = np.loadtxt(bad_src)
    good_bands = list(set(range(1, band_count + 1)).difference(bad_bands))
    
    print "Creating target dataset '%s'..." % tgt_path
    
    drv = gdal.GetDriverByName('ENVI')
    drv.Create(tgt_path, width, height, len(good_bands), tgt_type)

    tgt_ds = gdal.Open(tgt_path, 1)
    tgt_ds.SetGeoTransform(src_gtf)
    tgt_ds.SetProjection(src_prj)

    print "Extracting good bands..."

    for i in range(0, len(good_bands)):
        print "\t+ Copying source band %d (will become target band %d)..." % (good_bands[i], i + 1)
        src_bd = ds.GetRasterBand(good_bands[i])
        tgt_bd = tgt_ds.GetRasterBand(i + 1)
        tgt_bd.Fill(src_bd.GetNoDataValue())
        tgt_bd.WriteRaster(0, 0, width, height, src_bd.ReadRaster(0, 0, width, height))
        tgt_bd.SetDescription("")
    
    tgt_ds = None
    
    mdb = MetadataBuilder(tgt_path)
    mdb.build_statistics('min', verbose = True)
    mdb.build_overviews(verbose = True)
    mdb.flush_metadata()
