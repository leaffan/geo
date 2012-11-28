#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/09/04 14:51:09

u"""
... Put description here ...
"""

import os

from metadata_builder import MetadataBuilder

if __name__ == '__main__':
    
    src = r"Z:\autopls\dh\dh_s1_2x2_masked.img"
    src_dir = r"z:\autopls\dh\_final"
    
    for f in os.listdir(src_dir):
        if os.path.splitext(f)[-1].lower().endswith('img'):
            src = os.path.join(src_dir, f)
            mdb = MetadataBuilder(src)
    
            mdb.build_statistics('min', verbose = True)
            mdb.build_overviews(verbose = True, ovr_levels = [4, 8, 12])
            mdb.flush_metadata()
