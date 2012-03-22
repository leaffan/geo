#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: triangle_wrapper.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/03/13 13:51:22

u"""
A wrapper allowing for the execution of Triangle, a Delaunay triangulation
program available from <http://www.cs.cmu.edu/~quake/triangle.html>.

It allows for the execution of Triangle both locally and on a remote machine.
To facilitate the latter it is necessary to use a RemoteSSHClient object.

"""
import os
import tempfile
import sys
from subprocess import Popen, PIPE

from shapely.geometry import Point, LineString, Polygon

from remote_ssh_client import RemoteSSHClient

class TriangleWrapper():
    
    # TODO: allow for the modification of the used command line options

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
        if polygon:
            self.set_polygon(polygon)
        self.tmp_files = list()
        self.vertex_cnt = 0
        self.verbose = False

    def set_polygon(self, polygon):
        u"""
        Define the polygon to be triangulated by Triangle. Polygon is a polygon
        geometry as represented by the Shapely library.
        """
        self.py = polygon
        self.basename = ''

    def toggle_verbosity(self, verbose = True, level = 1):
        u"""
        Toggle the verbosity of wrapper's output.
        """
        if verbose:
            self.verbose = True
        else:
            self.verbose = False

    def apply_triangle(self, remote = False, polygon = ''):
        u"""
        Combine all processes to apply Triangle to a specified polygon, either
        local or via a remote instance of the binary.
        """
        # setting polygon if one was specified
        if polygon:
            self.set_polygon(py)
        # preparing *.poly file for Triangle
        if self.verbose:
            print "+ Preparing and creating polygon input data for Triangle..."
        self.convert_poly_data()
        # creating *.poly file
        self.write_poly_file()
        
        # exectuting Triangle
        if self.verbose:
            print "+ Executing Triangle",
        if remote:
            if not self.remote_prepared:
                print "Remote execution is not prepared..."
                return
            print "remotely..."
            self.execute_remote_triangle(self.verbose)
        else:
            if self.verbose:
                print "locally..."
            self.execute_triangle(self.verbose)

        # reading processing results    
        if self.verbose:
            print "+ Reading Triangle output..."
        self.read_node_file()
        self.read_ele_file()
        
        # cleaning up afterwards
        if self.verbose:
            print "+ Cleaning up after us..."
        self.cleanup()

    def write_poly_file(self, tgt_file = ''):
        u"""
        Write a file containing a source polygon's (or planar straight line
        graph) definition as expected by Triangle. File extension is '.poly',
        the format is described in detail at
        http://www.cs.cmu.edu/~quake/triangle.poly.html.
        """
        # setting list of output lines
        output = list()
    
        # working on vertex definition section
        # creating vertex header (number of vertices, number of dimensions,
        # number of attributes number of boundary markers)
        output.append("%d 2 0 0" % (self.vertex_cnt - 1))
        for cnt, x, y in self.vertices:
            # creating vertex lines (vertex id, x, y, boundary marker)
            output.append("%d %f %f" % (cnt, x, y))

        # working on segment definition section
        # creating segment header (number of segments, number of boundary
        # markers)
        output.append("%d 0" % len(self.segments))
        for i in range(len(self.segments)):
            # creating segment lines (segment id, endpoint, endpoint, boundary marker)
            output.append("%d %d %d" % (i + 1, self.segments[i][0], self.segments[i][1]))

        # working on hole definition section
        # checking whether source polygon is a MultiPolygon
        if hasattr(self.py, 'geoms'):
            # creating Triangle representation of the source MultiPolygon's holes
            # creating hole header (number of holes)
            hole_cnt = 0
            for single_py in self.py:
                hole_cnt += len(single_py.interiors)
            output.append(str(hole_cnt))
            h = 0
            for single_py in self.py:
                for inner_ring in single_py.interiors:
                    # creating hole lines (hole id, x, y) using a point that is
                    # guaranteed to be within the hole
                    inner_py_pt = Polygon(inner_ring).representative_point()
                    output.append("%d %f %f" % (h + 1, inner_py_pt.x, inner_py_pt.y))
                    h += 1
        # if source polygon is a simple polygon
        else:
            # creating Triangle representation of the source polygon's holes
            # creating hole header (number of holes)
            hole_cnt = len(self.py.interiors)
            output.append(str(hole_cnt))
            for i in range(len(self.py.interiors)):
                # creating hole lines (hole id, x, y) using a point that is
                # guaranteed to be within the hole
                inner_py_pt = Polygon(self.py.interiors[i]).representative_point()
                output.append("%d %f %f" % (i + 1, inner_py_pt.x, inner_py_pt.y))

        # creating temporary file
        self.create_temp_file(output)

        # adding basename of temp file to list of temporarily created files to
        # allow for later cleanup
        self.basename = os.path.splitext(self.poly_src)[0]
        self.tmp_files.append(self.basename)
 
        return self.poly_src

    def execute_remote_triangle(self, verbose = False):
        u"""
        Executing Triangle on a remote machine. This is for platforms that
        doesn't allow for compilation of Triangle, i.e. MacOS X.
        """
        # setting up remote ssh client
        rsc = RemoteSSHClient(ssh_cfg_file)
        # uploading source file
        if verbose:
            print "+ Uploading Triangle input data to remote location..."
        self.remote_poly_src = rsc.upload_file(self.poly_src, self.remote_data_dir)
        if verbose:
            print "+ Uploaded input data to '%s'..." % self.remote_poly_src
        
        # building remote command line
        self.build_triangle_cmd(remote = True)

        # executing remote command line
        cc, so, se = rsc.execute_commands(self.cmd)
        if verbose:
            #print "+ Remotely executed command(s): \n\t%s" % cc
            print "+ Triangle standard output:\n%s" % "\t" + "".join(["\t%s" % s for s in so]).strip()
        if se:
            print "+ Triangle error output:\n%s" % "".join(["\t%s" % s for s in se]).strip()
            try:
                self.cleanup()
            except:
                pass
            sys.exit()
        
        # downloading results
        if self.verbose:
            print "+ Downloading results..."
        rsc.download_file(os.path.splitext(self.remote_poly_src)[0] + ".1.node", os.path.splitext(self.poly_src)[0] + ".1.node")
        rsc.download_file(os.path.splitext(self.remote_poly_src)[0] + ".1.ele", os.path.splitext(self.poly_src)[0] + ".1.ele")

        if self.verbose:
            print "+ Cleaning up remotely..."
        # creating and executing command tp remove temporarily created files
        rm_cmds = ["rm %s" % (os.path.splitext(self.remote_poly_src)[0] + ".*")]
        rsc.execute_commands(rm_cmds)

    def execute_triangle(self, verbose = False):
        u"""
        Execute Triangle using the previously created command line.
        """
        if not self.poly_src:
            return
        self.build_triangle_cmd()
        # due to an apparent bug in the subprocess module, the call to Popen()
        # has to specify a pipe for stdin as well, which is closed immediately
        # afterwards (http://bit.ly/asA5qs)
        p = Popen(self.cmd, shell = False, stdout = PIPE, stderr = PIPE, stdin = PIPE)
        p.stdin.close()
        pout, perr = p.communicate()
        if verbose:
            print pout

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
        
        # preparing list of triangles
        self.triangles = list()

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
        else:
            # retrieving shared edges between triangles via lists of
            # shared nodes
            self.retrieve_shared_edges(shared_nodes)

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
        # coounting vertices of a simple polygon's outline
        else:
            vertex_cnt = self.traverse_linear_ring(self.py.exterior)
        # counting vertices of all the multipolygon's holes adding the result to
        # the previously retrievd vertex count
        if hasattr(self.py, 'geoms'):
            for single_py in self.py:
                for inner_ring in single_py.interiors:
                    vertex_cnt = self.traverse_linear_ring(inner_ring, vertex_cnt)
        # counting vertices of all a simple polygon's holes adding the result to
        # the previously retrievd vertex count
        else:
            for inner_ring in self.py.interiors:
                vertex_cnt = self.traverse_linear_ring(inner_ring, vertex_cnt)
    
        self.vertex_cnt = vertex_cnt

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

    def create_temp_file(self, content):
        u"""
        Create a temporary file and writing the specified content to it.
        """
        tmp_fd, tmp_name = tempfile.mkstemp(prefix = 'tw_', suffix = self.POLY_SUFFIX)
        tgt = os.fdopen(tmp_fd, 'wb')
        # joining all created lines and writing the result to a file
        tgt.write("\n".join(content))
        tgt.close()

        # setting temporarily created file as polygon geometry source file
        self.poly_src = tmp_name

    def prepare_remote_execution(self, ssh_cfg_file, remote_data_dir = ''):
        u"""
        Prepare remote execution of Triangle by identifying a configuration file
        containing SSH connection information and an optional data directory
        that will contain the Triangle input and output data.
        """
        self.remote_prepared = False
        if not remote_data_dir:
            self.remote_data_dir = "/".join((self.TRIANGLE_BIN_DIR, 'data'))
        else:
            self.remote_data_dir = remote_data_dir
        if os.path.isfile(ssh_cfg_file):
            self.ssh_cfg_file = ssh_cfg_file
            self.remote_prepared = True
        else:
            print "Couldn't find SSH configuration file '%s'..." % ssh_cfg_file

    def build_triangle_cmd(self, remote = False):
        u"""
        Build a command line to be executed via Triangle.
        """
        if remote:
            self.triangle_bin = '"' + './' + "/".join((self.TRIANGLE_BIN_DIR, self.TRIANGLE_BIN)) + '"'
            self.cmd = " ".join((self.triangle_bin, self.COMMAND_ARGUMENTS, '"' + self.remote_poly_src + '"'))
        else:
            self.triangle_bin = '"' + os.path.join(self.TRIANGLE_BIN_DIR, self.TRIANGLE_BIN) + '"'
            self.cmd = " ".join((self.triangle_bin, self.COMMAND_ARGUMENTS, '"' + self.poly_src + '"'))
        if self.verbose:
            print "+ Triangle command line:\n\t", self.cmd

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

    def cleanup(self):
        u"""
        Clean up, i.e. remove temporarily created files.
        """
        for tmp_name in self.tmp_files:
            if self.verbose:
                print "+ Deleting temporarily created files:"
            for suffix in (self.POLY_SUFFIX, self.NODE_SUFFIX, self.ELE_SUFFIX):
                tmp_file = "".join((tmp_name, suffix))
                if os.path.isfile(tmp_file):
                    if self.verbose:
                        print "\t%s" % tmp_file
                    os.unlink(tmp_file)

if __name__ == '__main__':
    from shapely.geometry import Polygon
    from shapely.wkt import loads

    ssh_cfg_file = r"d:\tmp\_test.cfg"
    wkt_src = r"D:\work\_misc\triangulation_sampling\wkt\mp.txt"
    py = loads(open(wkt_src).read())

    tw = TriangleWrapper()
    tw.toggle_verbosity()
    tw.set_polygon(py)
    tw.prepare_remote_execution(ssh_cfg_file)
    tw.apply_triangle(True)
