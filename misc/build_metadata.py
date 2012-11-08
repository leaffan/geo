#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/09/04 14:51:09

u"""
... Put description here ...
"""

from metadata_builder import MetadataBuilder

if __name__ == '__main__':
    
    
    src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_simulated_hymap\mos\2011-09-14_simulated_hymap_wahner_heide_mosaic_3m.img"
    src = r"Z:\mos\1_sub_utm31.img"
    src = r"D:\work\ms.monina\wp5\doeberitzer_heide\2008-08-07_hymap\orig\2008-08-07_hymap_doeberitzer_heide_3_orig_good_bands_only.img"
    src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\results\l3b.model.tif"
    src = r"D:\work\ms.monina\wp5\kalmthoutse_heide\2007-07-02_ahs\mos\2007-07-02_ahs_kalmthoutse_heide_mosaic.img"

    mdb = MetadataBuilder(src)
    
    mdb.build_statistics('min', verbose = True)
    mdb.build_overviews(verbose = True)
    mdb.flush_metadata()
