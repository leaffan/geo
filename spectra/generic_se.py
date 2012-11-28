#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: spectra_extractor.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/11/27 13:36:36

u"""
... Put description here ...
"""

import os
import sys

import numpy as np
from numpy import ma

from osgeo import gdal, ogr

from _utils import gdal_utils, ogr_utils, geom_utils, general_utils

class SpectraExtractor(object):
    
    def __init__(self, img_src, roi_src, tgt_dir):
        if os.path.isdir(img_src):
            self.img_src_dir = img_src
            self.img_src = None
        elif os.path.isfile(img_src):
            self.img_src = img_src
            self.img_src_dir = None
        else:
            print "Couldn't find specified source image or directory..."
            sys.exit()

        # setting target directory
        self.tgt_dir = tgt_dir

        # setting roi source and setting roi type
        self.roi_src = roi_src
        self.roi_type = ogr_utils.get_geom_type(self.roi_src, False).lower()
        if not self.roi_type in ['polygon', 'point', 'line string']:
            print "Geometry type '%s' not recognized. Only polygon, point and line string are supported..." % self.roi_type
            sys.exit()

        # setting context type to square by default
        self.set_context_type()
        # setting context range to 1 by default
        self.set_context_range()
        # turning off calibration by default
        self.set_calibration()

        self.spectra = list()
        self.extract_locations = list()

    def set_calibration(self, slope = 1, intercept = 0):
        u"""
        Set up linear scaling parameters for the spectra to be extracted,
        i.e. to convert from stored digital numbers to real reflectance values
        between 0 and 1.
        """
        self.slope = slope
        self.intercept = intercept

    def set_context_range(self, context_range = 1):
        u"""
        Set spatial context for extraction of point spectra. Depending on the
        selection of either a square or a circle neighborhood, context is given
        in pixel (square) or real-world (circle) units.
        """
        self.context_range = context_range

    def set_context_type(self, context_type = 'square'):
        u"""
        Set context type for extraction of point spectra. Can be either square -
        a nxn-neighborhood is used for the spectrum - or circle - a circle with
        radius n is used. The variable of n can be adjusted by setting the con-
        text range.
        """
        self.context_type = context_type

    def retrieve_image_data(self, img_fmt_types = []):
        u"""
        
        """
        self.image_data = dict()
        if self.img_src_dir is None and self.img_src:
            self.image_data[0] = self.img_src
        else:
            image_data_files = [f for f in glob.glob(os.path.join(self.img_src_dir, "*.*")) if os.path.splitext(f)[-1] in img_fmt_types]
            for f in image_data_files:
                img_id = int(re.search("_(\d)_?", os.path.basename(f)).group(1))
                self.image_data[img_id] = f
    
    def convert_vector_to_raster(self, img_src):
        u"""
        Base method to convert region of interest geometry data to pixel
        coordinates, i.e. rows and colummns of an image.
        """
        if self.roi_type == 'polygon':
            self.img_coordinates = self.rasterize_polygon_rois(img_src)
        elif self.roi_type == 'line string':
            self.img_coordinates = self.rasterize_line_rois(img_src)
        elif self.roi_type == 'point':
            self.img_coordinates = self.rasterize_point_rois(img_src, 'square', 5)

    def rasterize_point_rois(self, img_src, type = 'square', context = 1):
        u"""
        Convert points of interests from vector coordinates to pixel coordinates
        in the specified source image.
        """
        # retrieving necessary information from template image
        img_ds = gdal.Open(img_src)
        img_geo_transform = img_ds.GetGeoTransform()

        # opening vector layer to be rasterized
        roi_ds = ogr.Open(self.roi_src)
        roi_ly = roi_ds.GetLayer(0)

        img_coordinates = dict()

        for ft in roi_ly:
            fid = ft.GetFID()
            gm = ft.GetGeometryRef()
            
            if type == 'square':
                if context == 1:
                    col, row = gdal_utils.get_pixel_coordinates(img_geo_transform, gm.GetX(), gm.GetY())
                    img_coordinates[fid] = (col, row)
                else:
                    (c_lb, c_ub), (r_lb, r_ub) = gdal_utils.get_neighborhood(img_geo_transform, gm.GetX(), gm.GetY(), context)
                    img_coordinates[fid] = ((c_lb, c_ub), (r_lb, r_ub))
            elif type == 'circle':
                circle_pixels = gdal_utils.get_circle(img_geo_transform, gm.GetX(), gm.GetY(), context)
                img_coordinates[fid] = circle_pixels
        
        return img_coordinates

    def rasterize_line_rois(self, img_src, output = False):
        u"""
        Convert lines of interests from vector coordinates to pixel coordinates
        in the specified source image.
        """
        # retrieving necessary information from template image
        tpl_ds = gdal.Open(img_src)
        tpl_geo_transform = tpl_ds.GetGeoTransform()
        tpl_x_size, tpl_y_size = tpl_ds.RasterXSize, tpl_ds.RasterYSize

        # opening vector layer to be rasterized
        roi_ds = ogr.Open(self.roi_src)
        roi_ly = roi_ds.GetLayer(0)

        if output:
            mem_ds = gdal.GetDriverByName('MEM').Create("", tpl_x_size, tpl_y_size, 1, gdal.GDT_Byte)
            mem_ds.SetGeoTransform(tpl_geo_transform)
            mem_ds.SetProjection(roi_ly.GetSpatialRef().ExportToWkt())
            mem_data = mem_ds.GetRasterBand(1).ReadAsArray()
        
        img_coordinates = dict()
        
        for ft in roi_ly:
            fid = ft.GetFID()
            print "Working on FID %d..." % fid
            gm = ft.GetGeometryRef()
            vertices = gm.GetPoints()
            
            pixels = list()
            
            for i in range(0, len(vertices) - 2):
                # retrieving real world coordinates of sub-line endpoints
                x0, y0 = vertices[i]
                x1, y1 = vertices[i + 1]
                
                # converting real-world coordinates to image coordinates
                c0 = int((x0 - tpl_geo_transform[0]) / tpl_geo_transform[1])
                r0 = int((y0 - tpl_geo_transform[3]) / tpl_geo_transform[5])
                c1 = int((x1 - tpl_geo_transform[0]) / tpl_geo_transform[1])
                r1 = int((y1 - tpl_geo_transform[3]) / tpl_geo_transform[5])
            
                # finding sequential pixels between current vertices
                pixels += geom_utils.retrieve_line_pixels(c0, r0, c1, r1)
            # finally eliminating duplicate pixels
            else:
                pixels = general_utils.ordered_set(pixels)
            
            if output:
                for col, row in pixels:
                    mem_data[row, col] = 255

            img_coordinates[fid] = pixels

        if output:
            gdal_utils.export_data(mem_data, r"z:\mem_out_bresenham.img", tpl_ds)
        
        return pixels

    def rasterize_polygon_rois(self, img_src):
        u"""
        Convert polygons of interests from vector coordinates to pixel
        coordinates in the specified source image.
        """
        # declaring source imagery as template raster data set
        tpl_ds = gdal.Open(img_src)
        tpl_geo_transform = tpl_ds.GetGeoTransform()
        tpl_x_size, tpl_y_size = tpl_ds.RasterXSize, tpl_ds.RasterYSize
    
        # opening vector roi data source
        roi_ds = ogr.Open(self.roi_src)
        roi_ly = roi_ds.GetLayer(0)
        
        img_coordinates = dict()
        
        for ft in roi_ly:
            fid = ft.GetFID()
            print "Working on FID %d..." % fid
            mem_ds = gdal.GetDriverByName('MEM').Create("", tpl_x_size, tpl_y_size, 1, gdal.GDT_Byte)
            mem_ds.SetGeoTransform(tpl_geo_transform)
            mem_ds.SetProjection(roi_ly.GetSpatialRef().ExportToWkt())
    
            where_clause = "WHERE '%s' = %i" % ('FID', fid)   
            query = "SELECT * FROM '%s' %s" % (roi_ly.GetName(), where_clause)
            tmp_ds = ogr.Open(self.roi_src)
            sel_ly = tmp_ds.ExecuteSQL(query)
    
            gdal.RasterizeLayer(mem_ds, (1,), sel_ly, burn_values = (255,))
            mem_data = mem_ds.GetRasterBand(1).ReadAsArray()
    
            mask = ma.masked_where(mem_data != 255, mem_data)
    
            pixels = list()
    
            # reversing image shape to make it column-major
            shape = list(mask.shape)
            shape.reverse()
    
            non_mask_indices = ma.flatnotmasked_contiguous(mask)
            # iterating over each slice
            for sl in non_mask_indices:
                start_pixel = np.unravel_index(sl.start, tuple(shape), order = 'F')
                stop_pixel = np.unravel_index(sl.stop, tuple(shape), order = 'F')
                #print sl, np.unravel_index(sl.start, mask.shape), np.unravel_index(sl.stop, mask.shape)
                pixels.append((start_pixel, stop_pixel))
            else:
                img_coordinates[fid] = pixels
    
        return img_coordinates
    
if __name__ == '__main__':
    
    img_src = r"D:\work\ms.monina\wp5\doeberitzer_heide\2008-08-07_hymap\orig\2008-08-07_hymap_doeberitzer_heide_1_orig.img"
    vct_src = r"Z:\fabi\msave\_wet.shp"
    #vct_src = r"Z:\fabi\msave\_line_test.shp"
    #vct_src = r"D:\work\ms.monina\wp5\doeberitzer_heide\field\doeberitzer_heide_releve_plots.shp"
    
    se = SpectraExtractor(img_src, vct_src, r"Z:\spectra")
    se.retrieve_image_data()
    
    se.convert_vector_to_raster(se.image_data[0])
    
    print se.img_coordinates