#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2011/10/11 11:30:34

u"""
... Put description here ...
"""

if __name__ == '__main__':
    
    import sys
    import pickle
    from shapely.wkt import load, loads
    from shapely.geometry import LineString, Polygon
    from shapely.geometry.polygon import LinearRing

    sys.path.append(r"D:\dev\python\_misc\ffh")
    from habitat import Habitat, HabitatType, SubHabitat
    pkl_src = r"D:\dev\python\_misc\ffh\ffh_areas.pkl"

    ffh_areas = pickle.load(open(pkl_src))
    area = ffh_areas.itervalues().next()

    for sh in area.sub_habitats[1:2]:
    #sh = area.sub_habitats[0]
        py = loads(sh.outline)

    
    
    vertex_lines = list()
    segments = list()

    i = 1
    iv = i
    unique_cps = set()
    
    for cp in py.exterior.coords:
        #print i, cp[0], cp[1], 1
        if cp not in unique_cps:
            unique_cps.add(cp)
            vertex_lines.append("%d %f %f %d" % (i, cp[0], cp[1], 1))
            if len(unique_cps) > 1:
                segments.append((i - 1, i))
            i += 1
        else:
            segments.append((i - 1, iv))
    
    print
    
    for int_ring in py.interiors:
        iv = i
        unique_cps = set()
        for cp in int_ring.coords:
            if cp not in unique_cps:
                unique_cps.add(cp)
                vertex_lines.append("%d %f %f %d" % (i, cp[0], cp[1], 1))
                if len(unique_cps) > 1:
                    segments.append((i - 1, i))
                i += 1
            else:
                segments.append((i - 1, iv))
        print
    
    vertex_lines.insert(0, "%d 2 0 1" % (i - 1))
    
    
    print "\n".join(vertex_lines)

    print len(segments), 1
    for i in range(len(segments)):
        print i + 1, segments[i][0], segments[i][1], 1

    print len(py.interiors)
    
    for i in range(len(py.interiors)):
        inner_py_pt = Polygon(py.interiors[i]).representative_point()
        print i + 1, inner_py_pt.x, inner_py_pt.y

    
    sys.exit()
    
    
    print vertex_cnt, 1

    for i in range(vertex_cnt):
        j = i + 2
        if j > vertex_cnt:
            j = 1
        print i + 1, i + 1, j, 1

    print

    #outline = LinearRing(py.exterior.coords)
    #print outline
    #
    #for l in outline.coords:
    #    print l
    #
    #for i in range(1, vertex_cnt):
    #    ls = LineString([])
    #    print 1,
    
        
    