#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A base class for creating sample points located in a given region of interest,
i.e. polygon.
"""

from shapely.geometry import Polygon


class PolygonPointSampler(object):

    def __init__(self, polygon=''):
        """
        Initialize a new PolygonPointSampler object using the specified polygon
        object (as allocated by Shapely). If no polygon is given a new empty
        one is created and set as the base polygon.
        """
        if polygon:
            self.polygon = polygon
        else:
            self.polygon = Polygon()
        self.samples = list()
        self.sample_count = 0
        self.prepared = False

    def add_polygon(self, polygon):
        """
        Add another polygon entity to the base polygon by geometrically
        unifying it with the current one.
        """
        self.polygon = self.polygon.union(polygon)
        self.prepared = False

    def print_samples(self):
        """
        Print all sample points using their WKT representation.
        """
        for sample_pt in self.samples:
            print(sample_pt)

    def prepare_sampling(self):
        """
        Prepare the actual sampling procedure by splitting up the specified
        base polygon (that may consist of multiple simple polygons) and
        appending its compartments to a dedicated list.
        """
        self.src = list()
        if hasattr(self.polygon, 'geoms'):
            for py in self.polygon:
                self.src.append(py)
        else:
            self.src.append(self.polygon)
        self.prepared = True

    def perform_sampling(self):
        """
        Create a stub for the actual sampling procedure.
        """
        raise NotImplementedError
