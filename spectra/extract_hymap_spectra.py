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
    
    img_src = r"D:\work\ms.monina\wp5\wahner_heide\2009-08-06_hymap\georef\2009-08-06_hymap_wahner_heide_mos_first_envi.img"
    #img_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_simulated_hymap\mos\2011-09-14_simulated_hymap_wahner_heide_mos_4m.img"
    #img_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_simulated_hymap\diff\2011_minus_2009_hymap_wahner_heide.img"
    
    #loc_src = r"D:\work\ms.monina\wp5\wahner_heide\field\shp\invariant_points.shp"
    #loc_src = r"D:\work\ms.monina\wp5\wahner_heide\shp\wh_plots_2011.shp"
    loc_src = r"D:\work\ms.monina\wp5\wahner_heide\shp\wh_plots_2009.shp"

    tgt_dir = r"Z:\spectra"

    loc_id_field = 'plot_id'
    
    img_bad_src = ''
    
    #cov_src = ''
    cov_src = r"D:\work\ms.monina\wp5\wahner_heide\2009-08-06_hymap\_info\2009-08-06_hymap_plot_coverage.txt"

    neighborhood = 1
    factor = 1 / 10000.
    factor = 0

    se = SpectraExtractor(img_src, loc_src, '', tgt_dir)
    se.extract(loc_id_field, img_bad_src, cov_src, neighborhood, factor)
    se.dump_spectra(False)
