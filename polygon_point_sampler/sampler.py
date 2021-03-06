#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import random
from operator import attrgetter
from math import sqrt

from shapely.geometry import Point, Polygon, LineString
from shapely.ops import linemerge

import pypoly2tri as p2t

from polygon_point_sampler import PolygonPointSampler
from triangle_wrapper import TriangleWrapper
from utils import floatrange, WeightedRandomGenerator


class CentroidSampler(PolygonPointSampler):
    def perform_sampling(self):
        """
        Perform sampling by representing each source polygon with its centroid.
        """
        if not self.prepared:
            self.prepare_sampling()
        for src in self.src:
            self.samples.append(src.centroid)


class RepresentativePointSampler(PolygonPointSampler):
    def perform_sampling(self):
        """
        Perform sampling by representing each source polygon with a
        representative point whose coordinates are guaranteed to be within
        the polygon's geometry.
        """
        if not self.prepared:
            self.prepare_sampling()
        for src in self.src:
            self.samples.append(src.representative_point())


class RegularGridSampler(PolygonPointSampler):
    def __init__(self, polygon='', x_interval=100, y_interval=100):
        super(self.__class__, self).__init__(polygon)
        self.x_interval = x_interval
        self.y_interval = y_interval

    def perform_sampling(self):
        """
        Perform sampling by substituting the polygon with a regular grid of
        sample points within it. The distance between the sample points is
        given by x_interval and y_interval.
        """
        if not self.prepared:
            self.prepare_sampling()
        ll = self.polygon.bounds[:2]
        ur = self.polygon.bounds[2:]
        low_x = int(ll[0]) / self.x_interval * self.x_interval
        upp_x = (
            int(ur[0]) / self.x_interval * self.x_interval + self.x_interval)
        low_y = int(ll[1]) / self.y_interval * self.y_interval
        upp_y = (
            int(ur[1]) / self.y_interval * self.y_interval + self.y_interval)

        for x in floatrange(low_x, upp_x, self.x_interval):
            for y in floatrange(low_y, upp_y, self.y_interval):
                p = Point(x, y)
                if p.within(self.polygon):
                    self.samples.append(p)


class UniformRandomSampler(PolygonPointSampler):
    def __init__(self, polygon='', samples_per_area_unit=10, factor=1000000):
        super(self.__class__, self).__init__(polygon)
        self.samples_per_area_unit = samples_per_area_unit
        self.sample_count = 0
        self.factor = factor

    def set_sample_count(self, count):
        self.sample_count = count

    def perform_sampling(self):
        """
        Perform sampling by representing the polygon with randomized and
        uniformly distributed points that are guaranteed to be within the
        source polygon's geometry.

        To accomplish this, the following processing steps are conducted:
            - Delaunay triangulation of all source polygon vertices
            - transformation into a constrainted Delaunay triangulation
            - sampling of all created Delaunay triangles weighted in accordance
              to their area
            - creation of sample points within the area-weighted triangles
        """
        if not self.prepared:
            self.prepare_sampling()
        # creating constrained Delaunay triangulation
        self.cd_triangulate()
        # calculating number of samples to be created
        if not self.sample_count:
            self.sample_count = int(round(
                self.polygon.area * self.samples_per_area_unit / self.factor))
        # performing area based weighting
        self.area_based_weighting()
        # creating uniformly distributed points
        self.sample_uniform_points()

    def cd_triangulate(self):
        """
        Perform a Constrained Delaunay Triangulation (CDT) on the source
        polygon(s) resulting in list of triangles sorted by area in descending
        order.
        """
        triangulation = list()
        self.triangles = list()
        for src in self.src:
            triangulation.extend(self.cd_triangulate_single_polygon(src))
        for t in triangulation:
            triangle = Polygon(
                [
                    (t.GetPoint(0).x, t.GetPoint(0).y),
                    (t.GetPoint(1).x, t.GetPoint(1).y),
                    (t.GetPoint(2).x, t.GetPoint(2).y)])
            self.triangles.append(triangle)
        else:
            self.triangles = sorted(
                self.triangles, key=attrgetter('area'), reverse=True)

    def cd_triangulate_single_polygon(self, polygon):
        """
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
        border = [p2t.shapes.Point(x, y) for x, y in vertices[1:]]

        # print(
        #     "POLYGON ((%s))" % ", ".join(
        #         [("%f %f" % (p.x, p.y)) for p in border]))

        # initializing triangulation
        cdt = p2t.cdt.CDT(border)
        # adding holes to triangulation configuration
        for interior_ring in polygon.interiors:
            hole = list()
            for coord_pair in interior_ring.coords:
                hole.append(coord_pair)
            else:
                cdt.AddHole([p2t.shapes.Point(x, y) for x, y in hole[1:]])
        # performing triangulation and returning result
        cdt.Triangulate()
        return cdt.GetTriangles()

    def print_triangles(self):
        """
        Print all triangles in triangulation using their WKT representation.
        """
        for triangle in self.triangles:
            print(triangle)

    def area_based_weighting(self):
        """
        Perform an area based weighting of all created triangles. Using a pre-
        built sorted list with WeightedRandomGenerator this is very fast.
        Result is a dictionary containing triangle indices as key and their
        count of random occurrence as value.
        """
        # creating dictionary
        self.weighted_random_triangles = dict()
        # setting up weighted random generator using the area of the created
        # triangles as weighting criterion
        wrg = WeightedRandomGenerator(map(attrgetter('area'), self.triangles))
        # selecting a triangle from the pre-built list
        for i in range(self.sample_count):
            wr = wrg.next()
            if wr not in self.weighted_random_triangles:
                self.weighted_random_triangles[wr] = 0
            self.weighted_random_triangles[wr] += 1

    def sample_uniform_points(self):
        """
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
        """
        Create a random point within a triangle given by its corner
        coordinates.
        """
        a = triangle.exterior.coords[0]
        b = triangle.exterior.coords[1]
        c = triangle.exterior.coords[2]

        s = random()
        t = sqrt(random())

        x = (1 - t) * a[0] + t * ((1 - s) * b[0] + s * c[0])
        y = (1 - t) * a[1] + t * ((1 - s) * b[1] + s * c[1])

        return Point(x, y)


class SkeletonLineSampler(PolygonPointSampler):

    SIMPLIFY_TOLERANCE = 20

    def __init__(
        self,
        polygon='',
        simplify=True,
        simplify_tolerance=SIMPLIFY_TOLERANCE
    ):
        super(self.__class__, self).__init__(polygon)
        self.simplify = simplify
        self.simplify_tolerance = simplify_tolerance

    def perform_sampling(self):
        if not self.prepared:
            self.prepare_sampling()

        # performing a conforming Delaunay triangulation using Triangle
        self.tw = TriangleWrapper(self.polygon)
        # self.tw.toggle_verbosity()
        self.tw.apply_triangle()

        # creating skeleton line from triangulation
        self.skel = self.create_skeleton_line()
        self.convert_skeleton_to_sample_points()

    def create_skeleton_line(self, simplify=True, simplify_tolerance=''):
        """
        Create a skeleton line of the polygon by using the circumcenters of the
        triangles created by the Conforming Delaunay Triangulation applied by
        Triangle
        Optionally simplify (by default) the skeleton by using an algorithm
        provided by Shapely.
        """
        self.circumcenters = list()
        for t in self.tw.triangles:
            self.circumcenters.append(self.calculate_circumcenter(t))

        # list of skeleton segments
        skel_segments = list()
        for key in sorted(self.tw.shared_edges.keys()):
            if self.tw.shared_edges[key] != 2:
                continue
            # retrieve endpoints of the skeleton segment
            from_pt = self.circumcenters[key[0] - 1]
            to_pt = self.circumcenters[key[1] - 1]
            # creating skeleton segment
            skel_segment = LineString(
                [(cc.x, cc.y) for cc in (from_pt, to_pt)])
            skel_segments.append(skel_segment)
        else:
            # merging all skeleton segments to a single (possibly multiline)
            # object
            skel_line = linemerge(skel_segments)

        # simplifying skeleton line
        if simplify:
            if not simplify_tolerance:
                simplify_tolerance = self.SIMPLIFY_TOLERANCE
            skel_line = skel_line.simplify(simplify_tolerance, False)

        return skel_line

    def convert_skeleton_to_sample_points(self):
        """
        Convert a straight skeleton line to its vertices.
        """
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

    def calculate_circumcenter(self, triangle):
        u"""
        Calculate circumcenter of given triangle in cartesian coordinates
        according to formula given by: http://is.gd/ctPx80
        """
        a, b, c = [Point(triangle.exterior.coords[i]) for i in [0, 1, 2]]
        d = 2 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y))
        cx = (
            (a.y**2 + a.x**2) * (b.y - c.y) +
            (b.y**2 + b.x**2) * (c.y - a.y) +
            (c.y**2 + c.x**2) * (a.y - b.y)) / d
        cy = (
            (a.y**2 + a.x**2) * (c.x - b.x) +
            (b.y**2 + b.x**2) * (a.x - c.x) +
            (c.y**2 + c.x**2) * (b.x - a.x)) / d
        return Point((cx, cy))
