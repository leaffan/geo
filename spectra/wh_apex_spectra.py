#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: wh_spectra.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/09/22 01:48:56

u"""
Extraction of APEX spectra for the Wahner Heide area.
"""

from generic_se import SpectraExtractor

if __name__ == '__main__':

    tgt_dir = r"Z:\spectra"

    roi_src = r"D:\work\ms.monina\wp5\wahner_heide\shp\wh_plots_2011.shp"
    
    img_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_work"

    img_bad_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_info\2011-09-14_apex_bad_bands.txt"
    cov_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_info\2011-09-14_apex_strip_plot_id_linkage_unique_.txt"

    #context_range = 2

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
    se.set_calibration(factor)
    
    se.retrieve_thematic_information(roi_id_field)
    se.retrieve_image_data(['.img'])
    se.retrieve_band_information(img_bad_src)
    se.retrieve_coverage_information(cov_src)
    
    se.prepare_target()
    
    se.extract_spectra()
    
    se.dump_spectra(False)
    se.export_spectra()
