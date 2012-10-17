#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: extract_apex_spectra.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/09/22 01:48:56

u"""
... Put description here ...
"""

from spectra_extractor import SpectraExtractor

if __name__ == '__main__':

    tgt_dir = r"Z:\spectra"

    loc_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\field\kalmthoutse_heide_releve_plots.shp"
    
    img_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\roi"

    img_bad_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\_info\2007-07-02_ahs_bad_bands.txt"
    cov_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\_info\2007-07-02_ahs_strip_plot_id_linkage_unique_.txt"

    neighborhood = 2

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

    se = SpectraExtractor(img_src, loc_src, tgt_dir)
    
    se.retrieve_image_data(['.dat'])
    se.retrieve_sample_locations(loc_id_field)
    se.retrieve_band_information(img_bad_src)
    se.retrieve_coverage_information(cov_src, True)
    se.set_neighborhood(neighborhood)
    #se.set_calibration(factor)
    se.prepare_target()
    se.perform_extraction()

    se.dump_spectra(False)
    se.export_spectra()

