#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/04/30 15:21:09

u"""
... Put description here ...
"""
import os
import csv
import time

from osgeo import osr

from lxml import etree, html
from lxml.builder import *

def CLASS(*args): 
    return {"class":' '.join(args)}

def create_table_row(species, coverage):
    if "." in species:
        species = species.replace(".", " ")
    tr = E.tr(E.td(species), E.td(coverage, CLASS("numeric")), E.td(""))
    return tr

if __name__ == '__main__':
    
    tpl_src = r"D:\tmp\fieldsheet_template2.html"
    tgt_dir = r"d:\tmp\veg\nordost"
    plt_src = r"D:\tmp\veg\Bayern_120112_FFH_fuer naechste Phase.csv"
    plt_src = r"d:\tmp\veg\NordOst_071211_FFHneu_fuer naechste Phase.csv"
    
    if 'nordost' in plt_src.lower():
        utm_zone = 33
    elif 'bayern' in plt_src.lower():
        utm_zone = 32
    
    if '_ffh' in plt_src.lower():
        sheet_type = 'FFH'
    elif '_hnv' in plt_src.lower():
        sheet_type = 'HNV'
    
    src_sr = osr.SpatialReference()
    src_sr.SetWellKnownGeogCS('WGS84')
    src_sr.SetUTM(utm_zone)
    
    tgt_sr = osr.SpatialReference()
    tgt_sr.SetWellKnownGeogCS('WGS84')
    
    gm_tpl = "http://maps.googleapis.com/maps/api/staticmap?center=[x],[y]&zoom=14&size=500x360&sensor=false&markers=color:green|[x],[y]"
    
    ct = osr.CoordinateTransformation(src_sr, tgt_sr)
    csv_reader = csv.DictReader(open(plt_src, 'rb'), delimiter = ";")
    
    #print csv_reader.fieldnames
    
    species = sorted(csv_reader.fieldnames[csv_reader.fieldnames.index('Humidity') + 1:])
    
    #print species
    
    for row in csv_reader:
        plot = int(row['Plot'])
        x = int(row["X_UTM%d" % utm_zone])
        y = int(row["Y_UTM%d" % utm_zone])
        plot_species = list()
        for sp in species:
            if int(row[sp]):
                plot_species.append((sp, int(row[sp])))

        htm = html.parse(tpl_src).getroot()

        title_element = htm.xpath('//title')[0]
        title_element.text = title_element.text.replace("[plot_id]", "%d (%s)" % (plot, sheet_type))

        h1_element = htm.xpath('//h1')[0]
        h1_element.text = title_element.text

        plot_id_element = htm.get_element_by_id("plot_id")
        plot_id_element.text = str(plot)
        x_element = htm.get_element_by_id("x")
        x_element.text = str(x)
        y_element = htm.get_element_by_id("y")
        y_element.text = str(y)

        img_element = htm.get_element_by_id("location_map")
        
        lat, lon, z = ct.TransformPoint(float(x), float(y))
        img_src = gm_tpl.replace("[x]", str(lon))
        img_src = img_src.replace("[y]", str(lat))
        img_element.set('src', img_src)

        species_header = htm.get_element_by_id("species_header")
        for i in range(0, 21 - len(plot_species)):
            species_header.addnext(create_table_row("", ""))
        plot_species.reverse()
        for plt_sp in plot_species:
            sp, coverage = plt_sp
            species_header.addnext(create_table_row(sp, str(coverage)))

        doc = etree.ElementTree(htm)
        tgt_name = "%d.html" % plot
        tgt_path = os.path.join(tgt_dir, tgt_name)
        print tgt_path
        doc.write(tgt_path, pretty_print = True, method = "html", encoding="utf-8")

    import sys
    sys.exit()
    