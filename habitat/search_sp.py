#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/03/15 13:11:50

u"""
... Put description here ...
"""

from habitat import SpeciesFinder

if __name__ == '__main__':
    
    sp_names = ['Agropyron repens', 'Barbarea vulgaris', 'Calamagrosis canescens', 'Oxalis stricta']
    sp_src = r"N:\work\veg_wh_nur_d.txt"
    
    sp_names = [line.strip() for line in open(sp_src).readlines()]

    spf = SpeciesFinder()
    
    for sp_name in sp_names:
        spf.set_search_name(sp_name)
        spf.find_species()
        print "========================="