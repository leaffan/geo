#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: check_plots.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/02/29 12:52:31

u"""
This script checks whether point plots given in vector dataset (optionally in-
cluding a neighborhood around this point) is covered by valid values in a given
raster dataset. The according raster datasets should be of binary type, with 1
indicating a valid value and 0 otherwise.
Please note that point plots are simply checked for data coverage, not for any
other disturbances such as clouds, data errors, etc.
"""
import os
import glob
from operator import itemgetter
from types import DictionaryType

from osgeo import ogr

from _utils import ogr_utils, gdal_utils

def check_coverage(img_src, locations, neighborhood = 1):
    u"""
    Check whether the given locations have valid data values in the specified
    raster dataset. Optionally a specified neighborhood can be checked for
    valid data values.
    """
    # extracting raster values for locations and the given neighborhood
    spectra = gdal_utils.extract_spectra(img_src, locations, neighborhood)
    coverage = dict()
    for spectrum, location in zip(spectra, locations):
        # retrieving plot id
        plot_id = location['attributes']['plot_id']
        # if there are no raster values at all or the mean value of the
        # neighborhood does not equal 1 then the location has not exclusively
        # valid data values
        if type(spectrum) is DictionaryType:
            if spectrum is None or spectrum['mean'] != 1:
                coverage[plot_id] = 0
            else:
                coverage[plot_id] = 1
        else:
            if spectrum == 1:
                coverage[plot_id] = 1
            else:
                coverage[plot_id] = 0
    return coverage

if __name__ == '__main__':
    plt_src = r"D:\work\ms.monina\wp5\wahner_heide\shp\wh_plots_2011.shp"
    #plt_src = r"D:\work\ms.monina\wp5\wahner_heide\shp\wh_plots_2009.shp"
    cov_dir = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\coverage_old"
    #cov_dir = r"D:\work\ms.monina\wp5\wahner_heide\2011-08-02_worldview\coverage"
    #cov_dir = r"D:\work\ms.monina\wp5\wahner_heide\2009-08-06_hymap\coverage"

    # reading plots from vector dataset
    plt_ds = ogr.Open(plt_src)
    plt_ly = plt_ds.GetLayer(0)
    # caching plots to prepare raster data extraction
    cached_plots = ogr_utils.cache_locations(plt_ly, ['plot_id'])

    coverages = dict()

    # iterating over all GeoTiffs in coverage directory
    for tif in glob.glob(os.path.join(cov_dir, '*.tif')):
        print "+ Checking for plot availability in dataset '%s'..." % os.path.basename(tif),
        # checking plot coverage for current GeoTiff
        cov = check_coverage(tif, cached_plots, 2)
        coverages[os.path.basename(tif)] = cov
        print "Done"

    # iterating over all plot ids
    for cp in sorted(cached_plots, key = itemgetter('attributes')):
        plot_id = cp['attributes']['plot_id']
        line = list()
        line.append(plot_id)
        for tif in sorted(coverages):
            line.append(coverages[tif][plot_id])
        else:
            print "\t".join([str(e) for e in line])
