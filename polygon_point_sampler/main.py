#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/03/13 13:10:54

u"""
... Put description here ...
"""

from sampler import CentroidSampler, LabelPointSampler, RegularGridSampler, UniformRandomSampler

if __name__ == '__main__':
    
    from shapely.geometry import Polygon
    py = Polygon(((0., 0.), (0., 1.), (1., 1.), (1., 0.)))

    print "Centroid sampling:"
    cs = CentroidSampler(py)
    cs.perform_sampling()
    for s in cs.samples:
        print "\t", s
    
    print "Label point sampling:"
    ls = LabelPointSampler(py)
    ls.perform_sampling()
    for s in ls.samples:
        print "\t", s
    
    print "Regular grid sampling:"
    rs = RegularGridSampler(py, 0.25, 0.25)
    rs.perform_sampling()
    for s in rs.samples:
        print "\t", s
    
    print "Uniform random sampling:"
    us = UniformRandomSampler(py)
    us.set_sample_count(10)
    us.perform_sampling()
    for s in us.samples:
        print "\t", s