#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/04/13 14:20:38

u"""
... Put description here ...
"""

import os
import sys

from osgeo import ogr

if __name__ == '__main__':
    
    spc_src = r"D:\work\ms.monina\wp4\eunis_ht_characteristic_species_germany.txt"
    src_dir = r"D:\work\ms.monina\wp4\shp\florkart"
    
    shp_dict = dict()

    for f in os.listdir(src_dir):
        if os.path.splitext(f)[-1] == ".shp":
            src_shp = os.path.join(src_dir, f)
            ds = ogr.Open(src_shp)
            ly = ds.GetLayer(0)
            shp_dict[f] = ly.GetFeatureCount()

    for l in [line.strip() for line in open(spc_src).readlines()]:
        sp = l.split("\t")
        key = "_".join((sp[0].lower().replace(" ", "_"), "-".join(sp[1].split("/")))) + ".shp"
        if shp_dict.has_key(key):
            print "%s\t%d" % (sp[0], shp_dict[key])
        else:
            print "%s\t0" % sp[0]

