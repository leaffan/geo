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
from numpy import loadtxt

from spectrum import Spectrum

from _utils import gdal_utils, ogr_utils, general_utils

class SpectraExtractor(object):
    
    def __init__(self, img_src, loc_src, tgt_dir):
        if os.path.isdir(img_src):
            self.img_src_dir = img_src
            self.img_src = None
        elif os.path.isfile(img_src):
            self.img_src = img_src
            self.img_src_dir = None
        else:
            print "Couldn't find specified source image or directory..."
            sys.exit()
        self.loc_src = loc_src
        self.tgt_dir = tgt_dir
        # setting neighborhood to 1 by default
        self.neighborhood = 1
        # setting neighborhood type to square by default
        self.neighborhood_type = 'square'
        # turning off calibration by default
        self.set_calibration()
        self.spectra = list()
        self.extract_locations = list()
        
    def set_neighborhood(self, neighborhood = 1):
        u"""
        Sets the neighborhood of pixels that will be used for spectrum
        extraction.
        """
        self.neighborhood = neighborhood

    def set_neighborhood_type(self, neighborhood_type = 'square'):
        u"""
        Sets the neighborhood type that will be used for spectrum
        extraction.
        """
        self.neighborhood_type = neighborhood_type

    def set_calibration(self, slope = 1, intercept = 0):
        u"""
        Sets up linear scaling parameters for the spectra to be extracted,
        i.e. to convert from stored digital numbers to real reflectance values
        between 0 and 1.
        """
        self.slope = slope
        self.interecept = intercept

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

    def retrieve_sample_locations(self, loc_id_field, additional_attributes = []):
        u"""
        Retrieve sampling locations by using the specified attribute in the
        previously defined location data source.
        """
        self.loc_id_field = loc_id_field
        # handling location data source
        self.loc_ds = ogr.Open(self.loc_src)
        self.loc_ly = self.loc_ds.GetLayer(0)
        # caching locations
        self.cached_locations = ogr_utils.cache_locations(self.loc_ly, [self.loc_id_field] + additional_attributes)
        self.cached_locations = sorted(self.cached_locations, key = itemgetter('attributes'))

    def retrieve_band_information(self, bad_src = ''):
        u"""
        Retrieve all necessary band information, including identifiers of bands
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

    def retrieve_coverage_information(self, cov_src = '', np = False):
        u"""
        Retrieve coverage information, i.e. whether locations to have spectra
        extracted have valid data and are not covered by clouds, margins etc.
        Information is retrieved from an external file.
        """
        self.coverage = dict()
        if self.img_src_dir is None and os.path.isfile(cov_src):
            for line in open(cov_src).readlines():
                if line.startswith("#"):
                    continue
                try:
                    loc_id, coverage = [int(x.strip()) for x in line.split()]
                except:
                    tokens = line.split()
                    loc_id, coverage = tokens[0], int(tokens[1])
                self.coverage[loc_id] = coverage
        elif self.img_src is None and os.path.isfile(cov_src):
            if not np:
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
            else:
                #TODO: use this as standard
                cov_info = loadtxt(cov_src, unpack = True)
                plots = cov_info[0]
                plots_done = list()
                for s in range(len(cov_info[1:])):
                    self.coverage[s + 1] = list()
                    for p in range(len(plots)):
                        plot = int(plots[p])
                        if plot in plots_done:
                            continue
                        if cov_info[s + 1, p]:
                            self.coverage[s + 1].append(plot) 
                            #print s + 1, int(plots[p])
                

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
        if self.neighborhood > 1:
            if self.neighborhood_type == 'square':
                self.tgt_file = self.tgt_file.replace(".txt", "_%dx%d.txt" % tuple([self.neighborhood] * 2))
            elif self.neighborhood_type == 'circle':
                self.tgt_file = self.tgt_file.replace(".txt", "_circle_%d.txt" % self.neighborhood)

    def extract(self, loc_id_field, img_bad_src = '', cov_src = '', neighborhood = 1, factor = 1, add_attrs = [], nb_type = 'square'):
        self.retrieve_image_data(['.img'])
        self.retrieve_sample_locations(loc_id_field, add_attrs)
        self.retrieve_band_information(img_bad_src)
        self.retrieve_coverage_information(cov_src)
        self.set_neighborhood(neighborhood)
        self.set_neighborhood_type(nb_type)
        self.set_calibration(factor)
        self.prepare_target()
        self.perform_extraction()

    def perform_extraction(self):
        u"""
        Perform extraction of spectra for all source images.
        """
        # iterating over all source images
        for img_id in self.image_data:
            # retrieving current image id and image data src
            self.img_id = img_id
            self.img_src = self.image_data[img_id]
            # setting up a list of locations to have spectra extracted
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

    def extract_spectra(self, description_field = '', verbose = True):
        u"""
        Extract spectra from source imagery and creates well-defined spectrum
        objects.
        """
        # extracting spectra as simple lists
        spectra = gdal_utils.extract_spectra(self.img_src, self.extract_locations,
                                             neighborhood = self.neighborhood,
                                             verbose = verbose, bad_bands = self.bad_bands,
                                             scale_factor = self.slope, nb_type = self.neighborhood_type)
        # converting lists to spectrum objects
        # defining list of all extracted spectra
        # iterating over location/spectrum pairs
        for cp, sp in zip(self.extract_locations, spectra):
            # retrieving location id
            if cp.has_key('attributes'):
                additional_attributes = cp['attributes'].keys()
                additional_attributes.remove(self.loc_id_field)
            loc_id = cp[self.loc_id_field]
            # creating new spectrum object using location id and according coordinates
            spectrum = Spectrum(loc_id, (cp['x'], cp['y']))
            for aa in additional_attributes:
                spectrum.set_attribute(aa, cp['attributes'][aa])
            spectrum.set_neighborhood(self.neighborhood)
            spectrum.set_neighborhood_type(self.neighborhood_type)
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
    
    def dump_spectra(self, include_bad_bands = True, include_raw_data = True):
        u"""
        Prepare output of extracted spectra data to an external file.
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
            output.append(sp.__str__(include_bad_bands, include_spectra_source, include_raw_data))

        # finally adding a header line
        header_items = [self.loc_id_field, "img_id", "x", "y"]
        if len(self.image_data) == 1:
            header_items.remove("img_id")
        if self.spectra:
            tmp_sp = self.spectra[0]
        if len(tmp_sp.attributes) > 0:
            for attr in sorted(tmp_sp.attributes.keys()):
                header_items.append(attr)
        if self.neighborhood_type == 'circle':
            header_items.append("count")
        
        if self.neighborhood > 1:
            single_band_output = list()
            for band in output_bands:
                if band in self.good_bands:
                    raw_output = list()
                    if self.neighborhood_type == 'square':
                        for suff in general_utils.letter_generator(self.neighborhood * self.neighborhood):
                            raw_output.append("%d_raw_%s" % (band, suff))
                    elif self.neighborhood_type == 'circle':
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
    
if __name__ == '__main__':

    pass    

