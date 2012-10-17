#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: spectrum.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/09/12 11:04:40

u"""
... Put description here ...
"""

from types import DictType, NoneType

class Spectrum(object):
    
    def __init__(self, spectrum_id = '', location = ('','')):
        self.id = spectrum_id
        self.x, self.y = location
        self.values = dict()
        self.description = ''
        self.attributes = dict()
        self.neighborhood = 1
    
    def set_id(self, spectrum_id):
        u"""
        Sets the id of the spectrum, usually related to the location
        where it is taken.
        """
        self.id = spectrum_id

    def set_location(self, location):
        u"""
        Sets the location of the spectrum represented by a coordinate pair.
        """
        self.x, self.y = location

    def set_neighborhood(self, neighborhood):
        u"""
        Sets the pixel neighborhood for which the spectrum is taken.
        """
        self.neighborhood = neighborhood

    def set_description(self, description):
        u"""
        Sets an arbitrary description of the spectrum.
        """
        self.description = description

    def set_source(self, source):
        u"""
        Sets the source of the spectrum, i.e. an image that is part of a larger
        series or a flight strip number.
        """
        self.source = source

    def get_value(self, band_id):
        u"""
        Retrieves a single band measurement for the specified band id.
        """
        if self.values.has_key(band_id):
            return self.values[band_id]
        else:
            return None
    
    def set_value(self, band_id, value, overwrite = False):
        u"""
        Sets a single band measurement using the specified value for the given
        band id.
        """
        if self.values.has_key(band_id) and not overwrite:
            print "Will not overwrite existing value for band_id '%s'" % str(band_id)
        else:
            self.values[band_id] = SingleBandMeasurement(self.id, band_id, value)

    def all_values(self):
        u"""
        Returns the whole spectrum using their actual values.
        """
        return [v.__get__() for v in self.values.values()]

    def set_invalid(self, band_id):
        u"""
        Declares the single band measurement of the specified band id as invalid.
        """
        self.set_value(band_id, None)

    def get_attribute(self, attribute_id):
        u"""
        Gets an attribute that has been added to the spectrum data.
        """
        if self.attributes.has_key(attribute_id):
            return self.attributes[attribute_id]

    def set_attribute(self, attribute_id, value):
        u"""
        Sets an attribute to accompany the spectrum data.
        """
        self.attributes[attribute_id] = value

    def __str__(self, include_no_data = True, include_source = True):
        u"""
        Returns a string representation of the spectrum, either with invalid
        data and/or the source image included or not.
        """
        if include_source:
            prefix = "\t".join([str(x) for x in [self.id, self.source, self.x, self.y]])
        else:
            prefix = "\t".join([str(x) for x in [self.id, self.x, self.y]])
        if include_no_data:
            return "\t".join(([prefix] + [str(v) for v in self.values.values()]))
            #return return_str + "\t".join(([str(v) for v in self.values.values()]))
        else:
            return "\t".join(([prefix] + [str(v) for v in self.values.values() if v.__get__() is not None]))
            #return return_str + "\t".join(([str(v) for v in self.values.values() if v.__get__() is not None]))

class SingleBandMeasurement(object):
    
    NO_DATA_VALUE = -0.01
    
    def __init__(self, loc_id, band_id, value):
        
        # storing location and band information
        self.loc_id = loc_id
        self.band_id = band_id
        
        # checking whether we received an invalid value
        if type(value) is NoneType:
            self.raw = None
            self.mean = None
            self.std_dev = None
            self.neighborhood = None
        # checking whether we're operating in a nxn-neighborhood (n > 1), which
        # is indicated by a value aggregation represented by a dictionary object
        elif type(value) is DictType:
            self.raw = value['raw']
            self.min = value['min']
            self.max = value['max']
            self.mean = value['mean']
            self.std_dev = value['std_dev']
            self.count = value['count']
            self.neighborhood = value['neighborhood']
        # otherwise we received a single value representing a single pixel
        else:
            self.raw = value
            self.mean = self.min = self.max = value
            self.std_dev = 0
            self.neighborhood = 1
            self.count = 1

    def __get__(self):
        if self.neighborhood is None:
            return None
        elif self.neighborhood > 1:
            return self.mean
        else:
            return self.raw

    def __str__(self):
        if self.neighborhood is None:
            return str(self.NO_DATA_VALUE)
        elif self.neighborhood > 1:
            raw = "\t".join([str(f) for f in self.raw])
            mean = str(self.mean)
            std_dev = str(self.std_dev)
            return ("\t".join((raw, mean, std_dev)))
        else:
            return (str(self.raw))
