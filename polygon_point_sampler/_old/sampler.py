#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2011/10/04 10:43:59

u"""
... Put description here ...
"""
from random import random
from math import sqrt
from bisect import bisect_right
from operator import attrgetter

from shapely.geometry import Point, Polygon, LineString

import p2t

from polygon_point_sampler import PolygonToPointSampler

def floatrange(start, stop, step):
    while start < stop:
        yield start
        start += step

def permutation_2(iterable):
    pool = tuple(iterable)
    n = len(pool)
    if n < 2:
        return
    indices = range(n)
    cycles = range(n, n - 2, -1)
    yield tuple(pool[i] for i in indices[:2])
    while n:
        for i in reversed(range(2)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:2])
                break
        else:
            return
                

def permutations(iterable, r=None):
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    if r > n:
        return
    indices = range(n)
    cycles = range(n, n-r, -1)
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return

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

class CentroidSampler(PolygonToPointSampler):
    
    def perform_sampling(self):
        u"""
        Perform sampling by substituting each source polygon with its centroid
        coordinates.
        """
        for src in self.src:
            self.samples.append(src.centroid)

class LabelPointSampler(PolygonToPointSampler):

    def perform_sampling(self):
        u"""
        Perform sampling by substituting each source polygon with coordinates
        that are guaranteed to be within the polygon's geometry.
        """
        for src in self.src:
            self.samples.append(src.representative_point())

class RegularGridSampler(PolygonToPointSampler):
    
    def __init__(self, polygon = '', x_interval = 100, y_interval = 100):
        super(self.__class__, self).__init__(polygon)
        self.x_interval = x_interval
        self.y_interval = y_interval
    
    def perform_sampling(self):
        u"""
        Perform sampling by substituting the polygon with a regular grid of
        sample points within it. The distance between the sample points is
        given by x_interval and y_interval.
        """
        ll = self.polygon.bounds[:2]
        ur = self.polygon.bounds[2:]
        low_x = int(ll[0]) / self.x_interval * self.x_interval
        upp_x = int(ur[0]) / self.x_interval * self.x_interval + self.x_interval
        low_y = int(ll[1]) / self.y_interval * self.y_interval
        upp_y = int(ur[1]) / self.y_interval * self.y_interval + self.y_interval
        
        for x in floatrange(low_x, upp_x, self.x_interval):
            for y in floatrange(low_y, upp_y, self.y_interval):
                p = Point(x, y)
                if p.within(self.polygon):
                    self.samples.append(p)

class UniformRandomSampler(PolygonToPointSampler):
    
    def __init__(self, polygon = '', samples_per_area_unit = 10, factor = 1000000):
        super(self.__class__, self).__init__(polygon)
        self.samples_per_area_unit = samples_per_area_unit
        self.factor = factor

    def perform_sampling(self):
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
        self.cd_triangulate()
        self.sample_count = int(round(self.polygon.area * self.samples_per_area_unit / self.factor))
        self.area_based_weighting()
        self.sample_uniform_points()

    def cd_triangulate(self):
        u"""
        Perform a Constrained Delaunay Triangulation (CDT) on the source
        polygon(s) resulting in list of triangles sorted by area in descending
        order.
        """
        triangulation = list()
        self.triangles = list()
        for src in self.src:
            triangulation.extend(self.cd_triangulate_single_polygon(src))
        for t in triangulation:
            triangle = Polygon([(t.a.x, t.a.y), (t.b.x, t.b.y), (t.c.x, t.c.y)])
            self.triangles.append(triangle)
        else:
            self.triangles = sorted(self.triangles, key = attrgetter('area'), reverse = True)
    
    def cd_triangulate_single_polygon(self, polygon):
        u"""
        Perform a Constrained Delaunay Triangulation on a single polygon. The
        given polygon needs to be continuous (no multi-polygon) but may contain
        holes.
        """
        # creating a complete list of the polygon's vertices
        vertices = list()
        for coord_pair in polygon.exterior.coords:
            vertices.append(coord_pair)
        # creating the necessary data structure for the triangulation (list of
        # vertex points) excluding the duplicated start and end vertex
        border = [p2t.Point(x, y) for x, y in vertices[1:]]
        # initializing triangulation
        cdt = p2t.CDT(border)
        # adding holes to triangulation configuration
        for interior_ring in polygon.interiors:
            hole = list()
            for coord_pair in interior_ring.coords:
                hole.append(coord_pair)
            else:
                cdt.add_hole([p2t.Point(x, y) for x, y in hole[1:]])
        # performing triangulation and returning result
        return cdt.triangulate()

    def print_triangles(self):
        u"""
        Print all triangles in triangulation using their WKT representation.
        """
        for triangle in self.triangles:
            print triangle

    def area_based_weighting(self):
        u"""
        Perform an area based weighting of all created triangles. Using a pre-
        built sorted list with WeightedRandomGenerator this is very fast. Result
        is a dictionary containing triangle indices as key and their count of
        random occurrence as value.
        """
        # creating dictionary
        self.weighted_random_triangles = dict()
        # setting up weighted random generator using the area of the created
        # triangles as weighting criterion
        wrg = WeightedRandomGenerator(map(attrgetter('area'), self.triangles))
        # selecting a triangle from the pre-built list
        for i in range(self.sample_count):
            wr = wrg.next()
            if not self.weighted_random_triangles.has_key(wr):
                self.weighted_random_triangles[wr] = 0
            self.weighted_random_triangles[wr] += 1

    def sample_uniform_points(self):
        u"""
        Perform a random creation of a point within the selected triangles.
        """
        for randomized_triangle_idx in self.weighted_random_triangles:
            triangle = self.triangles[randomized_triangle_idx]
            count = self.weighted_random_triangles[randomized_triangle_idx]
            for j in range(count):
                point = self.create_point_in_triangle(triangle)
                j += 1
                self.samples.append(point)

    def create_point_in_triangle(self, triangle):
        u"""
        Create a random point within a triangle given by its corner coordinates.
        """
        a = triangle.exterior.coords[0]
        b = triangle.exterior.coords[1]
        c = triangle.exterior.coords[2]
        
        s = random()
        t = sqrt(random())

        x = (1 - t) * a[0] + t * ((1 - s) * b[0] + s * c[0])
        y = (1 - t) * a[1] + t * ((1 - s) * b[1] + s * c[1])

        return Point(x, y)

class SkeletonLineSampler(PolygonToPointSampler):

    SIMPLIFY_TOLERANCE = 20

    def __init__(self, polygon = '', simplify = True, simplify_tolerance = SIMPLIFY_TOLERANCE):
        super(self.__class__, self).__init__(polygon)
        self.simplify = simplify
        self.simplify_tolerance = simplify_tolerance

    def perform_sampling(self):
        from triangle_wrapper import TriangleWrapper
        self.tw = TriangleWrapper()
        self.skel = LineString()
        
        for src in self.src:
            self.tw.set_polygon(src)
            self.tw.create_poly_data()
            tmp_name = self.tw.write_poly_file()
            self.tw.build_triangle_cmd(tmp_name)
            self.tw.execute_triangle()
            self.tw.read_node_file()
            self.tw.read_ele_file()
            single_skel = self.tw.create_skeleton_line()
            self.skel = self.skel.union(single_skel)
        
        #print self.skel
        self.tw.cleanup()
        self.convert_skeleton_to_sample_points()

    def convert_skeleton_to_sample_points(self):
        # converting straight skeleton line to its vertices

        lines = list()

        if hasattr(self.skel, 'geoms'):
            for line in self.skel:
                lines.append(line)
        else:
            lines.append(self.skel)
        
        for line in lines:
            for x, y in line.coords:
                sp = Point((x, y))
                self.samples.append(sp)
                print sp

    def distance(self, from_pt, to_pt):
        
        return sqrt((from_pt[0] - to_pt[0]) ** 2 + (from_pt[1] - to_pt[1]) ** 2)
    

if __name__ == '__main__':
    
    import sys
    import pickle
    from shapely.wkt import load, loads

    sys.path.append(r"D:\dev\python\_misc\ffh")
    from habitat import Habitat, HabitatType, SubHabitat
    pkl_src = r"D:\dev\python\_misc\ffh\ffh_areas.pkl"

    ffh_areas = pickle.load(open(pkl_src))
    area = ffh_areas.itervalues().next()

    #ps = RegularGridSampler(Polygon(), 100, 150)
    #ps = UniformRandomSampler('', 100, 1000000)
    ps = SkeletonLineSampler()

    for sh in area.sub_habitats[:]:
    #sh = area.sub_habitats[0]
        py = loads(sh.outline)
        ps.add_polygon(py)
    
    #print sh.outline
    
    ps.prepare_sampling()
    ps.perform_sampling()
    #ps.perform_triangulation()
    #ps.show_triangulation()
    #ps.perform_sampling()
    #ps.calculate_circumcenters()
    #ps.find_neighbors()
    #ps.find_neighboring_triangles()
    #ps.create_skeleton()
    #ps.find_neighbors_sweep()
    #ps.print_triangles()
    #ps.print_samples()
