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
    
    img_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\mos\2007-07-02_ahs_kalmthoutse_heide_mosaic.img"
    loc_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\field\kalmthoutse_heide_releve_plots.shp"

    img_bad_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\_info\2007-07-02_ahs_bad_bands.txt"
    cov_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\_info\2007-07-02_ahs_mosaic_plot_coverage.txt"

    #factor = 1 / 10000.
    neighborhood = 6
    #neighborhood_type = 'circle'

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
    if not 'neighborhood_type' in locals():
        neighborhood_type = 'square'
    if not 'additional_attributes' in locals():
        additional_attributes = list()

    se = SpectraExtractor(img_src, loc_src, tgt_dir)
    se.extract(loc_id_field, img_bad_src, cov_src, neighborhood, factor, additional_attributes, neighborhood_type)
    se.dump_spectra(include_bad_bands = False)
    #se.export_spectra()
