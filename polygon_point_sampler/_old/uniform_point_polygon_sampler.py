#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2011/08/04 12:05:25

u"""
... Put description here ...
"""
import sys

from operator import itemgetter, attrgetter
from random import random
from math import sqrt
from bisect import bisect_right

from shapely.geometry import Point, Polygon, LineString, MultiPolygon
from shapely.wkt import load, loads

import p2t

import voronoi

def weighted_random_sub(weights):
    rnd = random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i

class WeightedRandomGenerator():
    
    def __init__(self, weights):
        self.totals = list()
        running_total = 0
        for w in weights:
            running_total += w
            self.totals.append(running_total)
    
    def next(self):
        rnd = random() * self.totals[-1]
        return bisect_right(self.totals, rnd)
        
    def __call__(self):
        return self.next()

class PolygonToPointSampler():
    
    def __init__(self, polygon):
        self.src_polygon = polygon
        self.extract_vertices()
        self.samples = list()
        self.sample_count = 0

    def print_samples(self):
        u"""
        Print all sample points using their WKT representation.
        """
        for sp in self.samples:
            print sp
    
    def centroid_sampling(self):
        u"""
        Perform sampling by substituting the polygon with its centroid
        coordinates.
        """
        self.samples = list()
        self.samples.append(self.src_polygon.centroid)

    def label_sampling(self):
        u"""
        Perform sampling by substituting the source polygon with coordinates that
        are guaranteed to be within the polygon's geometry.
        """
        self.samples = list()
        self.samples.append(self.src_polygon.representative_point())

    def regular_grid_sampling(self, x_interval, y_interval):
        u"""
        Perform sampling by substituting the polygon with a regular grid of
        sample points within it. The distance between the sample points is
        given by x_interval and y_interval.
        """
        self.samples = list()

        ll = self.src_polygon.bounds[:2]
        ur = self.src_polygon.bounds[2:]
        low_x = int(ll[0]) / x_interval * x_interval
        upp_x = int(ur[0]) / x_interval * x_interval + x_interval
        low_y = int(ll[1]) / y_interval * y_interval
        upp_y = int(ur[1]) / y_interval * y_interval + y_interval
        
        for x in range(low_x, upp_x, x_interval):
            for y in range(low_y, upp_y, y_interval):
                p = Point(x, y)
                if p.within(self.src_polygon):
                    self.samples.append(p)
    
    def uniform_random_sampling(self, sample_count = 0, cdt = True):
        u"""
        Perform sampling by substituting the polygon with uniformly distributed
        and randomized points that are guaranteed to be within it.
        
        To accomplish this, the following processing steps are conducted:
            - Delaunay triangulation of all source polygon vertices
            - transformation into a constrainted Delaunay triangulation
            - sampling of all created Delaunay triangles weighted in accordance
              to their area
            - creation of sample points within the area-weighted triangles
        
        """
        
        if not self.sample_count:
            self.sample_count = sample_count
        
        if not self.sample_count:
            self.calculate_sample_count()
        
        self.samples = list()
        if cdt:
            self.triangulate_cdt()
        else:
            self.extract_vertices()
            self.triangulate()
            self.constrain_triangulation()
        import time
        t0 = time.clock()
        self.area_based_weighting2(self.sample_count)
        t1 = time.clock() - t0
        print "weighting:", t1
        self.sample_uniform_points()
        t2 = time.clock() - t1
        print "sampling:", t2
    
    def uniform_random_sampling_with_distance_constraint(self, sample_count, min_distance):
        u"""
        Perform sampling by substituting the source polygon with uniformly
        distributed and randomized points that are separated from each other by the
        given minimum distance.
        
        """
        self.samples = list()
        self.triangulate()
        self.constrain_triangulation()
        
        buffered_zone = Polygon()
        
        while len(self.samples) < sample_count:
            wr = weighted_random_sub(map(attrgetter('area'), self.triangles))
            triangle = self.triangles[wr]
            sp = self.create_point_in_triangle(triangle)
            if buffered_zone.contains(sp):
                continue
            sp_buffer = sp.buffer(min_distance)
            buffered_zone = buffered_zone.union(sp_buffer)
            self.samples.append(sp)
        else:
            open(r"d:\tmp\buf.txt", 'wb').write(buffered_zone.__str__())
    
    def extract_vertices(self):
        unique_vertices = set()
        
        for coord_pair in self.src_polygon.exterior.coords:
            unique_vertices.add(coord_pair)
        
        for interior_ring in self.src_polygon.interiors:
            for coord_pair in interior_ring.coords:
                unique_vertices.add(coord_pair)

        unique_vertices = list(unique_vertices)
        self.src_vertices = [Point(unique_vertex_coords) for unique_vertex_coords in unique_vertices]

    def triangulate(self):
        self.triangulation = voronoi.computeDelaunayTriangulation(self.src_vertices)

    def triangulate_cdt(self):
    
        vertices = list()

        #print "preparing constrained delaunay triangulation"
        for coord_pair in self.src_polygon.exterior.coords:
            vertices.append(coord_pair)
        border = [p2t.Point(x, y) for x, y in vertices[1:]]
        #print "initializing cdt"
        cdt = p2t.CDT(border)
        #print "adding holes"
        for interior_ring in self.src_polygon.interiors:
            hole = list()
            for coord_pair in interior_ring.coords:
                hole.append(coord_pair)
            else:
                cdt.add_hole([p2t.Point(x, y) for x, y in hole[1:]])
        #print "performing cdt"
        triangles = cdt.triangulate()
        #print "done"
        
        self.triangles = list()
        
        for t in triangles:
            triangle = Polygon([(t.a.x, t.a.y), (t.b.x, t.b.y), (t.c.x, t.c.y)])
            self.triangles.append(triangle)
        else:
            self.triangles = sorted(self.triangles, key = attrgetter('area'), reverse = True)

    def calculate_sample_count(self, density = 1, factor = 1):
        self.sample_count = int(round(self.src_polygon.area * density / factor))

    def constrain_triangulation(self):
        self.triangles = list()

        for index_triple in self.triangulation:
            corners = list()
            for index in index_triple:
                corners.append(self.src_vertices[index])
            triangle = Polygon([(c.x, c.y) for c in corners])
            if py.contains(triangle):
                self.triangles.append(triangle)
        else:
            self.triangles = sorted(self.triangles, key = lambda triangle: triangle.area, reverse = True)
    
    def area_based_weighting(self, sample_count):
        self.weighted_random_triangles = dict()
        for i in range(sample_count):
            wr = weighted_random_sub(map(attrgetter('area'), self.triangles))
            if not self.weighted_random_triangles.has_key(wr):
                self.weighted_random_triangles[wr] = 0
            self.weighted_random_triangles[wr] += 1

    def area_based_weighting2(self, sample_count):
        self.weighted_random_triangles = dict()
        wrg = WeightedRandomGenerator(map(attrgetter('area'), self.triangles))
        for i in range(sample_count):
            wr = wrg.next()
            if not self.weighted_random_triangles.has_key(wr):
                self.weighted_random_triangles[wr] = 0
            self.weighted_random_triangles[wr] += 1

    def sample_uniform_points(self):
        self.samples = list()
        
        for randomized_triangle_idx in self.weighted_random_triangles:
            triangle = self.triangles[randomized_triangle_idx]
            count = self.weighted_random_triangles[randomized_triangle_idx]
            for j in range(count):
                point = self.create_point_in_triangle(triangle)
                j += 1
                self.samples.append(point)

    def create_point_in_triangle(self, triangle):
        a = triangle.exterior.coords[0]
        b = triangle.exterior.coords[1]
        c = triangle.exterior.coords[2]
        
        s = random()
        t = sqrt(random())

        x = (1 - t) * a[0] + t * ((1 - s) * b[0] + s * c[0])
        y = (1 - t) * a[1] + t * ((1 - s) * b[1] + s * c[1])

        return Point(x, y)

    def print_triangles(self):
        if not hasattr(self, 'triangles') and hasattr(self, 'triangulation'):
            self.triangles = list()
            for index_triple in self.triangulation:
                corners = list()
                for index in index_triple:
                    corners.append(self.src_vertices[index])
                triangle = Polygon([(c.x, c.y) for c in corners])
                self.triangles.append(triangle)
            else:
                self.triangles = sorted(self.triangles, key = lambda triangle: triangle.area, reverse = True)
        if not hasattr(self, 'triangles'):
            return
        if not self.triangles:
            return
        
        for t in self.triangles:
            print t

if __name__ == '__main__':

    # todo:
    
    # triangulation for all subparts
    # sampling afterwards

    import pickle
    
    sys.path.append(r"D:\dev\python\_misc\ffh")
    from habitat import Habitat, HabitatType, SubHabitat

    pkl_src = r"D:\dev\python\_misc\ffh\ffh_areas.pkl"

    ffh_areas = pickle.load(open(pkl_src))
    
    area = ffh_areas.itervalues().next()

    for sh in area.sub_habitats:
        py = loads(sh.outline)
        pps = PolygonToPointSampler(py)
        
        #print pps.src_polygon.area
        pps.calculate_sample_count(50, 1000000)
        #print pps.sample_count

        pps.uniform_random_sampling()

        print len(pps.samples)
        
        #pps.triangulate_cdt()
    ##pps.uniform_random_sampling(500, False)
        #pps.print_triangles()
    ##pps.print_samples()
    #if i == 1:
    #    break

    sys.exit()


    #weights = [.3, .3, .3, .1]
    #
    #wrg = WeightedRandomGenerator(weights)
    #
    #res = dict()
    #
    #for i in range(100):
    #    ret = wrg.next()
    #    if not res.has_key(ret):
    #        res[ret] = 0
    #    res[ret] += 1
    #else:
    #    for r in res:
    #        print weights[r], ":", res[r]

    #sys.exit()

    #import time
    #t0 = time.clock()
    #
    #py_src = r"d:\tmp\wh.txt"
    ##py_src = r"d:\tmp\ffh2.txt"
    #py = load(open(py_src))
    #
    #pps = PolygonToPointSampler(py)
    #
    ##pps.triangulate_cdt()
    #
    #pps.uniform_random_sampling(5000)
    ##pps.print_samples()
    #
    #print time.clock() - t0
    #
    ##pps.centroid_sampling()
    ##pps.print_samples()
    #
    ##pps.label_sampling()
    ##pps.print_samples()
    #
    ##pps.regular_grid_sampling(500, 1500)
    ##pps.print_samples()
    #
    ##pps.uniform_random_sampling_with_distance_constraint(50, 200)
    ##pps.print_samples()
    #
