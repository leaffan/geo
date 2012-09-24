#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/09/12 11:15:45

u"""
... Put description here ...
"""

import os
import glob
import re
import sys
import pickle

from operator import itemgetter, attrgetter
from osgeo import ogr

from spectrum import Spectrum

from _utils import gdal_utils, ogr_utils, general_utils

class SpectraExtractor(object):
    
    def __init__(self, src, loc_src, cov_src, tgt_dir):
        if os.path.isdir(src):
            self.img_src_dir = src
            self.img_src = None
        elif os.path.isfile(src):
            self.img_src = src
            self.img_src_dir = None
        else:
            print "Couldn't find specified source image or directory..."
            sys.exit()
        self.loc_src = loc_src
        self.tgt_dir = tgt_dir
        # setting neighborhood to 1 by default
        self.neighborhood = 1
        self.spectra = list()
        self.extract_locations = list()
        
    def set_neighborhood(self, neighborhood = 1):
        u"""
        Sets the neighborhood of pixels that will be used for spectrum
        extraction.
        """
        self.neighborhood = neighborhood

    def set_factor(self, factor = 1, intercept = 1):
        u"""
        Sets a scaling value for the spectra to be extracted, i.e. to convert
        from stored digital numbers to real reflectance values between 0 and 1.
        """
        self.factor = factor
        self.interecept = intercept

    def retrieve_image_data(self, img_fmt_types = []):
        self.image_data = dict()
        if self.img_src_dir is None and self.img_src:
            self.image_data[0] = self.img_src
        else:
            image_data_files = [f for f in glob.glob(os.path.join(self.img_src_dir, "*.*")) if os.path.splitext(f)[-1] in img_fmt_types]
            for f in image_data_files:
                img_id = int(re.search("_(\d)_", f).group(1))
                self.image_data[img_id] = f

    def retrieve_sample_locations(self, loc_id_field):
        u"""
        Retrieves sampling locations by using the specified attribute in the
        previously defined location data source.
        """
        self.loc_id_field = loc_id_field
        # handling location data source
        self.loc_ds = ogr.Open(self.loc_src)
        self.loc_ly = self.loc_ds.GetLayer(0)
        # caching locations
        self.cached_locations = ogr_utils.cache_locations(self.loc_ly, [self.loc_id_field])
        self.cached_locations = sorted(self.cached_locations, key = itemgetter('attributes'))

    def retrieve_band_information(self, bad_src = ''):
        u"""
        Retrieves all necessary band information, including identifiers of bands
        with known bad quality defined in the given external file.
        """
        # retrieving band count
        self.bad_src = bad_src
        try:
            self.band_count = gdal_utils.get_band_count(self.img_src)
        except:
            return
        # retrieving bad bands
        if bad_src and os.path.isfile(bad_src):
            self.bad_bands = [int(b) for b in open(bad_src).readlines()[1].split("\t")]
        else:
            self.bad_bands = list()
        # retrieving good bands by creating difference set with bad bands
        self.good_bands = list(set(range(1, self.band_count + 1)).difference(self.bad_bands))

    def retrieve_coverage_information(self, cov_src = ''):
        u"""
        
        """
        self.coverage = dict()
        if self.img_src_dir is None and os.path.isfile(cov_src):
            for line in open(cov_src).readlines():
                loc_id, coverage = [int(x.strip()) for x in line.split()]
                self.coverage[loc_id] = coverage
        elif self.img_src is None and os.path.isfile(cov_src):
            lines = [l.strip() for l in open(cov_src).readlines()]
            for line in lines:
                if line.startswith("#"):
                    continue
                img_id, locations = line.split("\t")
                img_id = int(img_id)
                try:
                    locations = [int(p.strip()) for p in locations[1:-1].split(",")]
                except:
                    locations = [p.strip() for p in locations[1:-1].split(",")]
                self.coverage[img_id] = locations

    def prepare_target(self):
        u"""
        Prepares target file dedicated to store extracted spectra data.
        """
        from datetime import datetime
        from time import gmtime, strftime
        
        if len(self.image_data) > 1:
            base = general_utils.long_substr(self.image_data.values())
        else:
            base = self.image_data[0]
        
        base = os.path.splitext(os.path.basename(base))[0]
        
        self.tgt_file = "".join((base, strftime("_%Y-%m-%d_%H%M", gmtime()), '_spectra.txt'))
        self.tgt_file = self.tgt_file.replace("__", "_")
        # adjusting target file name in accordance to the specified neighborhood
        if self.neighborhood > 1:
            self.tgt_file = self.tgt_file.replace(".txt", "_%dx%d.txt" % tuple([self.neighborhood] * 2))

        print self.tgt_file

    def perform_extraction(self):
        for img_id in self.image_data:
            self.img_id = img_id
            self.img_src = self.image_data[img_id]
            self.extract_locations = list()
            if len(self.image_data) > 1:
                for cp in self.cached_locations:
                    loc_id = cp[self.loc_id_field]
                    if loc_id in self.coverage[img_id]:
                        self.extract_locations.append(cp)
            else:
                if self.coverage:
                    for cp in self.cached_locations:
                        loc_id = cp[self.loc_id_field]
                        if self.coverage.has_key(loc_id) and self.coverage[loc_id]:
                            self.extract_locations.append(cp)
                else:
                    self.extract_locations = self.cached_locations
            self.retrieve_band_information(self.bad_src)
            self.extract_spectra()
            if len(self.image_data) > 1:
                self.cached_locations = location_backup

    def extract_spectra(self, description_field = '', verbose = True):
        u"""
        Extracts spectra from source imagery and creates well-defined spectrum
        objects.
        """
        # extracting spectra as simple lists
        spectra = gdal_utils.extract_spectra(self.img_src, self.extract_locations,
                                             neighborhood = self.neighborhood,
                                             verbose = verbose, bad_bands = self.bad_bands,
                                             scale_factor = self.factor)
        # converting lists to spectrum objects
        # defining list of all extracted spectra
        # iterating over location/spectrum pairs
        for cp, sp in zip(self.extract_locations, spectra):
            # retrieving location id
            loc_id = cp[self.loc_id_field]
            # creating new spectrum object using location id and according coordinates
            spectrum = Spectrum(cp[self.loc_id_field], (cp['x'], cp['y']))
            spectrum.set_neighborhood(self.neighborhood)
            spectrum.set_source(self.img_id)
            if description_field:
                spectrum.set_description(cp[description_field])
            # adding values to spectrum
            for gb, val in zip(self.good_bands, sp):
                spectrum.set_value(gb, val)
            # adding values of bands to spectrum
            for bb in self.bad_bands:
                spectrum.set_invalid(bb)
            # adding current spectrum to list of all extracted spectra
            self.spectra.append(spectrum)
    
    def dump_spectra(self, include_bad_bands = True):
        u"""
        Prepares output of extracted spectra data to an external file.
        """
        # initializing output array
        output = list()

        # determining output bands
        if include_bad_bands:
            output_bands = sorted(self.bad_bands + self.good_bands)
        else:
            output_bands = self.good_bands
            
        # if there is more than on source image, we'll include the origin of the
        # current spectra
        if len(self.image_data) > 1:
            include_spectra_source = True
        else:
            include_spectra_source = False

        # iterating over all spectra and adding them to output
        for sp in sorted(self.spectra, key = attrgetter('id')):
            output.append(sp.__str__(include_bad_bands, include_spectra_source))

        # finally adding a header line
        header_items = [self.loc_id_field, "img_id", "x", "y"]
        if len(self.image_data) == 1:
            header_items.remove("img_id")
        
        if self.neighborhood > 1:
            single_band_output = list()
            for band in output_bands:
                if band in self.good_bands:
                    raw_output = list()
                    for suff in general_utils.letter_generator(self.neighborhood * self.neighborhood):
                        raw_output.append("%d_raw_%s" % (band, suff))
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
        if pkl_target:
            pkl_target_file = pkl_target
        else:
            pkl_target_file = os.path.splitext(self.tgt_file)[0] + '.pkl'
        pkl_target_path = os.path.join(self.tgt_dir, pkl_target_file)
        print "+ Exporting spectra to external file '%s'..." % pkl_target_path
        pickle.dump(self.spectra, open(pkl_target_path, 'wb'))

    def extract(self, loc_id_field, img_bad_src = '', cov_src = '', neigborhood = 1, factor = 0):
        self.retrieve_image_data(['.img'])
        self.retrieve_sample_locations(loc_id_field)
        self.retrieve_band_information(img_bad_src)
        self.retrieve_coverage_information(cov_src)
        self.set_neighborhood(neigborhood)
        self.set_factor(factor)
        self.prepare_target()
        self.perform_extraction()
    
    
if __name__ == '__main__':
    
    img_src = r"D:\work\ms.monina\wp5\wahner_heide\2009-08-06_hymap\georef\2009-08-06_hymap_wahner_heide_mos_first_envi.img"
    img_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_work"
    loc_src = r"D:\work\ms.monina\wp5\wahner_heide\field\shp\invariant_points.shp"
    #loc_src = r"D:\work\ms.monina\wp5\wahner_heide\shp\wh_plots_2011.shp"
    #cov_src = r"D:\work\ms.monina\wp5\wahner_heide\2009-08-06_hymap\_info\2009-08-06_hymap_plot_coverage.txt"
    #cov_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_info\2011-09-14_apex_strip_plot_id_linkage_unique.txt"
    cov_src = ''
    tgt_dir = r"Z:\spectra"

    loc_id_field = 'pnt_id'
    factor = 0.0001

    img_bad_src = ''
    img_bad_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_info\2011-09-14_apex_bad_bands.txt"

    se = SpectraExtractor(img_src, loc_src, '', tgt_dir)
    se.extract(loc_id_field, img_bad_src, cov_src)
    se.dump_spectra(False)
    
    #se.retrieve_image_data(['.img'])
    #se.retrieve_sample_locations(loc_id_field)
    #se.retrieve_band_information(img_bad_src)
    #se.retrieve_coverage_information(cov_src)
    #se.prepare_target()
    #se.set_neighborhood()
    #se.set_factor()
    #se.perform_extraction()
    #se.prepare_output()
    #se.dump_spectra()
