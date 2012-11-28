#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/11/26 15:23:32

u"""
... Put description here ...
"""

import os

from osgeo import gdal, ogr

if __name__ == '__main__':
    
    tpl = r"D:\work\ms.monina\wp5\doeberitzer_heide\2008-08-07_hymap\orig\2008-08-07_hymap_doeberitzer_heide_1_orig.img"
    vct_src = r"Z:\fabi\msave\_wet.shp"
    vct_src = r"Z:\fabi\msave\_line_test.shp"

    tgt_dir = r"Z:\fabi\raster"

    true_value = 100
    false_value = 0
    no_data_value = -9999

    # retrieving output specifications from template raster data set
    tpl_ds = gdal.Open(tpl)
    tpl_geo_transform = tpl_ds.GetGeoTransform()
    tpl_x_size, tpl_y_size = tpl_ds.RasterXSize, tpl_ds.RasterYSize
    tpl_ds = None

    # opening vector base
    vct_ds = ogr.Open(vct_src)
    vct_ly = vct_ds.GetLayer(0)
    
    print "Template information:"
    print "\t Geographic transformation:", tpl_geo_transform
    print "\t Raster dimensionns: [%f, %f]" % (tpl_x_size, tpl_y_size)

    # preparing output files (GeoTiff + ArcInfo ASCII Grid)
    tif_name = "".join((vct_ly.GetName(), '.tif'))
    tif_path = os.path.join(tgt_dir, tif_name)
    asc_name = "".join((vct_ly.GetName(), '.asc'))
    asc_path = os.path.join(tgt_dir, asc_name)
    
    # preparing GeoTiff dataset, i.e. creating as well as
    # setting georeference and projection
    tif_ds = gdal.GetDriverByName('GTiff').Create(tif_path, tpl_x_size, tpl_y_size, 1, gdal.GDT_Byte)
    tif_ds.SetGeoTransform(tpl_geo_transform)
    tif_ds.SetProjection(vct_ly.GetSpatialRef().ExportToWkt())

    # rasterizing base layer to target dataset
    gdal.RasterizeLayer(tif_ds, (1,), vct_ly, burn_values = (255,))
    # rasterizing source vector layer to target dataset
    #gdal.RasterizeLayer(tif_ds, (1,), src_ly, burn_values = (255,))
        
    # computing band statistics
    tif_bd = tif_ds.GetRasterBand(1)
    tif_bd.ComputeStatistics(False)
        
    # exporting created GeoTiff to ArcInfo ASCII Grid format
    asc_ds = gdal.GetDriverByName('AAIGrid').CreateCopy(asc_path, tif_ds)
