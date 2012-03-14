#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: polygon_point_sampler.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2011/10/04 10:40:44

u"""
... Put description here ...
"""

from shapely.geometry import Polygon

class PolygonPointSampler(object):
    
    def __init__(self, polygon = ''):
        if polygon:
            self.polygon = polygon
        else:
            self.polygon = Polygon()
        self.samples = list()
        self.sample_count = 0
        self.prepared = False

    def add_polygon(self, polygon):
        u"""
        Adds another polygon entity by geometrically unifying it with the
        current base polygon.
        """
        self.polygon = self.polygon.union(polygon)
        self.prepared = False

    def print_samples(self):
        u"""
        Print all sample points using their WKT representation.
        """
        for sample_pt in self.samples:
            print sample_pt

    def prepare_sampling(self):
        self.src = list()
        if hasattr(self.polygon, 'geoms'):
            for py in self.polygon:
                self.src.append(py)
        else:
            self.src.append(self.polygon)
        self.prepared = True

    def perform_sampling(self):
        raise NotImplementedError
