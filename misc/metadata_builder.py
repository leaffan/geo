#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/06/20 02:07:18

u"""
... Put description here ...
"""

import os
import sys

from types import *

from lxml import etree
from osgeo import gdal

def ownprogress(a, b, c):
    pass
    #print a, c

class MetadataBuilder():

    BUCKET_COUNT = 256
    try:
        INF = float('inf')
    except:
        INF = 1e400
    
    def __init__(self, src_img):
        gdal.SetConfigOption("GDAL_PAM_ENABLED", "YES")
        gdal.SetConfigOption("ESRI_XML_PAM", "YES")
        
        if not os.path.isfile(src_img):
            print "Couldn't find source image '%s'..." % src_img
            sys.exit()
        
        self.src_img = src_img
        self.src_ds = gdal.Open(self.src_img)
        self.raster_count = self.src_ds.RasterCount

    def flush_metadata(self):
        self.src_ds = None
        self.src_ds = gdal.Open(self.src_img)

    #def set_statistics(self, no_data_value = ''):
    #    raster_count = self.src_ds.RasterCount
    #    
    #    for i in range(0, raster_count):
    #        print "Calculating statistics for band %d of %d..." % (i + 1, raster_count)
    #        bd = self.src_ds.GetRasterBand(i + 1)
    #        bd.SetNoDataValue(-1000)
    #        curr_stats = bd.ComputeStatistics(False)
    #        print curr_stats
    #        bd.SetNoDataValue(curr_stats[0])
    #        new_stats = bd.ComputeStatistics(False)
    #        print new_stats
    #        bd.GetHistogram(new_stats[0], new_stats[1], self.BUCKET_COUNT, False, False)

    def build_statistics(self, no_data_value = '', verbose = False):
        
        if verbose:
            print "Building statistics..."
        
        no_data_value = self.consolidate_no_data_value(no_data_value)
        
        if verbose:
            if not no_data_value and type(no_data_value) is StringType:
                print "\t+ A no data value has not been specified..."
            else:
                print "\t+ No data value:",
                if type(no_data_value) is StringType:
                     print "'%s'" % no_data_value
                else:
                    print "%f" % float(no_data_value)

        if no_data_value and no_data_value in ['min', 'max']:
            no_data_value = self.confirm_no_data_value(no_data_value)

        for i in range(0, self.raster_count):
            print "\t+ Working on band %d of %d..." % (i + 1, self.raster_count)
            bd = self.src_ds.GetRasterBand(i + 1)
            if no_data_value == '':
                bd.SetNoDataValue(self.INF)
            else:
                bd.SetNoDataValue(no_data_value)
            #if no_data_value == 'min':
            #    bd.SetNoDataValue(stats[0])
            #elif no_data_value == 'max':
            #    bd.SetNoDataValue(stats[1])
            #else:
            #    bd.SetNoDataValue(no_data_value)
            stats = bd.ComputeStatistics(False)
            bd.GetHistogram(stats[0], stats[1], self.BUCKET_COUNT, False, False)

    def build_overviews(self, ovr_type = 'NEAREST', ovr_levels = [2, 4, 6, 8, 10], verbose = False):
        if verbose:
            print "Building overviews..."
        self.src_ds.BuildOverviews(resampling = ovr_type, overviewlist = ovr_levels, callback = ownprogress, callback_data = self.src_ds.RasterCount)

    def confirm_no_data_value(self, type):
        test_bd = self.src_ds.GetRasterBand(1)
        stats = test_bd.ComputeStatistics(False)
        ndv = 0.0
        if type == 'min':
            ndv = stats[0]
        elif type == 'max':
            ndv = stats[1]
        return ndv

    def consolidate_no_data_value(self, no_data_value):
        # checking whether no data value was specified as either the minimum or
        # maximum data value
        if type(no_data_value) is StringType:
            if no_data_value.lower() in ['min', 'max']:
                no_data_value = no_data_value.lower()
            # unsetting no data value otherwise
            else:
                no_data_value = ''
        # checking whether specified no data value is a number
        elif type(no_data_value) in [IntType, FloatType]:
            pass
        else:
            no_data_value = ''

        return no_data_value

    #def set_no_data_value(self, no_data_values = 0):
    #    raster_count = self.src_ds.RasterCount
    #    
    #    if raster_count > 1:
    #        if not type(no_data_values) is ListType:
    #            no_data_values = [no_data_values] * raster_count
    #        else:
    #            if raster_count > len(no_data_values):
    #                no_data_values.extend([None] * (raster_count - len(no_data_values) + 1))
    #   
    #    for i in range(0, self.src_ds.RasterCount):
    #        ndv = no_data_values[i]
    #        if ndv is not None:
    #            bd = self.src_ds.GetRasterBand(i + 1)
    #            bd.SetNoDataValue(ndv)
    #            print "No data value for band %d: %s" % (i + 1, str(ndv))
    #
    #def build_metadata_xml(self):
    #    self.metadata = etree.SubElement(self.root, "Metadata")
    #    for i in range(0, self.src_ds.RasterCount):
    #        bd = self.src_ds.GetRasterBand(i + 1)
    #        etree.SubElement(self.metadata, "MDI", key = "Band_%d" % (i + 1)).text = bd.GetDescription()
    

if __name__ == '__main__':
    
    pass
    
    #src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\orig\2011-09-14_apex_wahner_heide_4_orig.img"
    #src = r"D:\geo_data\ms.monina\satellite_data\worldview\2011-08-02_wahner_heide\2011-08-11_worldview_ms_wahner_heide.tif"
    #src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\orig\2007-07-02_ahs_kalmthoutse_heide_2_orig.img"
    #src = r"D:\tmp\ahs_6_reduced.img"
    #src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex_final\orig\2011-09-14_apex_wahner_heide_1_coverage.img"
    #src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex_final\georef\2011-09-14_wahner_heide_4_ms_georef.img"
    #src = r"D:\work\ms.monina\wp5\doeberitzer_heide\2008-08-07_hymap\orig_3.img"
    #src = r"D:\work\ms.monina\wp5\wahner_heide\2009-08-06_hymap\work\2009-08-06_hymap_wahner_heide_mosaik_utm32.img"
    #src = r"Z:\tmp\mos\2009_wh_hy_envi_mos.img"
    #src = r"D:\work\ms.monina\wp5\wahner_heide\2009-08-06_hymap\georef\2009_08-06_hymap_wahner_heide_mos_first_envi.img"
    #
    #
    #
    #src_dir = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\ms"
    #
    #import os
    #import glob
    #
    #for src in glob.glob(os.path.join(src_dir, '*.img')):
    #    print src
    #    mdb = MetadataBuilder(src)
    #    mdb.set_statistics()
    #    mdb.flush_metadata()
    #
    #mdb = MetadataBuilder(src)
    #mdb.set_statistics()
    #mdb.flush_metadata()











    #ds = gdal.Open(src)
    #
    #bucket_count = 256
    #
    #root = etree.Element("PAMDataset")
    #metadata = etree.SubElement(root, "Metadata", domain = "IMAGE_STRUCTURE")
    #etree.SubElement(metadata, "MDI", key = "INTERLEAVE").text = "BAND"
    #metadata = etree.SubElement(root, "Metadata")
    #
    #for i in range(0, ds.RasterCount):
    #    bd = ds.GetRasterBand(i + 1)
    #    etree.SubElement(metadata, "MDI", key = "Band_%d" % (i + 1)).text = bd.GetDescription()
    #
    #for i in range(0, ds.RasterCount):
    #    print "Working on band %d of %d..." % (i + 1, ds.RasterCount)
    #    bd = ds.GetRasterBand(i + 1)
    #    bd_min, bd_max, bd_mean, bd_stddev = bd.ComputeStatistics(False)
    #    bd.SetNoDataValue(bd_min)
    #    bd_min, bd_max, bd_mean, bd_stddev = bd.ComputeStatistics(False)
    #    histogram = bd.GetHistogram(bd_min, bd_max, 256, 0, 0)
    #
    #    raster_band = etree.SubElement(root, "PAMRasterBand", band = str(i + 1))
    #    etree.SubElement(raster_band, "Description").text = bd.GetDescription()
    #    histograms = etree.SubElement(raster_band, "Histograms")
    #    hist_item = etree.SubElement(histograms, "HistItem")
    #    etree.SubElement(hist_item, "HistMin").text = str(bd_min)
    #    etree.SubElement(hist_item, "HistMax").text = str(bd_max)
    #    etree.SubElement(hist_item, "BucketCount").text = str(bucket_count)
    #    etree.SubElement(hist_item, "IncludeOutOufRange").text = str(0)
    #    etree.SubElement(hist_item, "Approximate").text = str(0)
    #    etree.SubElement(hist_item, "HistCount").text = "|".join(str(b) for b in histogram)
    #    
    #    bd_metadata = etree.SubElement(raster_band, "Metadata")
    #    etree.SubElement(bd_metadata, "MDI", key = "STATISTICS_MINIMUM").text = str(bd_min)
    #    etree.SubElement(bd_metadata, "MDI", key = "STATISTICS_MAXIMUM").text = str(bd_max)        
    #    etree.SubElement(bd_metadata, "MDI", key = "STATISTICS_MEAN").text = str(bd_mean)        
    #    etree.SubElement(bd_metadata, "MDI", key = "STATISTICS_STDDEV").text = str(bd_stddev)        
    #
    #print(etree.tostring(root, pretty_print = True))