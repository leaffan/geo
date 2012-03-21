#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: triangle_wrapper.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/03/13 13:51:22

u"""
A wrapper allowing for the execution of Triangle, a Delaunay triangulation
program available from <http://www.cs.cmu.edu/~quake/triangle.html>.

"""
import os
import tempfile

from subprocess import Popen, PIPE

from shapely.geometry import Point, LineString, Polygon
from shapely.ops import linemerge

from remote_ssh_client import RemoteSSHClient

class TriangleWrapper():

    SIMPLIFY_TOLERANCE = 20
    COMMAND_ARGUMENTS = '-pq0DP'
    POLY_SUFFIX = '.poly'
    NODE_SUFFIX = '.1.node'
    ELE_SUFFIX = '.1.ele'
    TRIANGLE_BIN = 'triangle'
    TRIANGLE_BIN_DIR = '_triangle'
    
    def __init__(self, polygon = ''):
        u"""
        Initialize a new instance of TriangleWrapper.
        """
        #self.triangle_bin = '"' + local_triangle_bin + '"'
        if polygon:
            self.set_polygon(polygon)
        self.tmp_files = list()
        self.vertex_cnt = 0

    def set_polygon(self, polygon):
        u"""
        Define the polygon to be triangulated by Triangle. Polygon is a polygon
        geometry as represented by the Shapely library.
        """
        self.py = polygon
        self.basename = ''

    def convert_poly_data(self):
        u"""
        Collect polygon data in a data structure according to Triangle's
        requirements. Polygon outlines and inner holes are treated the same -
        as defining segments of a planar straight line graph (PLSG). For more
        information see http://www.cs.cmu.edu/~quake/triangle.delaunay.html
        """
        self.vertices = list()
        self.segments = list()
        
        # counting vertices of all the multipolygon's outlines
        if hasattr(self.py, 'geoms'):
            vertex_cnt = 1
            for single_py in self.py:
                vertex_cnt = self.traverse_linear_ring(single_py.exterior, vertex_cnt)
        # coounting vertices of a polygon's outline
        else:
            vertex_cnt = self.traverse_linear_ring(self.py.exterior)
        # counting vertives of all the multipolygon's holes
        # using previous vertex count as starting point
        if hasattr(self.py, 'geoms'):
            for single_py in self.py:
                for inner_ring in single_py.interiors:
                    vertex_cnt = self.traverse_linear_ring(inner_ring, vertex_cnt)
        # counting vertiex of all the source polygon's holes
        # using previous vertex counts as starting point
        else:
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
    
        # creating vertex header (number of vertices, number of dimensions,
        # number of attributes number of boundary markers)
        output.append("%d 2 0 0" % (self.vertex_cnt - 1))
        for cnt, x, y in self.vertices:
            # creating vertex lines (vertex id, x, y, boundary marker)
            output.append("%d %f %f" % (cnt, x, y))

        # creating segment header (number of segments, number of boundary
        # markers)
        output.append("%d 0" % len(self.segments))
        for i in range(len(self.segments)):
            # creating segment lines (segment id, endpoint, endpoint, boundary marker)
            output.append("%d %d %d" % (i + 1, self.segments[i][0], self.segments[i][1]))

        # creating hole header (number of holes)
        if hasattr(self.py, 'geoms'):
            hole_cnt = 0
            for single_py in self.py:
                hole_cnt += len(single_py.interiors)
            output.append(str(hole_cnt))
            h = 0
            for single_py in self.py:
                for inner_ring in single_py.interiors:
                    inner_py_pt = Polygon(inner_ring).representative_point()
                    print inner_py_pt
                    output.append("%d %f %f" % (h + 1, inner_py_pt.x, inner_py_pt.y))
                    h += 1
        else:
            hole_cnt = len(self.py.interiors)
            output.append(str(hole_cnt))
            for i in range(len(self.py.interiors)):
                # creating hole lines (hole id, x, y) using a point that is
                # guaranteed to be within the hole
                inner_py_pt = Polygon(self.py.interiors[i]).representative_point()
                output.append("%d %f %f" % (i + 1, inner_py_pt.x, inner_py_pt.y))

        # creating temporary file
        tmp_fd, tmp_name = tempfile.mkstemp(prefix = 'tw_', suffix = self.POLY_SUFFIX)
        tgt = os.fdopen(tmp_fd, 'wb')
        # adding basename to list of temporarily created files to allow for
        # later cleanup
        self.basename = os.path.splitext(tmp_name)[0]
        self.tmp_files.append(self.basename)
 
        # joining all created lines and writing the result to a file
        tgt.write("\n".join(output))
        tgt.close()
        self.poly_src = tmp_name
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

        # reading lines from *.ele file
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
            # setting up corresponding entry in shared node dictionary
            for node in (a, b, c):
                if not shared_nodes.has_key(node):
                    shared_nodes[node] = list()
            # adding triangle index for each node to lists of shared nodes
            [shared_nodes[k].append(i) for k in a, b, c]
            # retrieving node coordinates
            # NB: pay attention NOT to use the -z command line switch that alters
            # Triangle's way of enumerating elements starting with zero
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

    def create_skeleton_line(self, simplify = True):
        u"""
        Create a skeleton line of the polygon by using the circumcenters of the
        triangles created by the Conforming Delaunay Triangulation applied by
        Triangle
        Optionally simplify (by default) the skeleton by using an algorithm
        provided by Shapely.
        """
        # list of skeleton segments
        skel_segments = list()
        for key in sorted(self.shared_edges.iterkeys()):
            if self.shared_edges[key] != 2:
                continue
            # retrieve endpoints of the skeleton segment
            from_pt = self.circumcenters[key[0] - 1]
            to_pt = self.circumcenters[key[1] - 1]
            # creating skeleton segment
            skel_segment = LineString([(cc.x, cc.y) for cc in (from_pt, to_pt)])
            skel_segments.append(skel_segment)
        else:
            # merging all skeleton segments to a single (possibly multiline)
            # object
            skel_line = linemerge(skel_segments)

        # simplifying skeleton line
        if simplify:
            skel_line = skel_line.simplify(self.SIMPLIFY_TOLERANCE, False)
        
        return skel_line

    def retrieve_shared_edges(self, shared_nodes):
        u"""
        Retrieve shared triangle edges, therewith determining all triangles'
        neighboring triangles (not including those that just touch each other
        in a single node).
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

    def build_triangle_cmd(self, poly_src, remote = False):
        u"""
        Build a command line to be executed via Triangle.
        """
        if remote:
            self.triangle_bin = '"' + './' + "/".join((self.TRIANGLE_BIN_DIR, self.TRIANGLE_BIN)) + '"'
            self.cmd = " ".join((self.triangle_bin, self.COMMAND_ARGUMENTS, '"' + poly_src + '"'))
        else:
            self.triangle_bin = '"' + os.path.join(self.TRIANGLE_BIN_DIR, self.TRIANGLE_BIN) + '"'
            self.cmd = " ".join((self.triangle_bin, self.COMMAND_ARGUMENTS, '"' + poly_src + '"'))
        print self.cmd

    def execute_remote_triangle(self, ssh_cfg_file, remote_triangle_dir = '_triangle', remote_data_dir = '', remote_triangle_bin = '', verbose = False):
        u"""
        Executing Triangle on a remote machine. This is for platforms that
        doesn't allow for compilation of Triangle, i.e. MacOS X.
        """
        # defining remote data directory
        if not remote_data_dir:
            remote_data_dir = "/".join((remote_triangle_dir, 'data'))
        if not remote_triangle_bin:
            remote_triangle_bin = self.triangle_bin
        
        # setting up remote ssh client
        rsc = RemoteSSHClient(ssh_cfg_file)
        # uploading source file
        self.remote_poly_src = rsc.upload_file(self.poly_src, remote_data_dir)
        
        # building remote command line
        #self.build_triangle_cmd(True)
        
        cmd = " ".join(("./_triangle/triangle", self.COMMAND_ARGUMENTS, '"' + self.remote_poly_src + '"'))
        
        # executing remote command line
        cc, so, se = rsc.execute_commands(cmd)
        if verbose:
            print "Remotely executed command(s): \n\t%s" % cc
            print "Standard output:\n%s" % "".join(["\t%s" % s for s in so])
        if se:
            print "Standard error:\n%s" % "".join(["\t%s" % s for s in se])
        
        # downloading results
        rsc.download_file(os.path.splitext(self.remote_poly_src)[0] + ".1.node", os.path.splitext(self.poly_src)[0] + ".1.node")
        rsc.download_file(os.path.splitext(self.remote_poly_src)[0] + ".1.ele", os.path.splitext(self.poly_src)[0] + ".1.ele")

        # creating and executing command tp remove temporarily created files
        rm_cmds = ["rm %s" % (os.path.splitext(self.remote_poly_src)[0] + ".*")]
        rsc.execute_commands(rm_cmds)

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

    def cleanup(self):
        u"""
        Clean up, i.e. remove temporarily created files.
        """
        for tmp_name in self.tmp_files:
            for suffix in (self.POLY_SUFFIX, self.NODE_SUFFIX, self.ELE_SUFFIX):
                tmp_file = "".join((tmp_name, suffix))
                if os.path.isfile(tmp_file):
                    print "found and deleted: %s" % tmp_file
                    os.unlink(tmp_file)

if __name__ == '__main__':
    import matplotlib.pyplot as pp
    from shapely.geometry import Polygon
    from shapely.wkt import loads

    ssh_cfg_file = r"d:\tmp\_test.cfg"

    py = Polygon(((0., 0.), (0., 1.), (1., 1.), (1., 0.)))
    py = Polygon(((0.92, 4.5), (5.82, 4.78), (5.64, 2.3), (3.32, 0.58), (3.02, 3.22), (4, 4)))
    wkt_src = r"D:\work\_misc\triangulation_sampling\wkt\mp.txt"
    py = loads(open(wkt_src).read())

    tw = TriangleWrapper()
    tw.set_polygon(py)
    tw.convert_poly_data()

    print tw.vertices
    print tw.segments

    tmp_name = tw.write_poly_file()
    print tmp_name
    tw.build_triangle_cmd(tmp_name)
    
    #import sys
    #sys.exit()
    
    tw.execute_triangle()
    #tw.execute_remote_triangle(ssh_cfg_file, verbose = True)

    tw.read_node_file()
    tw.read_ele_file()
    
    xlist = list()
    ylist = list()
    
    j = 0
    
    print len(tw.triangles)

    for t in tw.triangles:
        print t
    
    #for t in tw.triangles[:]:
    #    a, b, c = [Point(t.exterior.coords[i]) for i in [0, 1, 2]]
    #    pp.fill([a.x, b.x, c.x], [a.y, b.y, c.y], facecolor = 'g', alpha = 0.4, edgecolor = 'red')
    #    pp.text(t.representative_point().x, t.representative_point().y, str(j + 1))
    #    j += 1
    #else:
    #    pp.show()

    #    j += 1
    #    print "xxx"
    #    xlist.extend([a.x, b.x, c.x])
    #    xlist.append(None)
    #    ylist.extend([a.y, b.y, c.y])
    #    ylist.append(None)
    #
    #print "%d triangles..." % j
    #print xlist
    #pp.fill(xlist, ylist, facecolor = 'none', alpha = 0.4, edgecolor = 'red')
    #pp.show()
    
    
    #tw.create_skeleton_line()
    #tw.cleanup()