#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/04/11 15:22:05

u"""
... Put description here ...
"""
import os
from collections import OrderedDict
from operator import itemgetter

from osgeo import ogr
from _utils import ogr_utils

def build_id_lookup_table(src_shp, look_up_field):
    ds = ogr.Open(src_shp)
    ly = ds.GetLayer(0)
    
    lut = dict()
    
    for ft in ly:
        look_up_data = ft.GetFieldAsString(look_up_field)
        lut[look_up_data] = ft.GetFID()

    return lut

def build_species_lookup_table(src):
    lines = [l.strip() for l in open(src).readlines()]
    
    species_lut = dict()
    
    for line in lines:
        tokens = line.split(";")
        (species, location, symbol) = tokens[0:3]
        if not species_lut.has_key(species):
            species_lut[species] = list()
        if len(tokens) == 3:
            species_lut[species].append((location, symbol))
        elif len(tokens) > 3:
            species_lut[species].append((location, symbol) + tuple(tokens[3:]))
    
    return species_lut
    
def convert_feature(src_ft, tgt_ly, occurrence_dict):
    # retrieving current feature's geometry
    src_gm = src_ft.GetGeometryRef()
    # retrieving geometry's centroid coordinates
    occurrence_dict['x'] = src_gm.Centroid().GetX()
    occurrence_dict['y'] = src_gm.Centroid().GetY()
    # initializing new feature
    tgt_ft = ogr.Feature(tgt_ly.GetLayerDefn())
    # using the source feature's geometry
    tgt_ft.SetGeometry(src_gm)
    # setting attributes
    for key in occurrence_dict:
        tgt_ft.SetField(key, occurrence_dict[key])
    tgt_ly.CreateFeature(tgt_ft)


if __name__ == '__main__':
    
    tk25_src = r"D:\work\ms.monina\wp4\shp\blattschnitte\mtb_utm32.shp"
    quad_src = r"D:\work\ms.monina\wp4\shp\blattschnitte\mtbq_utm32.shp"
    spec_src = r"D:\work\ms.monina\wp4\florkart_2012_occurrences_habdir_annex_species_germany.txt"
    #spec_src = r"D:\work\ms.monina\wp4\florkart_2012_occurrences_eunis_characteristic_species_germany.txt"
    tgt_dir = r"D:\work\ms.monina\wp4\shp\florkart"
    #tgt_dir = r"d:\tmp"
    
    tk25_id_lut = build_id_lookup_table(tk25_src, 'id')
    quad_id_lut = build_id_lookup_table(quad_src, 'id')
    species_lut = build_species_lookup_table(spec_src)

    keys = ['Molinia caerulea']
    
    record = OrderedDict()
    record['species'] = ''
    record['tk25_id'] = ''
    record['quad_id'] = ''
    record['symbol'] = ''
    record['x'] = float(0)
    record['y'] = float(0)
    
    tk25_ds = ogr.Open(tk25_src)
    tk25_ly = tk25_ds.GetLayer(0)

    quad_ds = ogr.Open(quad_src)
    quad_ly = quad_ds.GetLayer(0)
    
    for key in species_lut:
        print "Working on '%s'..." % key
        data = species_lut[key]
        quad_ids = set()
        tk25_ids = set()
        tmp_ids = set()
        all_occ = dict()
        
        if len(data[0]) == 3:
            suffix = data[0][-1]
            record['suffix'] = ''
        else:
            suffix = ''

        tgt_file = key.lower().replace(" ", "_") + ".shp"
        tgt_shp = os.path.join(tgt_dir, tgt_file)
        tgt_ds, tgt_ly = ogr_utils.create_shapefile(tgt_shp, ogr.wkbPolygon, tk25_ly.GetSpatialRef())
        ogr_utils.create_feature_definition_from_record(record, tgt_ly)
        
        for entry in sorted(data, key = itemgetter(0), reverse = False):
            quad_location, symbol = entry[:2] 
            tk25_location = quad_location[:-1]
            quadrant = quad_location[-1]
 
            occ_dict = dict()
            occ_dict['species'] = key
            occ_dict['symbol'] = symbol
            occ_dict['quad_id'] = quad_location
            occ_dict['tk25_id'] = tk25_location
            if suffix:
                occ_dict['suffix'] = suffix
 
            if int(quadrant) != 0:
                if quad_location in quad_ids:
                    print "\tquad location '%s' already mapped..." % quad_location
                else:
                    quad_ids.add(quad_location)
                    if tk25_location in tk25_ids:
                        tk25_ids.remove(tk25_location)
                        del all_occ[tk25_location]
                    tmp_ids.add(tk25_location)
                    all_occ[quad_location] = occ_dict
                continue
            else:
                if tk25_location in tmp_ids:
                    continue
                if tk25_location in tk25_ids:
                    print "\ttk25 location '%s' already mapped..." % tk25_location
                    continue
                else:
                    tk25_ids.add(tk25_location)
                    all_occ[tk25_location] = occ_dict
        else:
            
            print "\t%d occurrences found for '%s'..." % ((len(quad_ids) + len(tk25_ids)), key)
            
            for quad_id in quad_ids:
                if quad_id in quad_id_lut:
                    ft = quad_ly.GetFeature(quad_id_lut[quad_id])
                    occ_dict = all_occ[quad_id]
                    convert_feature(ft, tgt_ly, occ_dict)
                else:
                    print "\tquad location '%s' not in lookup table..." % quad_id
            for tk25_id in tk25_ids:
                if tk25_id in tk25_id_lut:
                    ft = tk25_ly.GetFeature(tk25_id_lut[tk25_id])
                    occ_dict = all_occ[tk25_id]
                    convert_feature(ft, tgt_ly, occ_dict)
                else:
                    print "\tk25 location '%s' not in lookup table..." % tk25_id
        
            if suffix:
                tgt_ly = None
                tgt_file = key.lower().replace(" ", "_") + "_" + suffix.replace("/", "-") + ".shp"
                old_tgt_shp = tgt_shp
                new_tgt_shp = os.path.join(tgt_dir, tgt_file)
                drv = tgt_ds.GetDriver()
                new_tgt_ds = drv.CopyDataSource(tgt_ds, new_tgt_shp)
                new_tgt_ds = None
                tgt_ds = None
                drv.DeleteDataSource(old_tgt_shp)
