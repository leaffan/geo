#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/09/13 12:06:47

u"""
... Put description here ...
"""
import os
import pickle
import math
from pylab import *

import matplotlib.pyplot as plt

from _utils import numpy_utils
from spectrum import *

def get_spectrum_by_id(all_spectra, spectrum_id):
    for sp in all_spectra:
        if sp.id == spectrum_id:
            return sp
    else:
        return None

def get_spectra_by_attribute(all_spectra, attribute, value):
    found_spectra = list()
    for sp in all_spectra:
        if sp.get_attribute(attribute) == value:
            found_spectra.append(sp)
    else:
        return found_spectra

#def plot_single_spectrum(spectrum):

#def plot_spectra_pair()

if __name__ == '__main__':
    src_dir = r"Z:\spectra"
    tgt_dir = os.path.join(src_dir, "plots")

    apex_spec = r"D:\work\ms.monina\wp5\_apex_info.txt"
    hymap_spec = r"D:\work\ms.monina\wp5\_hymap_info.txt"
    re_spec = r"D:\work\ms.monina\wp5\_rapideye_info.txt"

    pkl_src = r"Z:\spectra\2009-08-06_hymap_wahner_heide_mos_first_envi_2012-11-05_115350_spectra.pkl"
    pkl_src = r"Z:\spectra\2011-09-14_apex_wahner_heide_mosaic_2012-11-06_123245_spectra.pkl"
    pkl_src = r"Z:\spectra\2011-09-14_apex_wahner_heide_mosaic_2012-11-06_123742_spectra.pkl"
    #pkl_src = r"Z:\spectra\subset_uffing_2_2012-11-05_151842_spectra.pkl"

    wl = numpy_utils.read_sensor_specs(apex_spec)[0]
    all_sp = pickle.load(open(pkl_src))

    f_s = get_spectra_by_attribute(all_sp, 'type', 'f')
    for sp in f_s:
        values = sp.all_values()
        aline, = plt.plot(wl, values, 'green')
    nf_s = get_spectra_by_attribute(all_sp, 'type', 'nf')
    for sp in nf_s:
        values = sp.all_values()
        aline, = plt.plot(wl, values, 'lime')
    else:
        #plt.xlim(x_min, x_max)
        plt.ylim(0, 0.5)
        #plt.title("Plot %d" % a1.id)
        #plt.axvline(x = 0.505, color = 'b')
        #plt.axvline(x = 0.584, color = 'g')
        #plt.axvline(x = 0.678, color = 'r')
        plt.axvline(x = 0.76, color = 'r')
        plt.axvline(x = 0.81)
        plt.axvline(x = 2.45)
        plt.axvline(x = 1.28)
        
        plt.grid(True)
        png_name = "apex_nf_vs._f_bb.png"
        plt.savefig(os.path.join(tgt_dir, png_name), dpi = 300)
        

    import sys
    sys.exit()

    
    apex_pkl_src = r"2011-09-14_apex_wahner_heide_spectra.pkl"
    hymap_pkl_src = r"Z:\tmp\spectra\2009-08-06_hymap_wahner_heide_mos_first_spectra.pkl"
    apex_pkl_src = r"2011-09-14_apex_wahner_heide_mosaic_2012-10-02_101843_spectra.pkl"
    hymap_pkl_src = r"2009-08-06_hymap_wahner_heide_mos_first_envi_2012-10-01_223931_spectra.pkl"
    
    apex_wl = numpy_utils.read_sensor_specs(apex_spec)[0]
    hymap_wl = numpy_utils.read_sensor_specs(hymap_spec)[0]
    x_min = math.floor(min(apex_wl + hymap_wl) * 10) / 10
    x_max = math.ceil(max(apex_wl + hymap_wl) * 10) / 10
    
    apex_spectra = pickle.load(open(os.path.join(src_dir, apex_pkl_src)))
    hymap_spectra = pickle.load(open(os.path.join(src_dir, hymap_pkl_src)))

    for i in range(0, len(apex_spectra))[:10]:
    
        apex = apex_spectra[i]
        hymap = get_spectrum_by_id(hymap_spectra, apex.id)
        
        if hymap is None:
            continue
        
        print "Plotting spectra for plot %d..." % apex.id
        
        avl = apex.all_values()
        hvl = hymap.all_values()
        
        y_max = 0.45
        if math.ceil(max(hvl + avl)) > y_max:
            y_max = math.ceil(max(hvl + avl) * 10) / 10
        
        aline, = plt.plot(apex_wl, avl, 'r')
        hline, = plt.plot(hymap_wl, hvl, 'g')
        
        plt.xlim(x_min, x_max)
        plt.ylim(0, plot_max)
        plt.title("Plot %d" % a1.id)
        plt.grid(True)
        
        png_name = "plot_%04d.png" % a1.id
        
        plt.savefig(os.path.join(tgt_dir, png_name), dpi = 300)
        plt.cla()

    #plt.show()