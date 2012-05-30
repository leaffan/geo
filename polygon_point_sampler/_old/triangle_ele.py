#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2011/10/12 12:43:14

u"""
... Put description here ...
"""

import sys

from shapely.geometry import Point, Polygon, LineString

def calculate_single_circumcenter(triangle):
    u"""
    Calculate circumcenter of given triangle in cartesian coordinates
    according to formula given by: http://is.gd/ctPx80
    """
    a, b, c = [Point(triangle.exterior.coords[i]) for i in [0, 1, 2]]
    d = 2 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y))
    cx = ((a.y**2 + a.x**2) * (b.y - c.y) + (b.y**2 + b.x**2) * (c.y - a.y) + (c.y**2 + c.x**2) * (a.y - b.y)) / d
    cy = ((a.y**2 + a.x**2) * (c.x - b.x) + (b.y**2 + b.x**2) * (a.x - c.x) + (c.y**2 + c.x**2) * (b.x - a.x)) / d
    return Point((cx, cy))

if __name__ == '__main__':

    ele_src = r"D:\dev\python\_misc\point_sampler\triangle\t1.1.ele"
    node_src = r"D:\dev\python\_misc\point_sampler\triangle\t1.1.node"
    

    lines = open(node_src).readlines()
    
    node_cnt = int(lines.pop(0).split()[0])
    nodes = list()
    triangles = list()
    circumcenters = list()

    for line in lines:
        if line.startswith('#'):
            continue
        tokens = line.split()
        pt = Point(float(tokens[1]), float(tokens[2]))
        nodes.append(pt)

    lines = open(ele_src).readlines()
    
    triangle_cnt = int(lines.pop(0).split()[0])
    
    print triangle_cnt
    
    shared_nodes = dict()
    shared_edges = dict()
    
    for line in lines:
        if line.startswith('#'):
            continue
        tokens = line.split()
        i, a, b, c = [int(x) for x in tokens]
        if not shared_nodes.has_key(a):
            shared_nodes[a] = list()
        if not shared_nodes.has_key(b):
            shared_nodes[b] = list()
        if not shared_nodes.has_key(c):
            shared_nodes[c] = list()
        [shared_nodes[k].append(i) for k in a, b, c]
        aa = nodes[a - 1]
        bb = nodes[b - 1]
        cc = nodes[c - 1]
        triangle = Polygon([(p.x, p.y) for p in [aa, bb, cc]])
        print triangle
        circumcenter = calculate_single_circumcenter(triangle)
        triangles.append(triangle)
        circumcenters.append(circumcenter)
    else:
        for k in sorted(shared_nodes.iterkeys()):
            entry = shared_nodes[k]
            print entry
            for l in range(0, len(entry)):
                for m in range(l + 1, len(entry)):
                    print "\t", entry[l], entry[m]
                    if not shared_edges.has_key((entry[l], entry[m])):
                        shared_edges[(entry[l], entry[m])] = 0
                    shared_edges[(entry[l], entry[m])] += 1
    
    for key in sorted(shared_edges.iterkeys()):
        if shared_edges[key] == 2:
            
            
            from_pt = circumcenters[key[0] - 1]
            to_pt = circumcenters[key[1] - 1]
            #print [circumcenters[i] for i in key[0], key[1]]
            
            ls = LineString([(cc.x, cc.y) for cc in (from_pt, to_pt)])
            print ls
    
    print
    
    for p in circumcenters:
        print p
