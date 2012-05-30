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
    tr = E.tr(E.td(species), E.td(""), E.td(coverage, CLASS("numeric")))
    return tr

def set_element_text(doc, element_id, data_dict, data_key, raw = False):
    element = doc.get_element_by_id(element_id)
    if raw:
        element.text = str(data_key)
    else:
        element.text = str(data_dict[data_key])

if __name__ == '__main__':
    
    tpl_src = r"d:\work\veggeo\msave\2012_fieldsheet_update\2012_fieldsheet_template.html"
    tgt_dir = r"d:\work\veggeo\msave\2012_fieldsheet_update\fieldsheets"
    #tgt_dir = r"/Users/markus/_tmp/bayern"
    plt_src = r"d:\work\veggeo\msave\2012_fieldsheet_update\data\Bayern_120112_FFH_fuer naechste Phase.csv"
    plt_src = r"d:\work\veggeo\msave\2012_fieldsheet_update\data\NordOst_071211_FFHneu_fuer naechste Phase.csv"
    plt_src = r"d:\work\veggeo\msave\2012_fieldsheet_update\data\NordOst_071211_HNV_fuer naechste Phase.csv"
    plt_src = r"d:\work\veggeo\msave\2012_fieldsheet_update\data\Bayern_120112_HNV_fuer naechste Phase.csv"
    #plt_src = r"/Users/markus/_work/veggeo/msave/NordOst_071211_FFHneu_fuer naechste Phase.csv"
    #plt_src = r"/Users/markus/_work/veggeo/msave/Bayern_120112_FFH_fuer naechste Phase.csv"
    #plt_src = r"/Users/markus/_work/veggeo/msave/NordOst_071211_HNV_fuer naechste Phase.csv"
    #plt_src = r"/Users/markus/_work/veggeo/msave/Bayern_120112_HNV_fuer naechste Phase.csv"
    
    MAX_NUMBER_SPECIES_ROWS = 16
    
    if 'nordost' in plt_src.lower():
        utm_zone = 33
        region = "Nordost"
    elif 'bayern' in plt_src.lower():
        utm_zone = 32
        region = "Bayern"
    
    tgt_dir = os.path.join(tgt_dir, region.lower())
    
    if '_ffh' in plt_src.lower():
        sheet_type = 'FFH'
    elif '_hnv' in plt_src.lower():
        sheet_type = 'HNV'
    
    if not os.path.isdir(tgt_dir):
        os.makedirs(tgt_dir)
    
    src_sr = osr.SpatialReference()
    src_sr.SetWellKnownGeogCS('WGS84')
    src_sr.SetUTM(utm_zone)
    
    tgt_sr = osr.SpatialReference()
    tgt_sr.SetWellKnownGeogCS('WGS84')
    
    gm_tpl = "http://maps.googleapis.com/maps/api/staticmap?center=[x],[y]&zoom=13&size=310x150&sensor=false&markers=color:green|[x],[y]"
    
    ct = osr.CoordinateTransformation(src_sr, tgt_sr)
    csv_reader = csv.DictReader(open(plt_src, 'rb'), delimiter = ";")
    
    species = sorted(csv_reader.fieldnames[csv_reader.fieldnames.index('Humidity') + 1:])
    
    record_count = 0
    
    for row in csv_reader:
        # retrieving plot id and x and y coordinates
        plot = int(row['Plot'])
        x = int(row["X_UTM%d" % utm_zone])
        y = int(row["Y_UTM%d" % utm_zone])

        # incrementing record count
        record_count += 1

        # creating plot-specific list of dominant species
        plot_species = list()
        for sp in species:
            if int(row[sp]):
                plot_species.append((sp, int(row[sp])))

        # parsing html contents of template page
        htm = html.parse(tpl_src).getroot()

        # changing contents of template page
        # setting page title and main heading
        title_element = htm.xpath('//title')[0]
        title_element.text = title_element.text.replace("Plot [plot_id]", "%s - Plot %d (%s)" % (region, plot, sheet_type))
        h1_element = htm.xpath('//h1')[0]
        h1_element.text = title_element.text

        # setting stativ Google map
        img_element = htm.get_element_by_id("location_map")
        lat, lon, z = ct.TransformPoint(float(x), float(y))
        img_src = gm_tpl.replace("[x]", str(lon))
        img_src = img_src.replace("[y]", str(lat))
        img_element.set('src', img_src)

        # setting text contents of several elements
        set_element_text(htm, 'plot_id', row, str(plot), True)
        set_element_text(htm, 'x', row, str(x), True)
        set_element_text(htm, 'y', row, str(y), True)
        set_element_text(htm, 'shrub_layer_fraction', row, 'Shrub(%)')
        set_element_text(htm, 'sheet_type', row, "%s type:" % sheet_type, True)
        set_element_text(htm, 'shrub_layer_height', row, 'Shrub(cm)')
        set_element_text(htm, 'grass_layer_fraction', row, 'Tallgrass(%)')
        set_element_text(htm, 'grass_layer_height', row, 'Tallgrass(cm)')
        set_element_text(htm, 'soil_fraction', row, 'Soil(%)')
        set_element_text(htm, 'water_fraction', row, 'Water(%)')
        set_element_text(htm, 'litter_fraction', row, 'Litter(%)')
        set_element_text(htm, 'cryptogam_fraction', row, 'Kryptogamen(%)')

        # setting dominant species
        species_header = htm.get_element_by_id("species_header")
        # creating some empty table rows
        for i in range(0, 20):
            species_header.addnext(create_table_row("", ""))
        plot_species.reverse()
        # creating table rows with previous data
        for plt_sp in plot_species:
            sp, coverage = plt_sp
            species_header.addnext(create_table_row(sp, str(coverage)))

        # creating new html document
        doc = etree.ElementTree(htm)
        if record_count >= 100:
            tgt_name = "%s_%s_%03d.html" % (region.lower(), sheet_type.lower(), plot)
        else:
            tgt_name = "%s_%s_%02d.html" % (region.lower(), sheet_type.lower(), plot)
        tgt_path = os.path.join(tgt_dir, tgt_name)
        print tgt_path
        doc.write(tgt_path, pretty_print = True, method = "html", encoding="utf-8")
