#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: kh_spectra.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/09/22 01:48:56

u"""
Extraction of spectra for the Kalmthoutse Heide area.
"""

from generic_se import SpectraExtractor

if __name__ == '__main__':

    tgt_dir = r"Z:\spectra"

    roi_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\field\kalmthoutse_heide_releve_plots.shp"
    #roi_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\field\950_and_951.shp"
    
    img_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\roi_refined"
    img_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\mos\2007-07-02_ahs_kalmthoutse_heide_mosaic.img"

    img_bad_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\_info\2007-07-02_ahs_bad_bands.txt"
    cov_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\_info\2007-07-02_ahs_strip_plot_id_linkage_unique_.txt"
    cov_src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\_info\2007-07-02_ahs_mosaic_plot_coverage.txt"

    context_range = 5
    context_type = 'circle'

    if not 'roi_id_field' in locals():
        roi_id_field = 'plot_id'
    if not 'img_bad_src' in locals():
        img_bad_src = ''
    if not 'cov_src' in locals():
        cov_src = ''
    if not 'factor' in locals():
        factor = 1
    if not 'context_range' in locals():
        context_range = 1

    se = SpectraExtractor(img_src, roi_src, tgt_dir)

    se.set_context_range(context_range)
    se.set_context_type(context_type)
    se.set_calibration(factor)
    
    se.retrieve_thematic_information(roi_id_field)
    se.retrieve_image_data(['.img'])
    se.retrieve_band_information(img_bad_src)
    se.retrieve_coverage_information(cov_src)
    
    se.prepare_target()

    se.extract_spectra()

    se.dump_spectra(False)
    #se.export_spectra()
