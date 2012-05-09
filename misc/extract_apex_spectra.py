#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/05/08 13:22:40

u"""
... Put description here ...
"""
import os
import glob
import sys

from types import DictionaryType, FloatType
from osgeo import ogr
from operator import itemgetter

from _utils import gdal_utils, ogr_utils

def retrieve_image_plot_links(src):
    lines = [l.strip() for l in open(src).readlines()]
    img_plt_links = dict()
    for line in lines:
        if line.startswith("#"):
            continue
        strip_id, plots = line.split("\t")
        strip_id = int(strip_id)
        plots = [int(p.strip()) for p in plots[1:-1].split(",")]
        img_plt_links[strip_id] = plots
    return img_plt_links

def find_image_plot_link(img_plt_links, plot_id):
    for strip_id in img_plt_links:
        if plot_id in img_plt_links[strip_id]:
            return strip_id
    return None

if __name__ == '__main__':
    
    apex_src_dir = r"D:\geo_data\ms.monina\airborne\apex\2011-09-14_wahner_heide\utm32"
    apex_plt_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\apex_strip_plot_id_linkage_unique.txt"
    apex_bad_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\apex_bad_bands.txt"
    plt_shp_src = r"D:\work\ms.monina\wp5\wahner_heide\shp\wh_plots_2011.shp"

    image_plt_links = retrieve_image_plot_links(apex_plt_src)
    image_data_files = glob.glob(os.path.join(apex_src_dir, "*.img"))
    apex_bands = set(range(1, 289))
    apex_bad_bands = [int(b) for b in open(apex_bad_src).readlines()[1].split("\t")]

    apex_good_bands = list(apex_bands.difference(apex_bad_bands))

    image_data = dict()

    for f in image_data_files:
        strip_id = int(f[-5])
        image_data[strip_id] = f

    #print image_plt_links
    #print image_data#
    plt_ds = ogr.Open(plt_shp_src)
    plt_ly = plt_ds.GetLayer(0)
    cached_plots = ogr_utils.cache_locations(plt_ly, ['plot_id'])

    #print image_plt_links[2]

    output = list()

    for strip_id in [2, 3, 4]:
        strip_output = list()
        strip_locations = list()
        for cp in sorted(cached_plots, key = itemgetter('attributes')):
            plot_id = cp['attributes']['plot_id']
            if plot_id in image_plt_links[strip_id]:
                strip_locations.append(cp)
        
        spectra = gdal_utils.extract_spectra(image_data[strip_id], strip_locations, verbose = True, neighborhood = 1, bad_bands = apex_bad_bands)

        for strip_location, spectrum in zip(strip_locations, spectra):
            plot_id = strip_location['attributes']['plot_id']
            if type(spectrum[0]) is DictionaryType:
                single_band_output = list()
                for band_sp in spectrum:
                    raw = "\t".join([str(f) for f in band_sp['raw']])
                    mean = str(band_sp['mean'])
                    std_dev = str(band_sp['std_dev'])
                    single_band_output.append("\t".join((raw, mean, std_dev)))
                strip_output.append("\t".join([str(x) for x in [plot_id, strip_id, strip_location['x'], strip_location['y']]] +
                                              ["\t".join(single_band_output)]))
            else:
                strip_output.append("\t".join([str(x) for x in [plot_id, strip_id, strip_location['x'], strip_location['y']]] +
                                              [str(v) for v in spectrum]))
        else:
            if type(spectrum[0]) is DictionaryType:
                single_band_output = list()
                for band in apex_good_bands:
                    single_band_output.append("%d_raw_a\t%d_raw_b\t%d_raw_c\t%d_raw_d\t%d_mean\t%d_std_dev" % tuple([band] * 6))
                strip_output.insert(0, "\t".join(("plot_id", "strip_id", "x", "y", "\t".join(single_band_output))))
            else:
                strip_output.insert(0, "\t".join(("plot_id", "strip_id", "x", "y", "\t".join([str(k) for k in apex_good_bands]))))

        output += strip_output

    #print "\n".join(output)
    
    open(r"d:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\2011-09-14_apex_wahner_heide_spectra.txt", 'wb').write("\n".join(output))

    #open(r"d:\tmp\apex_spectra.txt", 'wb').write("\n".join(output))
    
