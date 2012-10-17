#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/10/05 11:46:01

u"""
... Put description here ...
"""

from osgeo import gdal, osr

if __name__ == '__main__':
    
    src_img = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\reduced\1.dat"
    src_img = r"z:\mos\1_sub.dat"
    
    tgt_ps = 4.0
    
    src_ds = gdal.Open(src_img)
    src_prj = src_ds.GetProjection()
    src_srs = osr.SpatialReference()
    src_srs.ImportFromWkt(src_prj)
    src_gtf = src_ds.GetGeoTransform()
    src_width = src_ds.RasterXSize
    src_height = src_ds.RasterYSize
    src_nbands = src_ds.RasterCount

    tgt_gtf = (src_gtf[0], tgt_ps, 0.0, src_gtf[3], 0.0, - tgt_ps)
    
    tgt_srs = osr.SpatialReference()
    tgt_srs.SetWellKnownGeogCS("WGS84")
    tgt_srs.SetUTM(31)
    
    tx = osr.CoordinateTransformation(src_srs, tgt_srs)
    
    (ulx, uly, ulz) = tx.TransformPoint(src_gtf[0], tgt_gtf[3])
    (lrx, lry, lrz) = tx.TransformPoint(src_gtf[0] + src_gtf[1] * src_width, \
                                        src_gtf[3] + src_gtf[5] * src_height)

    tgt_gtf = (ulx, tgt_ps, src_gtf[2], uly, src_gtf[4], - tgt_ps)
    tgt_width = int((lrx - ulx) / tgt_ps)
    tgt_height = int((uly - lry) / tgt_ps)

    tgt_path = r"z:\mos\1_sub_utm31.img"
    
    #print tgt_prj.ExportToWkt()
    
    #import sys
    #sys.exit()
    
    tgt_ds = gdal.GetDriverByName('ENVI').Create(tgt_path, tgt_width, tgt_height, src_nbands, gdal.GDT_Float32)
    tgt_ds.SetGeoTransform(tgt_gtf)
    tgt_ds.SetProjection(tgt_srs.ExportToWkt())
    
    gdal.ReprojectImage(src_ds, tgt_ds, src_prj, tgt_srs.ExportToWkt(), gdal.GRA_Bilinear, 0.0, 0.0, gdal.TermProgress_nocb)
    