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
    
    
    src = r"D:\work\ms.monina\wp5\wahner_heide\2011-09-14_simulated_hymap\diff\2011_minus_2009_hymap_wahner_hei:de.img"
    src = r"z:\tmp\diff\diff_mosaic.dat"
    
    mdb = MetadataBuilder(src)
    
    mdb.build_statistics('min', verbose = True)
    mdb.build_overviews(verbose = True)
    mdb.flush_metadata()
