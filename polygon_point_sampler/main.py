#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/03/13 13:10:54

u"""
... Put description here ...
"""

from sampler import CentroidSampler, LabelPointSampler, RegularGridSampler, UniformRandomSampler, SkeletonLineSampler

if __name__ == '__main__':
    
    from shapely.geometry import Polygon
    from shapely.wkt import loads

    py = Polygon(((0., 0.), (0., 1.), (1., 1.), (1., 0.)))

    wkt_src = r"D:\work\_misc\triangulation_sampling\wkt\p.txt"
    py = loads(open(wkt_src).read())
    print py.area

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
    rs = RegularGridSampler(py, 500, 500)
    rs.perform_sampling()
    for s in rs.samples:
        print "\t", s
    
    print "Uniform random sampling:"
    us = UniformRandomSampler(py, 25)
    #us.set_sample_count(500)
    us.perform_sampling()
    for s in us.samples:
        print "\t", s
    
    us.print_triangles()
    
    print "Skeleton line sampling:"
    sls = SkeletonLineSampler(py)
    sls.perform_sampling()
    sls.convert_skeleton_to_sample_points()