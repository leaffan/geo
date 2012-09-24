#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: extract_single_strip_spectra.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/05/10 14:24:34

u"""
... Put description here ...
"""
import os
import re
from operator import itemgetter

from osgeo import ogr

from _utils import ogr_utils, gdal_utils, general_utils

if __name__ == '__main__':
    
    img_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-08-02_worldview\orig\2011-08-02_worldview_wahner_heide_ms_orig.img"
    plt_src = r"D:\work\ms.monina\wp5\wahner_heide\shp\wh_plots_2011.shp"
    cov_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-08-02_worldview\_info\2011-08-02_worldview_plot_coverage.txt"
    tgt_dir = r"D:\work\ms.monina\wp5\wahner_heide\2011-08-02_worldview\_spectra"
    search_pattern = 'ms'

    img_src = r"D:\work\ms.monina\wp5\wahner_heide\2009-08-06_hymap\georef\2009_08-06_hymap_wahner_heide_mos_first_envi.img"
    plt_src = r"D:\work\ms.monina\wp5\wahner_heide\shp\wh_plots_2009.shp"
    cov_src = r"D:\work\ms.monina\wp5\wahner_heide\2009-08-06_hymap\_info\2009-08-06_hymap_plot_coverage.txt"
    tgt_dir = r"D:\work\ms.monina\wp5\wahner_heide\2009-08-06_hymap\_spectra"
    search_pattern = 'mos'
    
    id_field = 'plot_id'

    img_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\mos\2011-09-14_apex_wahner_heide_mosaic.img"
    #img_src = r"D:\work\ms.monina\wp5\wahner_heide\2009-08-06_hymap\work\2009-08-06_hymap_wahner_heide_mos_first_envi.img"
    
    img_bad_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_info\2011-09-14_apex_bad_bands.txt"
    #img_bad_src = ''

    plt_src = r"D:\work\ms.monina\wp5\wahner_heide\field\shp\invariant_points.shp"
    cov_src = ''
    tgt_dir = r"Z:\tmp\spectra"
    
    id_field = 'pnt_id'

    search_pattern = 'mos'

    neighborhood = 1
    
    ############################################################################
    
    #plt_coverage = dict()
    #
    #if os.path.isfile(cov_src):
    #    for line in open(cov_src).readlines():
    #        plot, coverage = [int(x.strip()) for x in line.split()]
    #        plt_coverage[plot] = coverage
    
    #try:
    #    bad_bands = [int(b) for b in open(img_bad_src).readlines()[1].split("\t")]
    #except:
    #    bad_bands = list()
    
    ## retrieving plots
    #plt_ds = ogr.Open(plt_src)
    #plt_ly = plt_ds.GetLayer(0)
    ## caching plots
    #cached_plots = ogr_utils.cache_locations(plt_ly, [id_field])
    #cached_plots = sorted(cached_plots, key = itemgetter('attributes'))
    ## retrieving band count
    #band_count = gdal_utils.get_band_count(img_src)
    #good_bands = list(set(range(1, band_count + 1)).difference(bad_bands))
    ## setting up target file name
    #tgt_file = "".join((re.search("(.+)_%s_?" % search_pattern, os.path.basename(img_src)).group(1), '_spectra.txt'))
    ## extracting spectra
    #spectra = gdal_utils.extract_spectra(img_src, cached_plots, neighborhood = neighborhood, verbose = True, bad_bands = bad_bands)
    
    output = list()
    
    #for cp, spectrum in zip(cached_plots, spectra):
    #    plot_id = cp['attributes'][id_field]
    #    if not plt_coverage or plt_coverage[plot_id]:
            #if neighborhood == 1:
            #    output.append("\t".join([str(x) for x in [plot_id, cp['x'], cp['y']]] + [str(v) for v in spectrum]))
            #else:
            #    single_band_output = list()
            #    for band_sp in spectrum:
            #        raw = "\t".join([str(f) for f in band_sp['raw']])
            #        mean = str(band_sp['mean'])
            #        std_dev = str(band_sp['std_dev'])
            #        # putting it all together in output text for a single band
            #        single_band_output.append("\t".join((raw, mean, std_dev)))
            #    output.append("\t".join([str(x) for x in [plot_id, cp['x'], cp['y']]] + ["\t".join(single_band_output)]))
    else:
        # checking whether we operate in some nxn-neighborhood
        if neighborhood > 1:
            single_band_output = list()
            for band in good_bands:
                raw_output = list()
                for suff in general_utils.letter_generator(len(spectrum[0]['raw'])):
                    raw_output.append("%d_raw_%s" % (band, suff))
                single_band_output.append("%s\t%d_mean\t%d_std_dev" % ("\t".join(raw_output), band, band))
                #single_band_output.append("%d_raw_a\t%d_raw_b\t%d_raw_c\t%d_raw_d\t%d_mean\t%d_std_dev" % tuple([band] * 6))
            output.insert(0, "\t".join((id_field, "x", "y", "\t".join(single_band_output))))
        # otherwise the header is much easier to build
        #else:
        #    output.insert(0, "\t".join((id_field, "x", "y", "\t".join([str(k) for k in good_bands]))))
        

    if neighborhood > 1:
        tgt_file = tgt_file.replace(".txt", "_%dx%d.txt" % tuple([neighborhood] * 2))
    tgt_path = os.path.join(tgt_dir, tgt_file)
    open(tgt_path, 'wb').write("\n".join(output))

