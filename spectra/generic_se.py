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
import glob
import pickle
from operator import attrgetter

import numpy as np
from numpy import ma
from osgeo import gdal, ogr

from spectrum import Spectrum
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
        # turning of aggregation by default
        self.set_aggregation()

        self.spectra = list()
        self.extract_locations = list()
        
        self.verbosity = 1

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

    def set_aggregation(self, aggregate = False):
        u"""
        Toggle aggregation to allow for aggregating multiple spectra extractions
        by mean calculation. This is only valid if spectra of polygon regions of
        interests are considered.
        """
        self.aggregate = aggregate

    def retrieve_image_data(self, img_fmt_types = []):
        u"""
        
        """
        
        if not img_fmt_types:
            img_fmt_types.append(".img")
        
        self.image_data = dict()
        if self.img_src_dir is None and self.img_src:
            self.image_data[0] = self.img_src
        else:
            image_data_files = [f for f in glob.glob(os.path.join(self.img_src_dir, "*.*")) if os.path.splitext(f)[-1] in img_fmt_types]
            sorted(image_data_files)
            img_id = 0
            for f in image_data_files:
                #img_id = int(re.search("_(\d)_?", os.path.basename(f)).group(1))
                self.image_data[img_id] = f
                img_id += 1
    
    def retrieve_thematic_information(self, roi_link_field, attributes = []):
        self.roi_id = roi_link_field
        self.thematic_info = dict()

        roi_ds = ogr.Open(self.roi_src)
        roi_ly = roi_ds.GetLayer(0)
        link_idx = roi_ly.GetLayerDefn().GetFieldIndex(self.roi_id)

        attrs = ogr_utils.retrieve_attribute_properties(roi_ly, attributes)

        
        for ft in roi_ly:
            gm = ft.GetGeometryRef()
            fid = ft.GetFID()
            self.thematic_info[fid] = dict()
            self.thematic_info[fid][self.roi_id] = ft.GetField(link_idx)
            
            if ogr.GeometryTypeToName(gm.GetGeometryType()).lower() == 'point':
                self.thematic_info[fid]['x'] = gm.GetX()
                self.thematic_info[fid]['y'] = gm.GetY()
            else:
            #if ogr.GeometryTypeToName(gm.GetGeometryType()).lower() == 'polygon':
                self.thematic_info[fid]['x'] = gm.Centroid().GetX()
                self.thematic_info[fid]['y'] = gm.Centroid().GetY()

            added_attr_values = dict()
            for attr_name, attr_idx, attr_type in attrs:
                # finding suitable data type for current attribute    
                if attr_type.lower() == 'integer':
                    val = ft.GetFieldAsInteger(attr_idx)
                elif attr_type.lower() == 'real':
                    val = ft.GetFieldAsDouble(attr_idx)
                elif attr_type.lower() == 'date':
                    val = ft.GetFieldAsDateTime(attr_idx)
                else:
                    val = ft.GetFieldAsString(attr_idx)
                added_attr_values[attr_name] = val
                if self.thematic_info[fid].has_key(attr_name):
                    continue
                else:
                    self.thematic_info[fid][attr_name] = val
            self.thematic_info[fid]['attributes'] = added_attr_values

    def retrieve_band_information(self, bad_src = ''):
        u"""
        Retrieve all necessary band information, including identifiers of bands
        with known bad quality defined in the given external file.
        """
        # retrieving band count
        if self.img_src is None:
            self.band_count = gdal_utils.get_band_count(self.image_data[0])
        else:
            self.band_count = gdal_utils.get_band_count(self.img_src)
        # retrieving bad bands
        if bad_src and os.path.isfile(bad_src):
            self.bad_bands = [int(b) for b in np.loadtxt(bad_src)]
        else:
            self.bad_bands = list()
        # retrieving good bands by creating difference set with bad bands
        self.good_bands = list(set(range(1, self.band_count + 1)).difference(self.bad_bands))

    def retrieve_coverage_information(self, cov_src = ''):
        u"""
        Retrieve coverage information, i.e. whether locations to have spectra
        extracted have valid data and are not covered by clouds, margins etc.
        Information is retrieved from an external file.
        """
        self.coverage = dict()
        if cov_src and os.path.isfile(cov_src):
            for img_id in self.image_data:
                self.coverage[img_id] = list()
            try:
                data = np.loadtxt(cov_src)
            except:
                data = np.genfromtxt(cov_src, converters = {0: lambda s: s.strip()})
                
            for d in data:
                # extracting row_id, usually a location id, i.e. for a plot
                try:
                    row_id = int(d[0])
                except:
                    row_id = d[0]
                # retrieving non-zero elements for each row, i.e. indicators
                # for visibility and coverage for each image id
                try:
                    nz = np.flatnonzero(d[1:])
                except:
                    # this line is necessary to deal with zero-rank arrays
                    # that are generated by np.genfromtxt above if the
                    # original location ids cannot be converted to float,
                    # i.e. if they contain letters
                    nz = np.flatnonzero(np.array(d.tolist()[1:]))
                for n in nz:
                        self.coverage[n].append(row_id)

    def prepare_target(self):
        u"""
        Prepare target file dedicated to store extracted spectra data.
        """
        from time import localtime, strftime
        
        if len(self.image_data) > 1:
            base = general_utils.long_substr(self.image_data.values())
        else:
            base = self.image_data[0]
        
        base = os.path.splitext(os.path.basename(base))[0]
        
        self.tgt_file = "".join((base, strftime("_%Y-%m-%d_%H%M%S", localtime()), '_spectra.txt'))
        self.tgt_file = self.tgt_file.replace("__", "_")
        # adjusting target file name in accordance to the specified neighborhood
        if self.roi_type == 'point':
            if self.context_range > 1:
                if self.context_type == 'square':
                    self.tgt_file = self.tgt_file.replace(".txt", "_%dx%d.txt" % tuple([self.context_range] * 2))
                elif self.context_type == 'circle':
                    self.tgt_file = self.tgt_file.replace(".txt", "_circle_%d.txt" % self.context_range)
        elif self.roi_type == 'line string':
            self.tgt_file = self.tgt_file.replace(".txt", "_lines.txt")
        elif self.roi_type == 'polygon':
            self.tgt_file = self.tgt_file.replace(".txt", "_polygons.txt")
    
    def convert_vector_to_raster(self, img_src):
        u"""
        Base method to convert region of interest geometry data to pixel
        coordinates, i.e. rows and colummns of an image.
        """
        
        output = True
        
        if self.roi_type == 'polygon':
            self.img_coordinates = self.rasterize_polygon_rois(img_src, output)
        elif self.roi_type == 'line string':
            self.img_coordinates = self.rasterize_line_rois(img_src, output)
        elif self.roi_type == 'point':
            self.img_coordinates = self.rasterize_point_rois(img_src, output)

    def extract_spectra(self):
        u"""
        Extract spectra from source imagery and creates well-defined spectrum
        objects.
        """
        for img_id in self.image_data:
            self.img_src = self.image_data[img_id]
            self.convert_vector_to_raster(self.img_src)
            
            curr_coordinates = dict()
            
            if self.coverage:
                for fid in self.img_coordinates:
                    loc_id = self.thematic_info[fid][self.roi_id]
                    if loc_id in self.coverage[img_id]:
                        curr_coordinates[fid] = self.img_coordinates[fid]
            else:
                curr_coordinates = self.img_coordinates
                
            if self.roi_type == 'point':
                # extracting spectra as simple lists
                spectra = gdal_utils.extract_point_spectra(self.img_src, curr_coordinates,
                    bad_bands = self.bad_bands, calibration = (self.slope, self.intercept),
                    context_type = self.context_type, context_range = self.context_range,
                    verbose = self.verbosity)
            elif self.roi_type == 'polygon':
                #curr_coordinates = self.img_coordinates
                spectra = gdal_utils.extract_polygon_spectra(self.img_src, self.img_coordinates,
                    bad_bands = self.bad_bands, calibration = (self.slope, self.intercept),
                    aggregate = self.aggregate, verbose = self.verbosity)
            elif self.roi_type == 'line string':
                spectra = gdal_utils.extract_line_spectra(self.img_src, self.img_coordinates,
                    bad_bands = self.bad_bands, calibration = (self.slope, self.intercept),
                    verbose = self.verbosity)

            # converting dict of raw spectra to spectrum objects
            for fid in spectra:
                # retrieving basic thematic information for current fid
                roi_id = self.thematic_info[fid][self.roi_id]
                x = self.thematic_info[fid]['x']
                y = self.thematic_info[fid]['y']
                # retrieving additional attributes for current fid
                if self.thematic_info[fid].has_key('attributes'):
                    additional_attributes = self.thematic_info[fid]['attributes'].keys()
                # workaround to allow for subsequent iteration over a
                # single (aggregated polygon or simple point) spectrum
                if self.roi_type == 'point' or self.aggregate:
                    spectra[fid] = [spectra[fid]]
                if self.roi_type == 'line string':
                    cnt = 0
                #i = 0
                for sp in spectra[fid]:
                    #i += 1
                    #if not i % 20 == 0:
                    #    continue
                    #else:
                    #    i = 0
                    # creating new spectrum object using region of interest
                    # id and according coordinates
                    spectrum = Spectrum(roi_id, (x, y))
                    # copyying additional attributes
                    for aa in additional_attributes:
                        spectrum.set_attribute(aa, self.thematic_info[fid]['attributes'][aa])
                    if self.roi_type == 'line string':
                        cnt += 1
                        spectrum.set_attribute('_count', cnt)
                    # setting context range and type to default values
                    spectrum.set_context_range(self.context_range)
                    spectrum.set_context_type(self.context_type)
                    spectrum.set_source(img_id + 1)
                    # copying values to spectrum object
                    for gb, val in zip(self.good_bands, sp):
                        spectrum.set_value(gb, val)
                    # adding values of bad bands to spectrum
                    for bb in self.bad_bands:
                        spectrum.set_invalid(bb)
                    # adding current spectrum to list of all extracted spectra
                    self.spectra.append(spectrum)
                #else:
                #    with open(r"z:\sp.pkl", mode = 'a+b') as f:
                #        pickle.dump(spectrum, f)

    def dump_spectra(self, include_bad_bands = True, include_raw_data = True):
        u"""
        Prepare output of extracted spectra data to an external file.
        """
        if not self.spectra:
            return
        
        # initializing output array
        output = list()

        # determining output bands
        if include_bad_bands:
            output_bands = sorted(self.bad_bands + self.good_bands)
        else:
            output_bands = self.good_bands
        
        # if there is more than one source image, we'll include the origin of the
        # current spectra
        if len(self.image_data) > 1:
            include_spectra_source = True
        else:
            include_spectra_source = False

        # iterating over all spectra and adding them to output
        for sp in sorted(self.spectra, key = attrgetter('id')):
            output.append(sp.__str__(include_bad_bands, include_spectra_source, include_raw_data))

        # finally adding a header line
        header_items = [self.roi_id, "img_id", "x", "y"]
        if len(self.image_data) == 1:
            header_items.remove("img_id")
        tmp_sp = self.spectra[0]
        if len(tmp_sp.attributes) > 0:
            for attr in sorted(tmp_sp.attributes.keys()):
                header_items.append(attr)
        if self.context_type == 'circle':
            header_items.append("count")
        
        if self.context_range > 1:
            single_band_output = list()
            for band in output_bands:
                if band in self.good_bands:
                    raw_output = list()
                    if self.context_type == 'square':
                        for suff in general_utils.letter_generator(self.context_range * self.context_range):
                            raw_output.append("%d_raw_%s" % (band, suff))
                    elif self.context_type == 'circle':
                        raw_output.append("\t".join(("%d_min" % band, "%d_max" % band)))
                    single_band_output.append("%s\t%d_mean\t%d_std_dev" % ("\t".join(raw_output), band, band))
                else:
                    single_band_output.append(str(band))
            header_items.append("\t".join(single_band_output))
            #output.insert(0, "\t".join((self.loc_id_field, "img_id", "x", "y", "\t".join(single_band_output))))
        else:
            header_items.append("\t".join([str(k) for k in output_bands]))
            #output.insert(0, "\t".join((self.loc_id_field, "img_id", "x", "y", "\t".join([str(k) for k in output_bands]))))
        
        output.insert(0, "\t".join(header_items))

        # defining target file path
        self.tgt_path = os.path.join(self.tgt_dir, self.tgt_file)
        print "+ Dumping spectra to external file '%s'..." % self.tgt_path
        # writing result to specified output file path
        open(self.tgt_path, 'wb').write("\n".join(output))

    def export_spectra(self, pkl_target = ''):
        u"""
        Export extracted spectra data to an external pickle file.
        """
        if pkl_target:
            pkl_target_file = pkl_target
        else:
            pkl_target_file = os.path.splitext(self.tgt_file)[0] + '.pkl'
        pkl_target_path = os.path.join(self.tgt_dir, pkl_target_file)
        print "+ Exporting spectra to external file '%s'..." % pkl_target_path
        pickle.dump(self.spectra, open(pkl_target_path, 'wb'))

    def rasterize_point_rois(self, img_src, output = False):
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
            
            if self.context_type == 'square':
                #if context == 1:
                #    col, row = gdal_utils.get_pixel_coordinates(img_geo_transform, gm.GetX(), gm.GetY())
                #    img_coordinates[fid] = (col, row)
                #else:
                (c_lb, c_ub), (r_lb, r_ub) = gdal_utils.get_neighborhood(img_geo_transform, gm.GetX(), gm.GetY(), self.context_range)
                img_coordinates[fid] = ((c_lb, c_ub), (r_lb, r_ub))
            elif self.context_type == 'circle':
                circle_pixels = gdal_utils.get_circle(img_geo_transform, gm.GetX(), gm.GetY(), self.context_range)
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
        
        return img_coordinates

    def rasterize_polygon_rois(self, img_src, output = False):
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

        if output:
            out_ds = gdal.GetDriverByName('MEM').Create("", tpl_x_size, tpl_y_size, 1, gdal.GDT_Int16)
            out_ds.SetGeoTransform(tpl_geo_transform)
            out_ds.SetProjection(roi_ly.GetSpatialRef().ExportToWkt())
            out_data = out_ds.GetRasterBand(1).ReadAsArray()
            out_data[:] = -9999
        
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
            if output:
                out_data[~mask.mask] = fid

            pixels = list()
    
            # reversing image shape to make it column-major
            shape = list(mask.shape)
            shape.reverse()
    
            non_mask_indices = ma.flatnotmasked_contiguous(mask)
            # iterating over each slice
            if non_mask_indices is None:
                continue
            for sl in non_mask_indices:
                start_pixel = np.unravel_index(sl.start, tuple(shape), order = 'F')
                stop_pixel = np.unravel_index(sl.stop, tuple(shape), order = 'F')
                #print sl, np.unravel_index(sl.start, mask.shape), np.unravel_index(sl.stop, mask.shape)
                pixels.append((start_pixel, stop_pixel))
            else:
                img_coordinates[fid] = pixels

        if output:
            gdal_utils.export_data(out_data, r"z:\mem_out_raster.img", tpl_ds)
    
        return img_coordinates
    
if __name__ == '__main__':
    
    img_src = r"D:\work\ms.monina\wp5\doeberitzer_heide\2008-08-07_hymap\orig\2008-08-07_hymap_doeberitzer_heide_1_orig.img"
    #img_src = r"D:\work\ms.monina\wp5\doeberitzer_heide\2008-08-07_hymap\orig"
    #img_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\orig"
    img_src = r"D:\tmp\kh_fabi_analysis\kh_mosaic_subset.img"

    vct_src = r"D:\tmp\kh_fabi_analysis\sample_polygons.shp"
    #vct_src = r"Z:\fabi\shp\_nf.shp"
    #vct_src = r"Z:\fabi\msave\_line_test.shp"
    #vct_src = r"D:\work\ms.monina\wp5\doeberitzer_heide\field\doeberitzer_heide_releve_plots.shp"
    #vct_src = r"z:\fabi\shp\_nf_orig_pnt.shp"
    
    #bad_src = r"D:\work\ms.monina\wp5\doeberitzer_heide\2008-08-07_hymap\_info\2008-08-07_hymap_bad_bands_.txt"
    #o_bad_src = r"D:\work\ms.monina\wp5\doeberitzer_heide\2008-08-07_hymap\_info\2008-08-07_hymap_bad_bands.txt"
    bad_src = ''
    
    cov_src = ''
    #cov_src = r"D:\work\ms.monina\wp5\doeberitzer_heide\2008-08-07_hymap\_info\2008-08-07_hymap_strip_plot_id_linkage_unique.txt"
    #cov_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\_info\2007-07-02_ahs_strip_plot_id_linkage_unique_.txt"
    #cov_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\_info\2007-07-02_ahs_strip_plot_id_linkage_duplicates_.txt"

    se = SpectraExtractor(img_src, vct_src, r"Z:\spectra")
    #se.set_context_range()
    se.set_aggregation()
    se.set_calibration()
    se.retrieve_thematic_information('id', ['type'])
    se.retrieve_image_data()
    se.retrieve_band_information(bad_src)
    se.retrieve_coverage_information(cov_src)

    #for img_id in se.image_data:
    #    print img_id, se.image_data[img_id], se.coverage[img_id]

    se.prepare_target()
    se.extract_spectra()
    se.dump_spectra(False)
    #se.export_spectra()
