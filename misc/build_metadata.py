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
    
    src = [r"Z:\autopls\kh\_final\kh_2007_mosaic_autopls_model_g.img"]
    #src_dir = r"Z:\autopls\wh\_final"
    
    #for f in os.listdir(src_dir):
    for f in src:
        if os.path.splitext(f)[-1].lower().endswith('img'):
            if 'src_dir' in locals():
                src = os.path.join(src_dir, f)
            else:
                src = f
            mdb = MetadataBuilder(src)
    
            mdb.build_statistics('min', verbose = True)
            mdb.build_overviews(verbose = True)
            mdb.flush_metadata()
