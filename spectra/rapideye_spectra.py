#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/09/22 01:48:56

u"""
... Put description here ...
"""

from spectra_extractor import SpectraExtractor

if __name__ == '__main__':

    tgt_dir = r"Z:\spectra"
    
    img_src = r"Z:\fabi\msave\subset_uffing_2.img"
    #img_src = r"D:\work\ms.monina\wp5\wahner_heide\2009-08-06_hymap\_old\2009-08-06_hymap_wahner_heide_mosaik_utm32.tif"
    #img_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_simulated_hymap\mos\2011-09-14_simulated_hymap_wahner_heide_mos_4m.img"
    #img_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_simulated_hymap\diff\2011_minus_2009_hymap_wahner_heide.img"
    img_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\mos\2011-09-14_apex_wahner_heide_mosaic.img"
    
    #loc_src = r"D:\work\ms.monina\wp5\wahner_heide\field\shp\invariant_points.shp"
    #loc_src = r"D:\work\ms.monina\wp5\wahner_heide\shp\wh_plots_2011.shp"
    loc_src = r"Z:/fabi/msave/uffing_f.shp"
    loc_src = r"z:\fabi\wh_sample_pts.shp"
    #loc_src = r"D:\work\ms.monina\wp5\wahner_heide\field\shp\wh_195plots_doku_2009.shp"
    loc_id_field = 'id'
    
    additional_attributes = ['type']

    #img_bad_src = r"D:\work\ms.monina\wp5\wahner_heide\2009-08-06_hymap\_info\2009-08-06_hymap_bad_bands.txt"
    #img_bad_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_info\2011-09-14_apex_bad_bands.txt"
    #cov_src = r"D:\work\ms.monina\wp5\wahner_heide\2009-08-06_hymap\_info\2009-08-06_hymap_plot_coverage.txt"

    #factor = 1 / 10000.
    #neighborhood = 2

    if not 'loc_id_field' in locals():
        loc_id_field = 'plot_id'
    if not 'img_bad_src' in locals():
        img_bad_src = ''
    if not 'cov_src' in locals():
        cov_src = ''
    if not 'factor' in locals():
        factor = 1
    if not 'neighborhood' in locals():
        neighborhood = 1
    if not 'additional_attributes' in locals():
        additional_attributes = list()

    se = SpectraExtractor(img_src, loc_src, tgt_dir)
    se.extract(loc_id_field, img_bad_src, cov_src, neighborhood, factor, additional_attributes)
    se.dump_spectra(include_bad_bands = True)
    se.export_spectra()
