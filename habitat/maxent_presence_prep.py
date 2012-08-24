#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/07/04 10:47:47

u"""
... Put description here ...
"""

import sys

from osgeo import ogr

from shapely.geometry import Point, Polygon
from shapely.wkb import loads

from db.common import Session
from db.n2k import *

def cache_centroids(shp_src):
    cache = dict()
    
    ds = ogr.Open(shp_src)
    ly = ds.GetLayer(0)
    for ft in ly:
        geom = loads(ft.GetGeometryRef().ExportToWkb())
        map_id = ft.GetFieldAsString('id')
        cache[map_id] = geom.representative_point()
        #cache[map_id] = geom.centroid
    return cache

if __name__ == '__main__':
    
    m_src = r"D:\work\ms.monina\wp4\shp\blattschnitte\mtb_utm32.shp"
    q_src = r"D:\work\ms.monina\wp4\shp\blattschnitte\mtbq_utm32.shp"
    
    ht_src = r"D:\work\ms.monina\wp4\florkart_2012_occurrences_eunis_characteristic_species_n2k_areas_germany_all.txt"

    d_src = r"D:\work\ms.monina\wp4\shp\wp4_environmental_data_coverage.shp"
    
    # source shapes for mtb/quadrant tiles intersected with data coverage
    md_src = r"D:\work\ms.monina\wp4\work\data_coverage_mtb_intersect.shp"
    qd_src = r"D:\work\ms.monina\wp4\work\data_coverage_mtbq_intersect.shp"
    
    ht_map_ids = dict()

    # caching map ids
    for line in open(ht_src):
        tokens = line.strip().split("\t")
        if len(tokens) > 1:
            ht = tokens[0]
            ht_map_ids[ht] = list(set(tokens[1].split(", ")))
    
    # caching centroids
    m_centroids = cache_centroids(md_src)
    q_centroids = cache_centroids(qd_src)
    
    # preparing other stuff
    session = Session()
    output = list()
    wkt_output = list()

    for ht_id in sorted(ht_map_ids.keys()):
        ht_name = session.query(HabitatType).filter(HabitatType.type_id == ht_id).one().shortname
    
        print "Working on %s (%s)..." % (ht_id, ht_name)
        maxent_ht_name = " ".join((ht_id, ht_name)).lower().replace(" ", "_")

        all_map_ids = ht_map_ids[ht_id]
        # retrieving all mtb tiles where current habitat type is present
        m_ids = [map_id for map_id in all_map_ids if map_id.endswith('0')]
        # retrieving all quadrant tiles where current habitat type is present
        q_ids = [map_id for map_id in all_map_ids if not map_id.endswith('0')]
        # generalizing quadrant ids to corresponding mtb ids, i.e. 25101 -> 25100
        mq_ids = set([map_id[:-1] + '0' for map_id in q_ids])
        # calculating intersection between mtb ids and mtb/quadrant ids
        mq_intersect = [map_id for map_id in m_ids if map_id in mq_ids]

        print "\t+ Typical species present in %d map tiles overall (%d quadrant tiles, %d mtb tile(s))" % (len(all_map_ids), len(q_ids), len(m_ids))
        print "\t+ Quadrant tiles can be generalized to %d mtb tiles (%d mtb tiles present in this generalization)" % (len(mq_ids), len(mq_intersect))
        print "\t+ Expected result: rep. points for %d map tiles overall (%d quadrant tiles, %d mtb tile(s))" % (len(q_ids) + len(m_ids) - len(mq_intersect), len(q_ids), len(m_ids) - len(mq_intersect))

        m = 0
        q = 0

        for map_id in q_ids:
            if map_id in q_centroids:
                q += 1
                centroid = q_centroids[map_id]
                output.append("%s,%f,%f,%s" % (maxent_ht_name, centroid.x, centroid.y, map_id))
                wkt_output.append(str(centroid))
            else:
                print "\t# Rep. point for quadrant tile %s not in data coverage..." % map_id
        for map_id in m_ids:
            # checking whether mtb id was not already in generalized quadrant ids
            if map_id not in mq_ids:
                if map_id[:-1] in m_centroids:
                    m += 1
                    centroid = m_centroids[map_id[:-1]]
                    output.append("%s,%f,%f,%s" % (maxent_ht_name, centroid.x, centroid.y, map_id[:-1]))
                    wkt_output.append(str(centroid))
                else:
                    print "\t# Rep. point for mtb tile %s not in data coverage..." % map_id

        print "\t+ Found rep. points for %d map tiles overall (%d quadrant tiles, %d mtb tile(s))" % (m + q, q, m)
        print "===================================================================="

    open(r"d:\maxent_prep_cent.csv", 'wb').write("\n".join(output))

    #print "\n".join(wkt_output)