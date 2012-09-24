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
    
    img_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\mos\2011-09-14_apex_wahner_heide_mosaic.img"
    img_src_dir = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_work"
    
    loc_src = r"D:\work\ms.monina\wp5\wahner_heide\field\shp\invariant_points.shp"
    #loc_src = r"D:\work\ms.monina\wp5\wahner_heide\shp\wh_plots_2011.shp"

    tgt_dir = r"Z:\spectra"

    loc_id_field = 'pnt_id'
    img_bad_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_info\2011-09-14_apex_bad_bands.txt"
    cov_src = ''
    #cov_src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_apex\_info\2011-09-14_apex_strip_plot_id_linkage_unique.txt"


    se = SpectraExtractor(img_src, loc_src, '', tgt_dir)
    se.extract(loc_id_field, img_bad_src, cov_src)
    se.dump_spectra(False)
