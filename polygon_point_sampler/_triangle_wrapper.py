#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/03/13 13:51:22

u"""
... Put description here ...
"""

import os
import tempfile

from subprocess import Popen, PIPE

from shapely.geometry import Point

class TriangleWrapper():

    SIMPLIFY_TOLERANCE = 20
    COMMAND_ARGUMENTS = '-pq0DP'
    POLY_SUFFIX = '.poly'
    NODE_SUFFIX = '.1.node'
    ELE_SUFFIX = '.1.ele'
    
    def __init__(self, triangle_bin = r"triangle\triangle.exe"):
        u"""
        Initialize a new instance of TriangleWrapper.
        """
        self.triangle_bin = '"' + triangle_bin + '"'
        self.tmp_files = list()
        self.vertex_cnt = 0

    def set_polygon(self, polygon):
        u"""
        Define the polygon to be triangulated by Triangle.
        """
        self.py = polygon
        self.basename = ''

    def create_poly_data(self):
        u"""
        Collect polygon data in a data structure according to Triangle's
        requirements. Polygon outlines and inner holes are treated the same -
        as defining segments of a planar straight line graph (PLSG). For more
        information see http://www.cs.cmu.edu/~quake/triangle.delaunay.html
        """
        self.vertices = list()
        self.segments = list()
        
        vertex_cnt = self.traverse_linear_ring(self.py.exterior)
        for inner_ring in self.py.interiors:
            vertex_cnt = self.traverse_linear_ring(inner_ring, vertex_cnt)
    
        self.vertex_cnt = vertex_cnt

    def write_poly_file(self, tgt_file = ''):
        u"""
        Write a file containing a source polygon's (or planar straight line
        graph) definition as expected by Triangle. File extension is '.poly',
        the format is described in detail at
        http://www.cs.cmu.edu/~quake/triangle.poly.html.
        """
        output = list()
    
        # building vertex header (number of vertices, number of dimensions,
        # number of attributes number of boundary markers)
        output.append("%d 2 0 0" % (self.vertex_cnt - 1))
        for cnt, x, y in self.vertices:
            # building vertex lines (vertex id, x, y, boundary marker)
            output.append("%d %f %f" % (cnt, x, y))

        # building segment header (number of segments, number of boundary
        # markers)
        output.append("%d 0" % len(self.segments))
        for i in range(len(self.segments)):
            # building segment lines (segment id, endpoint, endpoint, boundary marker)
            output.append("%d %d %d" % (i + 1, self.segments[i][0], self.segments[i][1]))

        # building hole header (number of holes)
        output.append(str(len(self.py.interiors)))
        for i in range(len(self.py.interiors)):
            # building hole lines (hole id, x, y) using a point that is
            # guaranteed to be within the hole
            inner_py_pt = Polygon(self.py.interiors[i]).representative_point()
            output.append("%d %f %f" % (i + 1, inner_py_pt.x, inner_py_pt.y))

        # creating temporary file
        tmp_fd, tmp_name = tempfile.mkstemp(prefix = 'tw_tmp_', suffix = self.POLY_SUFFIX)
        tgt = os.fdopen(tmp_fd, 'wb')
        self.basename = os.path.splitext(tmp_name)[0]
        self.tmp_files.append(self.basename)
 
        # putting all lines together
        tgt.write("\n".join(output))
        tgt.close()
        return tmp_name

    def read_node_file(self, node_src = ''):
        u"""
        Read a file containing all triangulation's nodes as created by
        Triangle. File extension is '.node', the format is described in detail
        at http://www.cs.cmu.edu/~quake/triangle.node.html.
        """
        if not node_src:
            node_src = "".join((self.basename, self.NODE_SUFFIX))
        
        # preparing list of nodes
        self.nodes = list()

        # reading lines
        lines = open(node_src).readlines()
        # retrieving node count
        node_cnt = int(lines.pop(0).split()[0])

        for line in lines:
            # skipping blank lines and comments
            if not line.strip() or line.startswith('#'):
                continue
            # splitting line
            tokens = line.split()
            # creating node point and adding it to list of nodes
            pt = Point(float(tokens[1]), float(tokens[2]))
            self.nodes.append(pt)
    
    def read_ele_file(self, ele_src = ''):
        u"""
        Read a file containing all triangulation's elements as created by
        Triangle. File extension is '.ele', the format is described in detail
        at http://www.cs.cmu.edu/~quake/triangle.ele.html.
        """
        if not ele_src:
            ele_src = "".join((self.basename, self.ELE_SUFFIX))
        
        # preparing lists of triangles and circumcenters
        self.triangles = list()
        self.circumcenters = list()

        # reading lines
        lines = open(ele_src).readlines()
        # retrieving triangle count
        triangle_cnt = int(lines.pop(0).split()[0])

        # preparing a dictionary containing all triangles ids that share a
        # node
        shared_nodes = dict()

        for line in lines:
            # skipping blank lines and comments
            if not line.strip() or line.startswith('#'):
                continue
            # splitting line
            tokens = line.split()
            # retrieving triangle id, and node indices constructing the triangle
            i, a, b, c = [int(x) for x in tokens]
            for node in (a, b, c):
                if not shared_nodes.has_key(node):
                    shared_nodes[node] = list()
            # adding node indices to shared nodes lists
            [shared_nodes[k].append(i) for k in a, b, c]
            # retrieving node coordinates
            aa = self.nodes[a - 1]
            bb = self.nodes[b - 1]
            cc = self.nodes[c - 1]
            # creating triangle
            triangle = Polygon([(p.x, p.y) for p in [aa, bb, cc]])
            self.triangles.append(triangle)
            # calculating triangles circumcenter
            circumcenter = self.calculate_single_circumcenter(triangle)
            self.circumcenters.append(circumcenter)
        else:
            # retrieving shared edges between triangles via lists of
            # shared nodes
            self.retrieve_shared_edges(shared_nodes)

    def retrieve_shared_edges(self, shared_nodes):
        u"""
        Retrieve shared triangle edges, therewith determining all triangles'
        neighboring triangles.
        """
        # dictionary of shared edges, keys are 2-tuples of triangle ids (those
        # that share a node)
        self.shared_edges = dict()
        for k in sorted(shared_nodes.iterkeys()):
            entry = shared_nodes[k]
            # creating all permutations, i.e. node-sharing triangle id pairs
            for l in range(0, len(entry)):
                for m in range(l + 1, len(entry)):
                    if not self.shared_edges.has_key((entry[l], entry[m])):
                        self.shared_edges[(entry[l], entry[m])] = 0
                    self.shared_edges[(entry[l], entry[m])] += 1
        # in the final dictionary all triangles that share 2 nodes are sharing
        # an edge and are therefore neighbors

    def calculate_single_circumcenter(self, triangle):
        u"""
        Calculate circumcenter of given triangle in cartesian coordinates
        according to formula given by: http://is.gd/ctPx80
        """
        a, b, c = [Point(triangle.exterior.coords[i]) for i in [0, 1, 2]]
        d = 2 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y))
        cx = ((a.y**2 + a.x**2) * (b.y - c.y) + (b.y**2 + b.x**2) * (c.y - a.y) + (c.y**2 + c.x**2) * (a.y - b.y)) / d
        cy = ((a.y**2 + a.x**2) * (c.x - b.x) + (b.y**2 + b.x**2) * (a.x - c.x) + (c.y**2 + c.x**2) * (b.x - a.x)) / d
        return Point((cx, cy))

    def build_triangle_cmd(self, poly_src):
        u"""
        Build a command line to be executed via Triangle.
        """
        self.cmd = " ".join((self.triangle_bin, self.COMMAND_ARGUMENTS, '"' + poly_src + '"'))
        print self.cmd

    def execute_triangle(self):
        u"""
        Execute Triangle using the previously created command line.
        """
        if not self.cmd:
            return
        # due to an apparent bug in the subprocess module, the call to Popen()
        # has to specify a pipe for stdin as well, which is closed immediately
        # afterwards (http://bit.ly/asA5qs)
        p = Popen(self.cmd, shell = False, stdout = PIPE, stderr = PIPE, stdin = PIPE)
        p.stdin.close()
        pout, perr = p.communicate()
        print pout

    def traverse_linear_ring(self, linear_ring, initial_idx = 1):
        u"""
        Traverse a linear ring (i.e. a polygon outline or holes within a poly-
        gon) to retrieve number of vertices and vertex coordinates using a
        data structure according to Triangle's requirements.
        """
        # set of unique coordinates
        unique_coordinates = set()
        # initial index is a continuous count of all the polygon's vertices
        i = initial_idx
        # traversing coordinate pairs
        for x, y in linear_ring.coords:
            if (x, y) not in unique_coordinates:
                unique_coordinates.add((x, y))
                self.vertices.append((i, x, y))
                if len(unique_coordinates) > 1:
                    self.segments.append((i - 1, i))
                i += 1
            # if coordinates are already in set, we have reached the final
            # vertex of the linear ring
            # therefore creating last segment
            else:
                self.segments.append((i - 1, initial_idx))
        # returning increased vertex count
        return i

if __name__ == '__main__':
    
    from shapely.geometry import Polygon
    py = Polygon(((0., 0.), (0., 1.), (1., 1.), (1., 0.)))

    tw = TriangleWrapper()
    tw.set_polygon(py)
    tw.create_poly_data()

    print tw.vertices
    print tw.segments

    tmp_name = tw.write_poly_file()
    print tmp_name
    tw.build_triangle_cmd(tmp_name)
    
    tw.execute_triangle()
    tw.read_node_file()
    tw.read_ele_file()
    tw.create_skeleton_line()
    tw.cleanup()