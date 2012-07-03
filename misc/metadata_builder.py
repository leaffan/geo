#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/06/20 02:07:18

u"""
... Put description here ...
"""

from types import ListType

from lxml import etree
from osgeo import gdal

class MetadataBuilder():

    BUCKET_COUNT = 256
    
    def __init__(self, src_img):
        
        gdal.SetConfigOption("GDAL_PAM_ENABLED", "YES")
        gdal.SetConfigOption("ESRI_XML_PAM", "YES")
        
        self.src_img = src_img
        self.src_ds = gdal.Open(self.src_img)

    def flush_metadata(self):
        self.src_ds = None
        self.src_ds = gdal.Open(self.src_img)

    def set_statistics(self, no_data_value = ''):
        raster_count = self.src_ds.RasterCount
        
        for i in range(0, raster_count):
            print "Calculating statistics for band %d of %d..." % (i + 1, raster_count)
            bd = self.src_ds.GetRasterBand(i + 1)
            curr_stats = bd.GetStatistics(True, True)
            bd.SetNoDataValue(curr_stats[0])
            new_stats = bd.ComputeStatistics(False)
            bd.GetHistogram(new_stats[0], new_stats[1], self.BUCKET_COUNT, False, False)

    def set_no_data_value(self, no_data_values = 0):
        raster_count = self.src_ds.RasterCount
        
        if raster_count > 1:
            if not type(no_data_values) is ListType:
                no_data_values = [no_data_values] * raster_count
            else:
                if raster_count > len(no_data_values):
                    no_data_values.extend([None] * (raster_count - len(no_data_values) + 1))
       
        for i in range(0, self.src_ds.RasterCount):
            ndv = no_data_values[i]
            if ndv is not None:
                bd = self.src_ds.GetRasterBand(i + 1)
                bd.SetNoDataValue(ndv)
                print "No data value for band %d: %s" % (i + 1, str(ndv))

    def build_metadata_xml(self):
        self.metadata = etree.SubElement(self.root, "Metadata")
        for i in range(0, self.src_ds.RasterCount):
            bd = self.src_ds.GetRasterBand(i + 1)
            etree.SubElement(self.metadata, "MDI", key = "Band_%d" % (i + 1)).text = bd.GetDescription()
    

if __name__ == '__main__':
    
    src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\orig\2011-09-14_apex_wahner_heide_4_orig.img"
    src = r"D:\geo_data\ms.monina\satellite_data\worldview\2011-08-02_wahner_heide\2011-08-11_worldview_ms_wahner_heide.tif"
    src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\orig\2007-07-02_ahs_kalmthoutse_heide_2_orig.img"
    src = r"D:\tmp\ahs_6_reduced.img"

    mdb = MetadataBuilder(src)
    
    mdb.set_statistics()
    mdb.flush_metadata()

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