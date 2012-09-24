#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: extract_multi_strip_spectra.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/05/08 13:22:40

u"""
This script uses a number of remote sensing images and accompanying ancillary
information to extract point spectra from the imagery for a number of specified
locations.
"""
import os
import glob
import re

from osgeo import ogr
from operator import itemgetter

from _utils import gdal_utils, ogr_utils, general_utils

def retrieve_image_plot_links(src):
    u"""
    Retrieve for each image strip the corresponding plot ids. Plot ids were as-
    signed to image strips based on where their best representation could be
    found.
    This information is stored in an external source in the following format:
    <strip_id>  [plot_id, plot_id, ...]
    """
    lines = [l.strip() for l in open(src).readlines()]
    img_plt_links = dict()
    for line in lines:
        if line.startswith("#"):
            continue
        strip_id, plots = line.split("\t")
        strip_id = int(strip_id)
        try:
            plots = [int(p.strip()) for p in plots[1:-1].split(",")]
        except:
            plots = [p.strip() for p in plots[1:-1].split(",")]
        img_plt_links[strip_id] = plots
    return img_plt_links

def find_image_plot_link(img_plt_links, plot_id):
    u"""
    Find the image strip for the given plot id using the specified dictionary
    object.
    """
    for strip_id in img_plt_links:
        if plot_id in img_plt_links[strip_id]:
            return strip_id
    return None

if __name__ == '__main__':
    
    # directory containing imagery
    img_src_dir = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_work"
    #img_src_dir = r"D:\work\ms.monina\wp5\doeberitzer_heide\2008-08-07_hymap\orig"
    #img_src_dir = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\orig"
    # source file containing information about bad bands
    img_bad_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_info\2011-09-14_apex_bad_bands.txt"
    #img_bad_src = r"D:\work\ms.monina\wp5\doeberitzer_heide\2008-08-07_hymap\_info\2008-08-07_hymap_bad_bands.txt"
    #img_bad_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\_info\2007-07-02_ahs_bad_bands.txt"
    # source file containing information about linkage between image strips and  plots
    img_plt_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_info\2011-09-14_apex_strip_plot_id_linkage_unique.txt"
    #img_plt_src = r"D:\work\ms.monina\wp5\doeberitzer_heide\2008-08-07_hymap\_info\2008-08-07_hymap_strip_plot_id_linkage_duplicates.txt"
    #img_plt_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\_info\2007-07-02_ahs_strip_plot_id_linkage_unique.txt"
    # source file containing plot geometries
    plt_shp_src = r"D:\work\ms.monina\wp5\wahner_heide\shp\wh_plots_2011.shp"
    #plt_shp_src = r"D:\work\ms.monina\wp5\doeberitzer_heide\field\doeberitzer_heide_releve_plots.shp"
    #plt_shp_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\field\kalmthoutse_heide_releve_plots.shp"
    
    # target directory for spectra output
    tgt_dir = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_spectra"
    tgt_dir = r"Z:\tmp\spectra"

    # pixel-neighborhood to extract spectra from
    neighborhood = 2
    # image file extension(s)
    types = ('.img')
    
    ############################################################################
    
    # retrieving links between flight strips and plot ids
    image_plt_links = retrieve_image_plot_links(img_plt_src)
    # retrieving image files
    image_data_files = [f for f in glob.glob(os.path.join(img_src_dir, "*.*")) if os.path.splitext(f)[-1] in types]
    # retrieving bad bands from specified file
    try:
        bad_bands = [int(b) for b in open(img_bad_src).readlines()[1].split("\t")]
    except:
        bad_bands = list()

    # building an image data dictionary using strip ids as keys
    image_data = dict()
    # list of all available strip ids
    available_strips = list()
    for f in image_data_files:
        strip_id = int(re.search("_(\d)_", f).group(1))
        available_strips.append(strip_id)
        image_data[strip_id] = f
    # retrieving plots
    plt_ds = ogr.Open(plt_shp_src)
    plt_ly = plt_ds.GetLayer(0)
    # caching plots
    cached_plots = ogr_utils.cache_locations(plt_ly, ['plot_id'])

    # setting up output
    output = list()
    
    # iterating over a selection of strip ids
    for strip_id in available_strips:
        # retrieving band count
        band_count = gdal_utils.get_band_count(image_data[strip_id])
        # retrieving good bands by calculating the difference between all 
        # bands and those that have been declared bad
        good_bands = list(set(range(1, band_count + 1)).difference(bad_bands))

        tgt_file = "".join((re.search("(.+)_\d_", os.path.basename(image_data[strip_id])).group(1), '_spectra.txt'))

        # setting up a list of plots that are linked with the current strip
        strip_locations = list()
        # setting up the output for current strip id
        strip_output = list()
        # retrieving plots that are linked with the current strip
        for cp in sorted(cached_plots, key = itemgetter('attributes')):
            plot_id = cp['attributes']['plot_id']
            if plot_id in image_plt_links[strip_id]:
                strip_locations.append(cp)
        
        # extracting spectra from the current image strip for all plots that
        # are linked with it
        # bands that have been regarded bad are ignored
        spectra = gdal_utils.extract_spectra(image_data[strip_id], strip_locations, verbose = True, neighborhood = neighborhood, bad_bands = bad_bands)

        # as there are as much plots for the current strip as there are spectra
        # we can simultaneously iterate over them
        for strip_location, spectrum in zip(strip_locations, spectra):
            plot_id = strip_location['attributes']['plot_id']
            # checking whether were in some nxn-neighborhood, i.e. retrieved
            # values from a group of pixels
            if neighborhood > 1:
                single_band_output = list()
                # retrieving raw values and basic descriptive statistics
                for band_sp in spectrum:
                    raw = "\t".join([str(f) for f in band_sp['raw']])
                    mean = str(band_sp['mean'])
                    std_dev = str(band_sp['std_dev'])
                    # putting it all together in output text for a single band
                    single_band_output.append("\t".join((raw, mean, std_dev)))
                # merging all single band outputs with plot information to build
                # output for a single plot
                strip_output.append("\t".join([str(x) for x in [plot_id, strip_id, strip_location['x'], strip_location['y']]] +
                                              ["\t".join(single_band_output)]))
            # otherwise a single value has been retrieved for each band,
            # i.e. from a single pixel
            else:
                # putting it all together in output text for a single plot
                strip_output.append("\t".join([str(x) for x in [plot_id, strip_id, strip_location['x'], strip_location['y']]] +
                                              [str(v) for v in spectrum]))

        output += strip_output

    # finally adding header lines
    # checking whether we operate in some nxn-neighborhood
    if neighborhood > 1:
        single_band_output = list()
        for band in good_bands:
            raw_output = list()
            for suff in general_utils.letter_generator(len(spectrum[0]['raw'])):
                raw_output.append("%d_raw_%s" % (band, suff))
            single_band_output.append("%s\t%d_mean\t%d_std_dev" % ("\t".join(raw_output), band, band))
            #single_band_output.append("%d_raw_a\t%d_raw_b\t%d_raw_c\t%d_raw_d\t%d_mean\t%d_std_dev" % tuple([band] * 6))
        output.insert(0, "\t".join(("plot_id", "strip_id", "x", "y", "\t".join(single_band_output))))
    # otherwise the header is much easier to build
    else:
        output.insert(0, "\t".join(("plot_id", "strip_id", "x", "y", "\t".join([str(k) for k in good_bands]))))

    if neighborhood > 1:
        tgt_file = tgt_file.replace(".txt", "_%dx%d.txt" % tuple([neighborhood] * 2))
    tgt_path = os.path.join(tgt_dir, tgt_file)
    open(tgt_path, 'wb').write("\n".join(output))
