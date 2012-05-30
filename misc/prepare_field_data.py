#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/04/24 11:26:01

u"""
... Put description here ...
"""

import os
import re

from operator import itemgetter

import sys
sys.path.append(r"D:\dev\python\geo\habitat")
from habitat import SpeciesFinder

def read_coordinates(coord_src):
    coords = dict()
    
    for line in [l.strip() for l in open(coord_src).readlines()]:
        plot_id, x, y = [int(token) for token in line.split("\t")]
        coords[plot_id] = (x, y)
    else:
        return coords

if __name__ == '__main__':
    
    coord_src_2009 = r"D:\work\ms.monina\wp5\wahner_heide\field\_final\koordinaten_doku_2009.txt"
    coord_src_uh_2011 = r"D:\work\ms.monina\wp5\wahner_heide\field\_final\koordinaten_ulli_2011.txt"
    coord_src_df_2011 = r"D:\work\ms.monina\wp5\wahner_heide\field\_final\koordinaten_dirk_2011.txt"

    uh_src = r"D:\work\ms.monina\wp5\wahner_heide\field\_final\Uli_combined.txt"
    df_src = r"D:\work\ms.monina\wp5\wahner_heide\field\_final\Dirk_combined.txt"

    translate_dict = dict()
    translate_dict['Vegetationshoehe'] = 'height'
    translate_dict['Hoehe'] = 'height'
    translate_dict['Moose'] = 'mosses'
    translate_dict['Flechten'] = 'lichen'
    translate_dict['Pilze'] = 'fungi'
    translate_dict['offenerBoden'] = 'open_soil'
    translate_dict['Boden'] = 'open_soil'
    translate_dict['Litter'] = 'litter'
    translate_dict['abgestorben'] = 'litter'
    translate_dict['Lebermoose'] = 'liverworts'

    tgt_dir = r"d:\tmp\veg"

    uh_plot_regex = "(20\d+)u(\d+)"
    df_plot_regex = "X(20\d+)D(\d+)SE"
    uh_sp_regex = "([A-Z]\w+)([A-Z]\w+\-?(\w+)?)"
    df_sp_regex = "([A-Z]\w+\-?\w+)"

    coords_2009 = read_coordinates(coord_src_2009)
    coords_uh = read_coordinates(coord_src_uh_2011)
    coords_df = read_coordinates(coord_src_df_2011)
    
    uh_lines = [l.strip() for l in open(uh_src).readlines()]
    df_lines = [l.strip() for l in open(df_src).readlines()]

    # popping header lines
    uh_header = uh_lines.pop(0)
    df_header = df_lines.pop(0)
    
    uh_tokens = uh_header.split("\t")
    new_uh_tokens = list()
    new_uh_tokens.append('plot')
    new_uh_tokens.append('x')
    new_uh_tokens.append('y')
    
    uh_to_df_species = dict()
    
    for token in uh_tokens:
        if translate_dict.has_key(token):
            new_uh_tokens.append(translate_dict[token])
        else:
            match = re.search(uh_sp_regex, token)
            if not match:
                print "Couldn't match species name... %s" % token
            else:
                new_uh_token = "%s_%s" % (match.group(1), match.group(2).lower())
                key = new_uh_token.replace("_", "")
                uh_to_df_species[key] = new_uh_token
                new_uh_tokens.append(new_uh_token)
    
    df_tokens = df_header.split("\t")
    new_df_tokens = list()
    new_df_tokens.append('plot')
    new_df_tokens.append('x')
    new_df_tokens.append('y')
    
    for token in df_tokens:
        if translate_dict.has_key(token):
            new_df_tokens.append(translate_dict[token])
        else:
            match = re.search(df_sp_regex, token)
            if not match:
                print "Couldn't match species name... %s" % token
            else:
                if uh_to_df_species.has_key(token):
                    new_df_token = uh_to_df_species[token]
                else:
                    spf = SpeciesFinder()
                    spf.set_search_name(token)
                    sr = spf.search_on_eunis()
                    (sp_name, sp_type, sp_url), ratio = spf.find_best_match(sr)
                    found = sp_name
                    if token == found.replace(" ", ""):
                        new_df_token = found.replace(" ", "_")
                    else:
                        print "Couldn't find new species name for '%s'... Please re-check!" % token
                        new_df_token = token
            new_df_tokens.append(new_df_token)
    
    uh = dict()
    uh[2009] = list()
    uh[2011] = list()
    
    df = dict()
    df[2009] = list()
    df[2011] = list()
    
    for line in uh_lines[:]:
        tokens = line.split("\t")
        match = re.search(uh_plot_regex, tokens[0])
        if match:
            year, plot_id = [int(m) for m in match.group(1, 2)]
        else:
            print "Regular expression didn't match..."
        #print "Working on plot_id '%d' for year '%d'" % (plot_id, year)
        if year == 2009:
            if coords_2009.has_key(plot_id):
                x, y = coords_2009[plot_id]
            else:
                print "Couldn't find coordinates..."
        elif year == 2011:
            if coords_uh.has_key(plot_id):
                x, y = coords_uh[plot_id]
            else:
                print "Couldn't find coordinates..."
        uh[year].append((plot_id, x, y, tokens[1:]))
    else:
        for year in uh:
            data = uh[year]
            data = sorted(data, key = itemgetter(0))
            data = ["\t".join((str(plot_id), str(x), str(y), "\t".join(rest))) for plot_id, x, y, rest in data]
            data.insert(0, "\t".join(new_uh_tokens))

            out_name = "wh_veg_final_uh_%d.txt" % year
            out_path = os.path.join(tgt_dir, out_name)
            open(out_path, 'wb').write("\n".join(data))

    for line in df_lines[:]:
        tokens = line.split("\t")
        match = re.search(df_plot_regex, tokens[0])
        if match:
            year, plot_id = [int(m) for m in match.group(1, 2)]
        else:
            print "Regular expression didn't match..."
        #print "Working on plot_id '%d' for year '%d'" % (plot_id, year)
        if year == 2009:
            if coords_2009.has_key(plot_id):
                x, y = coords_2009[plot_id]
            elif coords_df.has_key(plot_id):
                x, y = coords_df[plot_id]
            else:
                print "Couldn't find 2009 coordinates for plot id '%d'..." % plot_id
        elif year == 2011:
            if coords_df.has_key(plot_id):
                x, y = coords_df[plot_id]
            elif coords_2009.has_key(plot_id):
                x, y = coords_2009[plot_id]
            else:
                print "Couldn't find coordinates for plot id '%d'..." % plot_id
        df[year].append((plot_id, x, y, tokens[1:]))
    else:
        for year in df:
            data = df[year]
            data = sorted(data, key = itemgetter(0))
            data = ["\t".join((str(plot_id), str(x), str(y), "\t".join(rest))) for plot_id, x, y, rest in data]
            data.insert(0, "\t".join(new_df_tokens))

            out_name = "wh_veg_final_df_%d.txt" % year
            out_path = os.path.join(tgt_dir, out_name)
            open(out_path, 'wb').write("\n".join(data))
