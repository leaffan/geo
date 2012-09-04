#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/07/02 12:55:22

u"""
... Put description here ...
"""

import os

from osgeo import ogr

from _utils import ogr_utils, general_utils

if __name__ == '__main__':
    
    m_src = r"D:\work\ms.monina\wp4\shp\blattschnitte\mtb_utm32.shp"
    q_src = r"D:\work\ms.monina\wp4\shp\blattschnitte\mtbq_utm32.shp"
    ht_src = r"D:\work\ms.monina\wp4\florkart_2012_occurrences_eunis_characteristic_species_n2k_areas_germany_all.txt"
    
    tgt_dir = r"D:\work\ms.monina\wp4\shp\natura2000\habitat_type_occurrences"
    tgt_dir = r"d:\tmp\msk"
    
    m_ds = ogr.Open(m_src)
    q_ds = ogr.Open(q_src)
    
    m_ly = m_ds.GetLayer(0)
    q_ly = q_ds.GetLayer(0)
    
    ht_map_ids = dict()
    
    for line in open(ht_src):
        tokens = line.strip().split("\t")
        if len(tokens) > 1:
            ht = tokens[0]
            ht_map_ids[ht] = list()
            ht_map_ids[ht] = tokens[1].split(", ")
    
    for ht in sorted(ht_map_ids.keys()):
        try:
            print "Working on habitat type %s..." % ht
            all_map_ids = set(ht_map_ids[ht])
            # retrieving all mtb ids where current habitat type is present
            m_ids = [map_id for map_id in all_map_ids if map_id.endswith('0')]
            # retrieving all quadrant ids where current habitat type is present
            q_ids = [map_id for map_id in all_map_ids if not map_id.endswith('0')]
            # calculating all mtb ids for available quadrant ids, i.e. 25101 -> 25100
            mq_ids = set([map_id[:-1] + '0' for map_id in q_ids])
            # calculating intersection between mtb ids and mtb/quadrant ids
            mq_intersect = [map_id for map_id in m_ids if map_id in mq_ids]
    
            print "\t+ Found in %d quadrants and %d mtbs (%d map tiles overall)..." % (len(q_ids), len(m_ids), len(m_ids) + len(q_ids))
    
            tgt_file = ht + ".shp"
            tgt_shp = os.path.join(tgt_dir, tgt_file)
            print "\t+ Saving feature subset to %s..." % tgt_shp
            tgt_ds, tgt_ly = ogr_utils.create_shapefile(tgt_shp, ogr.wkbPolygon, q_ly.GetSpatialRef())
            ogr_utils.create_feature_definition_from_template(q_ly, tgt_ly)
            
            if q_ids:
                for subset in general_utils.subset_list(q_ids, 1000):
                    # building where clause for retrieving subset of all quadrant features
                    q_where_clause = "SELECT * FROM %s WHERE %s IN (%s)" % (q_ly.GetName(), 'id', ", ".join(["'%s'" % map_id for map_id in subset]))
                    q_sub = q_ds.ExecuteSQL(q_where_clause)
                    for ft in q_sub:
                        tgt_ly.CreateFeature(ft)
            
            if m_ids and len(mq_intersect) != len(m_ids):
                # building where clause for retrieving subset of all mtb features
                m_where_clause = "SELECT * FROM %s WHERE %s IN (%s)" % (m_ly.GetName(), 'id', ", ".join(["'%s'" % map_id[:-1] for map_id in m_ids if map_id not in mq_ids]))
                m_sub = m_ds.ExecuteSQL(m_where_clause)
                for ft in m_sub:
                    tgt_ly.CreateFeature(ft)
    
            q_sub = None
            m_sub = None
        
        except:
            pass



